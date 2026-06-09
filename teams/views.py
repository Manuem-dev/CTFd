from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Team, TeamMember
from challenges.models import CTFEvent


@login_required
def create_team(request, event_slug):
    event = get_object_or_404(CTFEvent, slug=event_slug)

    # Check if user already has a team in this event
    existing = TeamMember.objects.filter(
        user=request.user, team__event=event
    ).first()
    if existing:
        return redirect('team_detail', event_slug=event_slug, team_slug=existing.team.slug)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()

        if name and slug:
            team = Team.objects.create(
                event=event,
                name=name,
                slug=slug,
                description=description,
                created_by=request.user,
            )
            TeamMember.objects.create(
                team=team,
                user=request.user,
                role='captain',
            )
            return redirect('team_detail', event_slug=event_slug, team_slug=team.slug)

    return render(request, 'teams/create.html', {'event': event})


def team_detail(request, event_slug, team_slug):
    event = get_object_or_404(CTFEvent, slug=event_slug)
    team = get_object_or_404(Team, event=event, slug=team_slug)
    members = team.members.select_related('user').all()
    solves = team.solves.select_related('challenge', 'user').order_by('-created_at')[:20]

    is_member = False
    is_captain = False
    if request.user.is_authenticated:
        tm = TeamMember.objects.filter(team=team, user=request.user).first()
        if tm:
            is_member = True
            is_captain = tm.role == 'captain'

    return render(request, 'teams/detail.html', {
        'event': event,
        'team': team,
        'members': members,
        'solves': solves,
        'is_member': is_member,
        'is_captain': is_captain,
    })


@login_required
def join_team(request, event_slug, team_slug):
    event = get_object_or_404(CTFEvent, slug=event_slug)
    team = get_object_or_404(Team, event=event, slug=team_slug)

    # Check if already in a team for this event
    existing = TeamMember.objects.filter(
        user=request.user, team__event=event
    ).first()
    if existing:
        return redirect('team_detail', event_slug=event_slug, team_slug=team.slug)

    if request.method == 'POST':
        if team.member_count >= 4:
            messages.error(request, "This team is already full (maximum 4 members).")
            return redirect('team_detail', event_slug=event_slug, team_slug=team.slug)

        TeamMember.objects.create(
            team=team,
            user=request.user,
            role='member',
        )
        return redirect('team_detail', event_slug=event_slug, team_slug=team.slug)

    return render(request, 'teams/join.html', {
        'event': event,
        'team': team,
    })


@login_required
def leave_team(request, event_slug, team_slug):
    event = get_object_or_404(CTFEvent, slug=event_slug)
    team = get_object_or_404(Team, event=event, slug=team_slug)

    tm = TeamMember.objects.filter(team=team, user=request.user).first()
    if tm and request.method == 'POST':
        tm.delete()
        # If captain leaves, promote first member or delete team
        if not team.members.exists():
            team.delete()
            return redirect('event_detail', slug=event_slug)
        else:
            first_member = team.members.first()
            first_member.role = 'captain'
            first_member.save()

    return redirect('event_detail', slug=event_slug)


def event_teams(request, event_slug):
    event = get_object_or_404(CTFEvent, slug=event_slug)
    teams = Team.objects.filter(event=event).order_by('name')

    user_team = None
    if request.user.is_authenticated:
        tm = TeamMember.objects.filter(
            user=request.user, team__event=event
        ).select_related('team').first()
        if tm:
            user_team = tm.team

    return render(request, 'teams/list.html', {
        'event': event,
        'teams': teams,
        'user_team': user_team,
    })
