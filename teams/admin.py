from django.contrib import admin
from .models import Team, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'created_at']
    list_filter = ['event']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role', 'joined_at']
    list_filter = ['role']
