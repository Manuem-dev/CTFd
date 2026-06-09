from django.contrib import admin
from .models import CTFEvent, ChallengeCategory, Challenge, Submission, Solve, ChallengeFile, ChallengeLink


@admin.register(CTFEvent)
class CTFEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'start_date', 'end_date', 'is_public']
    list_filter = ['status', 'is_public']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


@admin.register(ChallengeCategory)
class ChallengeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color', 'sort_order']
    prepopulated_fields = {'slug': ['name']}


class ChallengeFileInline(admin.TabularInline):
    model = ChallengeFile
    extra = 1
    fields = ['label', 'file', 'file_size']
    readonly_fields = ['file_size']


class ChallengeLinkInline(admin.TabularInline):
    model = ChallengeLink
    extra = 1
    fields = ['label', 'url']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'category', 'difficulty', 'point_value', 'solve_count', 'is_active']
    list_filter = ['difficulty', 'is_active', 'category']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title', 'author']
    inlines = [ChallengeFileInline, ChallengeLinkInline]


@admin.register(ChallengeFile)
class ChallengeFileAdmin(admin.ModelAdmin):
    list_display = ['label', 'challenge', 'filename', 'human_size', 'uploaded_at']
    list_filter = ['challenge__event']
    search_fields = ['label', 'challenge__title']
    readonly_fields = ['file_size', 'uploaded_at']

    def filename(self, obj):
        return obj.filename
    filename.short_description = 'Filename'

    def human_size(self, obj):
        return obj.human_size
    human_size.short_description = 'Size'


@admin.register(ChallengeLink)
class ChallengeLinkAdmin(admin.ModelAdmin):
    list_display = ['label', 'challenge', 'url', 'created_at']
    list_filter = ['challenge__event']
    search_fields = ['label', 'url', 'challenge__title']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'is_correct', 'created_at']
    list_filter = ['is_correct']


@admin.register(Solve)
class SolveAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'team', 'created_at']
