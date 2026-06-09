from django.db import models
from django.contrib.auth.models import User
import uuid


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey('challenges.CTFEvent', on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_teams')

    class Meta:
        unique_together = ['event', 'slug']
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def score(self):
        return self.solves.aggregate(
            total=models.Sum('challenge__point_value')
        )['total'] or 0

    @property
    def member_count(self):
        return self.members.count()

    @property
    def solve_count(self):
        return self.solves.count()


class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('captain', 'Captain'),
        ('member', 'Member'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['team', 'user']

    def __str__(self):
        return f"{self.user.username} in {self.team.name} ({self.role})"
