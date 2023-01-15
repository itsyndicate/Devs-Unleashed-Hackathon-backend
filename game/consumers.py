import asyncio
import json

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q

from core.models import FightChallenge, FightStatus
from game.game_logic.actions_mapping import map_action
from game.game_logic.fight import Fight
from game.game_logic.fight_creator import create_fight_from_fight_challenge


async def get_fight_by_account_id(account_id: str) -> FightChallenge:
    queryset = FightChallenge.objects.filter(Q(opponent__player__account_id=account_id)
                                             | Q(initiator__player__account_id=account_id), status=FightStatus.PENDING)
    if not await queryset.aexists():
        raise FightChallenge.DoesNotExist
    if await queryset.acount() > 1:
        raise FightChallenge.MultipleObjectsReturned
    return await queryset.afirst()


@database_sync_to_async
def finish_fight(fight: FightChallenge, winner_id: str):
    fight.refresh_from_db()
    fight.status = FightStatus.COMPLETED
    if winner_id:
        fight.winner_id = winner_id
    else:
        fight.draw = True
    fight.save()


def ensure_json_contains(data: dict, *args) -> bool:
    for arg in args:
        if arg not in data:
            return False
    return True


fight_storage: dict[str, Fight] = {}


# TODO: Refactor this class
class FightConsumer(AsyncWebsocketConsumer):
    account_id: str
    fight: FightChallenge
    fight_group_name: str
    _fight_object: Fight | None = None

    @property
    def fight_object(self) -> Fight | None:
        if not self._fight_object:
            self._fight_object = fight_storage.get(self.fight_group_name)
        return self._fight_object

    @fight_object.setter
    def fight_object(self, fight: Fight):
        fight_storage.setdefault(self.fight_group_name, fight)
        self._fight_object = fight_storage[self.fight_group_name]

    def remove_fight_object_from_storage(self):
        fight_storage.pop(self.fight_group_name, None)

    async def connect(self):
        self.account_id = self.scope["url_route"]["kwargs"]["account_id"]
        try:
            self.fight = await get_fight_by_account_id(self.account_id)
        except (FightChallenge.DoesNotExist, FightChallenge.MultipleObjectsReturned):
            raise DenyConnection

        # self.fight_object = create_fight_from_fight_challenge(self.fight)

        self.fight_group_name = f"fight_{self.fight.pk}"

        await self.channel_layer.group_add(self.fight_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        fight_object = self.fight_object
        if fight_object is not None and fight_object.is_ended:
            self.remove_fight_object_from_storage()
            if not fight_object.is_draw:
                await finish_fight(self.fight, fight_object.winner.account_id)
            else:
                await finish_fight(self.fight, None)
        await self.channel_layer.group_discard(self.fight_group_name, self.channel_name)

    async def map_action_to_type(self, action_name: str) -> str:
        fight_object = self.fight_object
        if fight_object is not None and fight_object.is_ended:
            return "game_over"

        match action_name:
            case "waiting":
                if fight_object is None:
                    return "wait_to_start"
                return "send_to_opponent"
            case "start_game":
                if fight_object is None:
                    self.fight_object = await create_fight_from_fight_challenge(self.fight)
                    return "start_game"
                return "send_to_opponent"
            case _: return "send_to_opponent"

    async def receive(self, text_data=None, bytes_data=None):
        fight_object = self.fight_object
        if fight_object is not None and fight_object.fight_timer.is_countdown:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        is_json_valid = ensure_json_contains(data, 'account_id', 'action')
        if not is_json_valid:
            return

        account_id = data['account_id']
        action_name = data['action']
        action = map_action(self.account_id, action_name, fight=fight_object)
        action.do_action()

        await self.channel_layer.group_send(
            self.fight_group_name,
            {
                "type": await self.map_action_to_type(action_name),
                "account_id": account_id,
                "action": action_name,
                "text_data": text_data,
            }
        )

    async def wait_to_start(self, event):
        account_id = event['account_id']
        if account_id == self.account_id:
            return
        await self.send(text_data=event['text_data'])

    async def start_game(self, event):
        await self.send(text_data=json.dumps({
            "type": "server_info",
            "message": "game_started",
            "fight": self.fight_object.to_json(),
        }))
        await self.countdown()

    async def countdown(self):
        fight_object = self.fight_object
        if not fight_object.fight_timer.is_countdown:
            return
        while fight_object.fight_timer.is_countdown:
            await asyncio.sleep(0.1)
        await self.send(text_data=json.dumps({
            "type": "server_info",
            "message": "fight_started",
            "fight": fight_object.to_json()
        }))

    async def send_to_opponent(self, event):
        account_id = event['account_id']
        if account_id == self.account_id:
            return
        fight_object = self.fight_object
        send_data = json.dumps({
            "fight": fight_object.to_json(),
            "data": event['text_data']
        })
        await self.send(text_data=send_data)

    async def game_over(self, event):
        fight_object = self.fight_object
        if not fight_object.is_ended:
            return
        await self.send(text_data=json.dumps({
            "type": "server_info",
            "message": "game_over",
            "fight": fight_object.to_json()
        }))
        await self.close()
