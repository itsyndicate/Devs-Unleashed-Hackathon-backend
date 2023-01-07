from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, ListAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from core.models import Taskogotchi, PlayerProfile, Project, FightChallenge, Player
from api_v1.serializers import TaskogotchiSerializer, PlayerProfileSerializer, ProjectSerializer, \
    FightChallengeSerializer, OpponentSerializer
from rest_framework.permissions import AllowAny
from api_v1.utils import validate_request


class TaskogotchiView(CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView):
    """
    **GET**: Retrieve a taskogotchi
    **POST**: Create a taskogotchi
    **PUT**: Update a taskogotchi

    All requests require the following data to identify the taskogotchi:
    {
        "account_id": "123456789",
        "project_id": "123456789"
    }
    """
    permission_classes = (AllowAny,)
    serializer_class = TaskogotchiSerializer
    queryset = Taskogotchi.objects.all()

    def create(self, request, *args, **kwargs):
        validate_request(request)
        account_id = request.data.get('account_id')
        project_id = request.data.get('project_id')
        player_profile = PlayerProfile.objects.get(player__account_id=account_id, project__project_id=project_id)
        if Taskogotchi.objects.filter(profile=player_profile).exists():
            return Response({'error': 'Taskogotchi already exists'}, status=400)
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        validate_request(request)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        validate_request(request)
        return super().update(request, *args, **kwargs)

    def get_object(self):
        return self.queryset.get(profile__player__account_id=self.request.data['account_id'],
                                 profile__project__project_id=self.request.data['project_id'])


class RegisterPlayerView(APIView):
    """
    Creates a new user and project if necessary
    Request data example:
    {
        "player_name": "test",
        "account_id": "5b10ac8d82e05b22cc7d4ef5",
        "project_id": "75fe4dcc22b50e28d8ca01b5",
        "project_name": "test project"
    }

    **player_name** and **project_name** are called displayName in Jira and aren't required
    """

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
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


class OpponentsListView(ListAPIView, GenericAPIView):
    """
    **GET**: List all opponents for a given project
    All requests require the following data to identify the taskogotchi:
    {
        "account_id": "123456789",
        "project_id": "123456789"
    }
    """
    permission_classes = (AllowAny,)
    serializer_class = OpponentSerializer
    queryset = Taskogotchi.objects.all()

    def list(self, request, *args, **kwargs):
        validate_request(request)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def get_queryset(self):
        project_id = self.request.data.get('project_id') or self.request.GET.get('project_id')
        account_id = self.request.data.get('account_id') or self.request.GET.get('account_id')
        return self.queryset.filter(profile__project__project_id=project_id)\
            .exclude(profile__player__account_id=account_id)
