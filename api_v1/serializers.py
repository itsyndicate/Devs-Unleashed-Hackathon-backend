from rest_framework import serializers
from core.models import Taskogotchi, Project, PlayerProfile, FightChallenge, Player
from django.shortcuts import get_object_or_404


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'project_id')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'account_id')


class PlayerProfileSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    project = ProjectSerializer()

    class Meta:
        model = PlayerProfile
        fields = ('id', 'player', 'project')


class FightChallengeSerializer(serializers.ModelSerializer):
    initiator = PlayerProfileSerializer()
    opponent = PlayerProfileSerializer()
    winner = PlayerProfileSerializer()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = FightChallenge
        fields = ('id', 'initiator', 'opponent', 'status', 'winner', 'draw')


class TaskogotchiSerializer(serializers.ModelSerializer):
    profile = PlayerProfileSerializer(read_only=True)
    account_id = serializers.CharField(write_only=True)
    project_id = serializers.CharField(write_only=True)
    last_updated = serializers.DateTimeField(read_only=True)
    # image = serializers.JSONField()

    def create(self, validated_data):
        player_profile = get_object_or_404(PlayerProfile, player__account_id=validated_data.pop('account_id'),
                                           project__project_id=validated_data.pop('project_id'))
        validated_data['profile'] = player_profile
        return super().create(validated_data)

    class Meta:
        model = Taskogotchi
        fields = ('id', 'profile', 'image', 'last_updated', 'health', 'strength', 'account_id', 'project_id')
