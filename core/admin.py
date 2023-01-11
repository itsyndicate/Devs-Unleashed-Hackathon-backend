from django.contrib import admin
from core.models import Taskogotchi, Project, PlayerProfile, FightChallenge, Player


@admin.register(Taskogotchi)
class TaskogotchiAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'last_updated', 'health', 'strength')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project_id')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'account_id')


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'project')


@admin.register(FightChallenge)
class FightChallengeAdmin(admin.ModelAdmin):
    list_display = ('id', 'initiator', 'opponent', 'status', 'winner', 'draw')
    list_editable = ('status', 'draw')
