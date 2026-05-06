from django.contrib import admin
from .models import LectureSession, CompletedTopic


@admin.register(LectureSession)
class LectureSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)


@admin.register(CompletedTopic)
class CompletedTopicAdmin(admin.ModelAdmin):
    list_display = ('topic', 'session', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('topic', 'session__user__username')
    readonly_fields = ('completed_at',)
