from rest_framework import serializers
from core.models import Taskogotchi, Project, UserProfile, FightChallenge


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'project_id')


class UserProfileSerializers(serializers.ModelSerializer):
    project = ProjectSerializer()

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'account_id', 'project')


class FightChallengeSerializer(serializers.ModelSerializer):
    initiator = UserProfileSerializers()
    opponent = UserProfileSerializers()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = FightChallenge
        fields = ('id', 'initiator', 'opponent', 'status', 'winner', 'draw')


class TaskogotchiSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    project = ProjectSerializer()
    # image = serializers.JSONField()

    class Meta:
        model = Taskogotchi
        fields = ('id', 'user', 'project', 'image', 'last_updated', 'health', 'strength')
