from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


class Project(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Taskogotchi(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='taskogotchi')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    image = models.JSONField('Image components stored as JSON', null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    health = models.IntegerField(default=100)
    strength = models.IntegerField(default=100)

    class Meta:
        unique_together = ('user', 'project')

