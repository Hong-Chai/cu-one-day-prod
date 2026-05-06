from django.db import models
from django.conf import settings


class LectureSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lecture_sessions')
    current_topic = models.CharField(max_length=500, blank=True, verbose_name="Текущая тема")
    current_lecture_text = models.TextField(blank=True, verbose_name="Черновик лекции")
    current_feedback = models.TextField(blank=True, verbose_name="Последний фидбэк")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Сессия лекций"
        verbose_name_plural = "Сессии лекций"

    def __str__(self):
        return f"Сессия {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"


class CompletedTopic(models.Model):
    session = models.ForeignKey(LectureSession, on_delete=models.CASCADE, related_name='completed_topics')
    topic = models.CharField(max_length=500, verbose_name="Тема")
    lecture_text = models.TextField(verbose_name="Текст лекции")
    feedback = models.TextField(verbose_name="Фидбэк от ИИ")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Завершенная тема"
        verbose_name_plural = "Завершенные темы"

    def __str__(self):
        return f"{self.topic} - {self.completed_at.strftime('%Y-%m-%d')}"
