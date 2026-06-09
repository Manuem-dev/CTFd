from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Count, Q, F
from django.conf import settings
from django.contrib import messages
import os
from .models import CTFEvent, ChallengeCategory, Challenge, Submission, Solve, ChallengeFile, ChallengeLink
from teams.models import Team, TeamMember


def home(request):
    events = CTFEvent.objects.filter(is_public=True)
    running_events = events.filter(status='running')
    upcoming_events = events.filter(status='upcoming')
    finished_events = events.filter(status='finished')
    return render(request, 'home.html', {
        'running_events': running_events,
        'upcoming_events': upcoming_events,
        'finished_events': finished_events,
    })


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')


def event_detail(request, slug):
    event = get_object_or_404(CTFEvent, slug=slug)
    challenges = Challenge.objects.filter(event=event, is_active=True)
    categories = ChallengeCategory.objects.filter(
        challenges__event=event,
        challenges__is_active=True
    ).distinct()

    solved_ids = set()
    if request.user.is_authenticated:
        solved_ids = set(
            Solve.objects.filter(user=request.user, event=event)
            .values_list('challenge_id', flat=True)
        )

    # Team for this event
    user_team = None
    if request.user.is_authenticated:
        tm = TeamMember.objects.filter(
            user=request.user, team__event=event
        ).select_related('team').first()
        if tm:
            user_team = tm.team

    return render(request, 'events/detail.html', {
        'event': event,
        'challenges': challenges,
        'categories': categories,
        'solved_ids': solved_ids,
        'user_team': user_team,
    })


def event_scoreboard(request, slug):
    event = get_object_or_404(CTFEvent, slug=slug)

    # Team scoreboard
    team_scores = (
        Team.objects.filter(event=event)
        .annotate(
            total_score=Sum('solves__challenge__point_value', default=0),
            total_solves=Count('solves')
        )
        .order_by('-total_score', 'total_solves')
    )

    # Individual scoreboard
    user_scores = (
        Solve.objects.filter(event=event)
        .values('user__username')
        .annotate(
            total_score=Sum('challenge__point_value'),
            total_solves=Count('id')
        )
        .order_by('-total_score', 'total_solves')
    )

    return render(request, 'events/scoreboard.html', {
        'event': event,
        'team_scores': team_scores,
        'user_scores': user_scores,
    })


def challenge_detail(request, event_slug, challenge_slug):
    event = get_object_or_404(CTFEvent, slug=event_slug)
    challenge = get_object_or_404(Challenge, event=event, slug=challenge_slug)
    files = ChallengeFile.objects.filter(challenge=challenge)
    links = ChallengeLink.objects.filter(challenge=challenge)
    
    solved = False
    user_team = None
    if request.user.is_authenticated:
        solved = Solve.objects.filter(user=request.user, challenge=challenge).exists()
        tm = TeamMember.objects.filter(
            user=request.user, team__event=event
        ).select_related('team').first()
        if tm:
            user_team = tm.team

    return render(request, 'challenges/detail.html', {
        'event': event,
        'challenge': challenge,
        'solved': solved,
        'user_team': user_team,
        'files': files,
        'links': links,
    })


@login_required
def submit_flag(request, event_slug, challenge_slug):
    event = get_object_or_404(CTFEvent, slug=event_slug)
    challenge = get_object_or_404(Challenge, event=event, slug=challenge_slug)

    if request.method != 'POST':
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    submitted_flag = request.POST.get('flag', '').strip()

    # Get user's team for this event
    user_team = None
    tm = TeamMember.objects.filter(
        user=request.user, team__event=event
    ).select_related('team').first()
    if tm:
        user_team = tm.team

    # Already solved?
    already_solved = Solve.objects.filter(user=request.user, challenge=challenge).exists()

    # Create submission
    submission = Submission.objects.create(
        challenge=challenge,
        user=request.user,
        team=user_team,
        event=event,
        submitted_flag=submitted_flag,
        is_correct=(submitted_flag == challenge.flag),
    )

    is_correct = submission.is_correct

    if is_correct and not already_solved:
        Solve.objects.create(
            challenge=challenge,
            user=request.user,
            team=user_team,
            event=event,
        )
        challenge.solve_count = Solve.objects.filter(challenge=challenge).count()
        challenge.save(update_fields=['solve_count'])

    if request.htmx:
        html = render_to_string('challenges/partials/flag_result.html', {
            'is_correct': is_correct,
            'already_solved': already_solved,
            'challenge': challenge,
        })
        return HttpResponse(html)

    return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)


