from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api_v1.serializers import TaskogotchiSerializer, PlayerProfileSerializer, FightChallengeSerializer, \
    OpponentSerializer, CreatePlayerProfileSerializer, CreateFightChallengeSerializer, UpdateFightChallengeSerializer
from api_v1.utils import validate_request
from core.models import Taskogotchi, PlayerProfile, Project, FightChallenge, Player, FightStatus


@extend_schema(
    methods=['PATCH'], exclude=True
)
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter('account_id', type=str, required=True),
        OpenApiParameter('project_id', type=str, required=True)
    ],
    description='Get taskogotchi by account_id and project_id'
)
@extend_schema(
    methods=['POST'],
    description="Create taskogotchi by account_id and project_id. \n\n"
                "If taskogotchi already exists, will return 409 error. (if not, call @let45fc)\n\n"
                "Requires the following data provided to identify the taskogotchi:\n\n"
                "```\n"
                "{\n\n"
                '\t"account_id": "123456789",\n\n'
                '\t"project_id": "123456789"\n\n'
                "}\n"
                "```"
)
@extend_schema(
    methods=['PUT'],
    description="Update taskogotchi by account_id and project_id. \n\n"
                "If taskogotchi does not exist, will return 404 error. (if not, call @let45fc)\n\n"
                "Requires the following data provided to identify the taskogotchi:\n\n"
                "```\n"
                "{\n\n"
                '\t"account_id": "123456789",\n\n'
                '\t"project_id": "123456789"\n\n'
                "}\n"
                "```"
)
class TaskogotchiView(CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TaskogotchiSerializer
    queryset = Taskogotchi.objects.all()

    def create(self, request, *args, **kwargs):
        validate_request(request, 'project_id', 'account_id')
        account_id = request.data.get('account_id')
        project_id = request.data.get('project_id')
        player_profile = PlayerProfile.objects.get(player__account_id=account_id, project__project_id=project_id)
        if Taskogotchi.objects.filter(profile=player_profile).exists():
            return Response({'error': 'Taskogotchi already exists'}, status=409)
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        validate_request(request, 'project_id', 'account_id')
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        validate_request(request, 'project_id', 'account_id')
        return super().update(request, *args, **kwargs)

    def get_object(self):
        project_id = self.request.data.get('project_id') or self.request.GET.get('project_id')
        account_id = self.request.data.get('account_id') or self.request.GET.get('account_id')
        return self.queryset.get(profile__player__account_id=account_id,
                                 profile__project__project_id=project_id)


@extend_schema(
    methods=['POST'],
    request=CreatePlayerProfileSerializer(),
)
class RegisterPlayerView(APIView):
    """
    Creates a new player and project if necessary. If player already exists, will update it with the provided data.
    (only names of project or user, ids won't change)

    Request data example:
    ```
    {
        "player_name": "test",
        "account_id": "5b10ac8d82e05b22cc7d4ef5",
        "project_id": "75fe4dcc22b50e28d8ca01b5",
        "project_name": "test project"
    }
    ```

    **player_name** and **project_name** are called displayName in Jira and aren't required
    """

    serializer_class = PlayerProfileSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        validate_request(request, 'project_id', 'account_id')
        player_name = request.data.get('player_name')
        account_id = request.data.get('account_id')
        project_id = request.data.get('project_id')
        project_name = request.data.get('project_name')

        if account_id is None or project_id is None:
            raise ValidationError(detail='account_id and project_id are required')

        project, _ = Project.objects.update_or_create(project_id=project_id, defaults={'name': project_name})
        player, _ = Player.objects.update_or_create(account_id=account_id, defaults={'name': player_name})
        user_profile, _ = PlayerProfile.objects.get_or_create(player=player, project=project)
        return Response(PlayerProfileSerializer(user_profile).data)


@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter('account_id', type=str, required=True),
        OpenApiParameter('project_id', type=str, required=True)
    ],
    description='List of all opponents for a given project'
)
class OpponentsListView(ListAPIView, GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = OpponentSerializer
    queryset = Taskogotchi.objects.all()

    def list(self, request, *args, **kwargs):
        validate_request(request, 'project_id', 'account_id')
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def get_queryset(self):
        project_id = self.request.data.get('project_id') or self.request.GET.get('project_id')
        account_id = self.request.data.get('account_id') or self.request.GET.get('account_id')
        return self.queryset.filter(profile__project__project_id=project_id) \
            .exclude(profile__player__account_id=account_id)


@extend_schema(
    methods=['PATCH'], exclude=True
)
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter('account_id', type=str, required=True),
    ],
    description="Retrieve current fight challenge"
)
@extend_schema(
    methods=['POST'],
    request=CreateFightChallengeSerializer(),
    description="Create a new fight challenge\n\n"
    "**Be careful! You can't create new fight if you're already in another fight! "
                "In case you try, you'll get an 409 error.**"
)
@extend_schema(
    methods=['PUT'],
    request=UpdateFightChallengeSerializer(),
    description="Update fight challenge\n\n"
    "Available actions: *accept*, *start*, *complete*, *cancel*.\n\n"
    "If fight doesn't exist, you'll get 404 error. (if not, please notify @let45fc)\n\n"
    "Don't forget to send **account_id** in request data! It is necessary to identify the fight you are in.\n\n"
    "**Important**: when completing a fight, you need to send **\"winner_account_id\"** if there's a winner in fight. "
                "If there's no winner, you need to send **\"winner_account_id\": null** "
                "or not to send this field at all. "
    "If winner_account_id is not provided, the fight will be considered a draw."
)
class FightChallengeView(CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FightChallengeSerializer
    queryset = FightChallenge.objects.all()

    def create(self, request, *args, **kwargs):
        validate_request(request, 'project_id', 'account_id', 'opponent_id')
        if self.get_queryset().exists():
            return Response({'error': "You're already in fight."}, status=409)
        return super().create(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter('account_id', type=str, required=True),
            OpenApiParameter('project_id', type=str, required=True)
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        validate_request(request, 'account_id')
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        validate_request(request, 'project_id', 'account_id', 'action')
        return super().update(request, *args, **kwargs)

    def get_object(self):
        if self.queryset.count() > 1:
            raise ValidationError(detail='Something went wrong. More than one pending fight challenge exists', code=500)
        return self.queryset.first()

    def get_queryset(self):
        account_id = self.request.data.get('account_id') or self.request.GET.get('account_id')
        return self.queryset.filter(Q(opponent__player__account_id=account_id)
                                    | Q(initiator__player__account_id=account_id)) \
            .exclude(status__in=[FightStatus.COMPLETED, FightStatus.CANCELED])
