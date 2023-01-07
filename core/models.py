from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    project_id = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    account_id = models.CharField('accountId from Jira', max_length=128, unique=True)

    def __str__(self):
        return self.name


# profile of user in specific project
class PlayerProfile(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='profiles')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='profiles')

    def __str__(self):
        return self.player.name + ' in ' + self.project.name

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        unique_together = ('player', 'project')


class FightStatus(models.TextChoices):
    WAITING_ACCEPT = 'WA', 'Waiting for accept'
    PENDING = 'P', 'Pending'
    COMPLETED = 'CO', 'Completed'
    CANCELED = 'CA', 'Canceled'


class FightChallenge(models.Model):
    initiator = models.ForeignKey('PlayerProfile', on_delete=models.CASCADE, related_name='initiated_fights')
    opponent = models.ForeignKey('PlayerProfile', on_delete=models.CASCADE, related_name='received_fights',
                                 null=True, blank=True)
    status = models.CharField(max_length=2, choices=FightStatus.choices, default=FightStatus.WAITING_ACCEPT)
    winner = models.ForeignKey('PlayerProfile', on_delete=models.CASCADE, related_name='won_fights', null=True,
                               blank=True)
    draw = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        assert self.initiator != self.opponent, "You can't fight with yourself"
        assert self.initiator.project == self.opponent.project, "You can't fight with someone from another project"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Fight between {self.initiator} and {self.opponent}"


class Taskogotchi(models.Model):
    profile = models.OneToOneField('PlayerProfile', on_delete=models.CASCADE, related_name='taskogotchi')
    image = models.JSONField('Image components stored as JSON', null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    health = models.IntegerField(default=100)
    strength = models.IntegerField(default=100)

    class Meta:
        verbose_name = 'Taskogotchi'
        verbose_name_plural = 'Taskogotchies'
