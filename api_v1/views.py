from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from core.models import Taskogotchi, PlayerProfile, Project, FightChallenge, Player
from api_v1.serializers import TaskogotchiSerializer, PlayerProfileSerializer, ProjectSerializer, FightChallengeSerializer
from rest_framework.permissions import AllowAny


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
        account_id = request.data.get('account_id')
        project_id = request.data.get('project_id')
        if not account_id or not project_id:
            return Response({'error': 'account_id and project_id are required'}, status=400)
        player_profile = PlayerProfile.objects.get(player__account_id=account_id, project__project_id=project_id)
        if Taskogotchi.objects.filter(profile=player_profile).exists():
            return Response({'error': 'Taskogotchi already exists'}, status=400)
        return super().create(request, *args, **kwargs)

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
            return Response({'error': 'account_id and project_id are required'}, status=400)

        project, _ = Project.objects.update_or_create(project_id=project_id, defaults={'name': project_name})
        player, _ = Player.objects.update_or_create(account_id=account_id, defaults={'name': player_name})
        user_profile, _ = PlayerProfile.objects.get_or_create(player=player, project=project)
        return Response(PlayerProfileSerializer(user_profile).data)
