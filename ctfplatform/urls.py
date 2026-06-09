from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from challenges import views as challenge_views
from teams import views as team_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', challenge_views.home, name='home'),
    path('register/', challenge_views.register_view, name='register'),
    path('login/', challenge_views.login_view, name='login'),
    path('logout/', challenge_views.logout_view, name='logout'),
    path('events/create/', challenge_views.create_event, name='create_event'),
    path('events/<slug:slug>/', challenge_views.event_detail, name='event_detail'),
    path('events/<slug:slug>/scoreboard/', challenge_views.event_scoreboard, name='event_scoreboard'),
    path('events/<slug:slug>/solves/', challenge_views.event_solves, name='event_solves'),
    path('events/<slug:event_slug>/challenges/create/', challenge_views.create_challenge, name='create_challenge'),
    path('events/<slug:event_slug>/challenges/<slug:challenge_slug>/', challenge_views.challenge_detail, name='challenge_detail'),
    path('events/<slug:event_slug>/challenges/<slug:challenge_slug>/submit/', challenge_views.submit_flag, name='submit_flag'),
    # Challenge files & links management
    path('events/<slug:event_slug>/challenges/<slug:challenge_slug>/files/add/', challenge_views.add_challenge_file, name='add_challenge_file'),
    path('events/<slug:event_slug>/challenges/<slug:challenge_slug>/files/<uuid:file_id>/delete/', challenge_views.delete_challenge_file, name='delete_challenge_file'),
    path('events/<slug:event_slug>/challenges/<slug:challenge_slug>/links/add/', challenge_views.add_challenge_link, name='add_challenge_link'),
    path('events/<slug:event_slug>/challenges/<slug:challenge_slug>/links/<uuid:link_id>/delete/', challenge_views.delete_challenge_link, name='delete_challenge_link'),
    # Teams
    path('events/<slug:event_slug>/teams/', team_views.event_teams, name='event_teams'),
    path('events/<slug:event_slug>/teams/create/', team_views.create_team, name='create_team'),
    path('events/<slug:event_slug>/teams/<slug:team_slug>/', team_views.team_detail, name='team_detail'),
    path('events/<slug:event_slug>/teams/<slug:team_slug>/join/', team_views.join_team, name='join_team'),
    path('events/<slug:event_slug>/teams/<slug:team_slug>/leave/', team_views.leave_team, name='leave_team'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