@staff_member_required
def create_event(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_public = request.POST.get('is_public') == 'on'

        if name and slug and start_date and end_date:
            CTFEvent.objects.create(
                name=name,
                slug=slug,
                description=description,
                start_date=start_date,
                end_date=end_date,
                is_public=is_public,
                status='upcoming',
                created_by=request.user,
            )
            return redirect('home')

    return render(request, 'events/create.html')


@staff_member_required
def create_challenge(request, event_slug):
    event = get_object_or_404(CTFEvent, slug=event_slug)
    categories = ChallengeCategory.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        slug = request.POST.get('slug', '').strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        point_value = int(request.POST.get('point_value', 100))
        difficulty = request.POST.get('difficulty', 'medium')
        flag = request.POST.get('flag', '').strip()
        hint = request.POST.get('hint', '').strip()
        author = request.POST.get('author', '').strip()

        if title and slug and flag and category_id:
            category = ChallengeCategory.objects.get(id=category_id)
            challenge = Challenge.objects.create(
                event=event,
                category=category,
                title=title,
                slug=slug,
                description=description,
                point_value=point_value,
                difficulty=difficulty,
                flag=flag,
                hint=hint,
                author=author,
            )
            return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge.slug)

    return render(request, 'challenges/create.html', {
        'event': event,
        'categories': categories,
    })



@staff_member_required
def add_challenge_file(request, event_slug, challenge_slug):
    if request.method != 'POST':
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    event = get_object_or_404(CTFEvent, slug=event_slug)
    challenge = get_object_or_404(Challenge, event=event, slug=challenge_slug)

    uploaded_file = request.FILES.get('file')
    label = request.POST.get('label', '').strip()

    if not uploaded_file or not label:
        messages.error(request, "Please provide both a file and a label.")
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    filename = uploaded_file.name.lower()
    allowed = getattr(settings, 'ALLOWED_CHALLENGE_FILE_EXTENSIONS', ChallengeFile.ALLOWED_EXTENSIONS)
    if not any(filename.endswith(ext) for ext in allowed):
        messages.error(request, "File type not allowed.")
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    max_size = getattr(settings, 'MAX_CHALLENGE_FILE_SIZE', 50 * 1024 * 1024)
    if uploaded_file.size > max_size:
        messages.error(request, "File too large.")
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"=== UPLOAD DEBUG ===")
        logger.error(f"STORAGE: {settings.DEFAULT_FILE_STORAGE}")
        # logger.error(f"ENDPOINT: {settings.AWS_S3_ENDPOINT_URL}")
        # logger.error(f"BUCKET: {settings.AWS_STORAGE_BUCKET_NAME}")
        # logger.error(f"REGION: {settings.AWS_S3_REGION_NAME}")
        # logger.error(f"KEY_ID: {settings.AWS_ACCESS_KEY_ID[:8]}...")
        
        cf = ChallengeFile(challenge=challenge, label=label)
        cf.file = uploaded_file
        cf.file_size = uploaded_file.size
        cf.save()
        
        logger.error(f"=== UPLOAD SUCCESS: {cf.file.name} ===")
        logger.error(f"=== FILE URL: {cf.file.url} ===")
        logger.error(f"=== FILE NAME: {cf.file.name} ===")
        messages.success(request, f"File '{label}' uploaded successfully.")
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"=== UPLOAD FAILED: {e} ===")
        logger.error(traceback.format_exc())
        messages.error(request, f"Upload failed: {e}")

    return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

@staff_member_required
def delete_challenge_file(request, event_slug, challenge_slug, file_id):
    """Delete a file attached to a challenge."""
    if request.method != 'POST':
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    event = get_object_or_404(CTFEvent, slug=event_slug)
    challenge = get_object_or_404(Challenge, event=event, slug=challenge_slug)
    cf = get_object_or_404(ChallengeFile, id=file_id, challenge=challenge)

    # Delete physical file
    if cf.file :
        cf.file.delete(save=False)

    label = cf.label
    cf.delete()
    messages.success(request, f"File '{label}' deleted.")
    return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)


@staff_member_required
def add_challenge_link(request, event_slug, challenge_slug):
    """Add an external link to a challenge."""
    if request.method != 'POST':
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    event = get_object_or_404(CTFEvent, slug=event_slug)
    challenge = get_object_or_404(Challenge, event=event, slug=challenge_slug)

    label = request.POST.get('label', '').strip()
    url = request.POST.get('url', '').strip()

    if not label or not url:
        messages.error(request, "Please provide both a label and a URL.")
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    if not url.startswith(('http://', 'https://')):
        messages.error(request, "URL must start with http:// or https://")
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    ChallengeLink.objects.create(challenge=challenge, label=label, url=url)
    messages.success(request, f"Link '{label}' added.")
    return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)


@staff_member_required
def delete_challenge_link(request, event_slug, challenge_slug, link_id):
    """Delete a link attached to a challenge."""
    if request.method != 'POST':
        return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)

    event = get_object_or_404(CTFEvent, slug=event_slug)
    challenge = get_object_or_404(Challenge, event=event, slug=challenge_slug)
    cl = get_object_or_404(ChallengeLink, id=link_id, challenge=challenge)

    label = cl.label
    cl.delete()
    messages.success(request, f"Link '{label}' deleted.")
    return redirect('challenge_detail', event_slug=event_slug, challenge_slug=challenge_slug)


def event_solves(request, slug):
    event = get_object_or_404(CTFEvent, slug=slug)
    solves = Solve.objects.filter(event=event).select_related('challenge', 'user', 'team')[:50]
    return render(request, 'events/solves.html', {
        'event': event,
        'solves': solves,
    })
