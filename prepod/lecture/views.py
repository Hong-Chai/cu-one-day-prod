from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import LectureSession, CompletedTopic
from .ai_service import generate_topic, check_lecture


@login_required
def lecture_app(request):
    """Главная страница приложения лекций"""
    session, _ = LectureSession.objects.get_or_create(user=request.user)
    
    context = {
        'has_expertise': bool(request.user.expertise),
        'expertise': request.user.expertise,
        'completed_topics': session.completed_topics.all().order_by('-completed_at'),
        'completed_count': session.completed_topics.count(),
        'current_topic': session.current_topic,
        'current_lecture_text': session.current_lecture_text,
        'current_feedback': session.current_feedback,
    }
    
    return render(request, 'lecture/app.html', context)


@login_required
@require_POST
def save_expertise(request):
    """Сохраняет экспертизу пользователя и генерирует первую тему"""
    try:
        data = json.loads(request.body)
        expertise = data.get('expertise', '').strip()
        
        if not expertise:
            return JsonResponse({'error': 'Экспертиза не может быть пустой'}, status=400)
        
        request.user.expertise = expertise
        request.user.save()
        
        session, _ = LectureSession.objects.get_or_create(user=request.user)
        completed_topics = list(session.completed_topics.values_list('topic', flat=True))
        
        topic = generate_topic(expertise, completed_topics)
        
        session.current_topic = topic
        session.current_lecture_text = ''
        session.current_feedback = ''
        session.save()
        
        return JsonResponse({
            'success': True,
            'topic': topic
        })
    except Exception as e:
        print(f"Error in save_expertise: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def submit_lecture(request):
    """Проверяет текст лекции через ИИ"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '').strip()
        lecture_text = data.get('lecture_text', '').strip()
        
        if not topic or not lecture_text:
            return JsonResponse({'error': 'Тема и текст лекции обязательны'}, status=400)
        
        result = check_lecture(topic, lecture_text, request.user.expertise)
        print(f"AI result: {result}")
        
        session, _ = LectureSession.objects.get_or_create(user=request.user)
        
        if result['status'] == 'ok':
            CompletedTopic.objects.create(
                session=session,
                topic=topic,
                lecture_text=lecture_text,
                feedback=result['feedback']
            )
            
            completed_topics = list(session.completed_topics.values_list('topic', flat=True))
            new_topic = generate_topic(request.user.expertise, completed_topics)
            
            session.current_topic = new_topic
            session.current_lecture_text = ''
            session.current_feedback = ''
            session.save()
            
            return JsonResponse({
                'status': 'ok',
                'feedback': result['feedback'],
                'new_topic': new_topic
            })
        else:
            session.current_topic = topic
            session.current_lecture_text = lecture_text
            session.current_feedback = result['feedback']
            session.save()
            
            return JsonResponse({
                'status': 'not ok',
                'feedback': result['feedback']
            })
    except Exception as e:
        print(f"Error in submit_lecture: {e}")  # Логирование
        return JsonResponse({'error': str(e)}, status=500)
