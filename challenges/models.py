from django.db import models
from django.contrib.auth.models import User
import uuid
import os


class CTFEvent(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('running', 'Running'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default='')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.status == 'running'


class ChallengeCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='shield')
    color = models.CharField(max_length=30, default='blue')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'challenge categories'

    def __str__(self):
        return self.name


class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('insane', 'Insane'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(CTFEvent, on_delete=models.CASCADE, related_name='challenges')
    category = models.ForeignKey(ChallengeCategory, on_delete=models.CASCADE, related_name='challenges')
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(blank=True, default='')
    point_value = models.IntegerField(default=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    flag = models.CharField(max_length=500)
    hint = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    solve_count = models.IntegerField(default=0)
    author = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'slug']
        ordering = ['point_value', 'title']

    def __str__(self):
        return f"{self.title} ({self.point_value}pts)"


def challenge_file_upload_path(instance, filename):
    """Upload files to challenge_files/<challenge_id>/<filename>"""
    return f"challenge_files/{instance.challenge.id}/{filename}"


class ChallengeFile(models.Model):
    """A downloadable file attached to a challenge."""
    ALLOWED_EXTENSIONS = ['.py', '.sh', '.zip', '.tar.gz', '.tar', '.txt', '.pcap', '.bin', '.c', '.js']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='files')
    label = models.CharField(max_length=200, help_text="Display name for this file")
    file = models.FileField(upload_to=challenge_file_upload_path)
    file_size = models.PositiveBigIntegerField(default=0, help_text="File size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"{self.label} ({self.challenge.title})"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def extension(self):
        name = self.file.name.lower()
        if name.endswith('.tar.gz'):
            return '.tar.gz'
        return os.path.splitext(name)[1]

    @property
    def file_icon(self):
        ext = self.extension
        icons = {
            '.zip': 'archive',
            '.tar.gz': 'archive',
            '.tar': 'archive',
            '.py': 'python',
            '.sh': 'terminal',
            '.txt': 'document',
            '.pcap': 'network',
            '.c': 'code',
            '.js': 'code',
            '.bin': 'binary',
        }
        return icons.get(ext, 'file')

    @property
    def human_size(self):
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != 'B' else f"{size} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class ChallengeLink(models.Model):
    """An external link attached to a challenge."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=200, help_text="Display text for the link")
    url = models.URLField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.label} → {self.url} ({self.challenge.title})"


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, related_name='submissions')
    event = models.ForeignKey(CTFEvent, on_delete=models.CASCADE, related_name='submissions')
    submitted_flag = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = 'CORRECT' if self.is_correct else 'WRONG'
        return f"{self.user.username} - {self.challenge.title} - {status}"


class Solve(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='solves')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solves')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, related_name='solves')
    event = models.ForeignKey(CTFEvent, on_delete=models.CASCADE, related_name='solves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['challenge', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} solved {self.challenge.title}"
