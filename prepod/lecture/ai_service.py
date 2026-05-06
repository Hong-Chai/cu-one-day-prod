import json
from django.conf import settings
from mistralai.client import Mistral

client = Mistral(api_key=settings.MISTRAL_API_KEY)


def generate_topic(expertise, completed_topics):
    """
    Генерирует новую тему для лекции на основе экспертизы пользователя

    Args:
        expertise: Описание экспертизы пользователя
        completed_topics: Список уже завершенных тем

    Returns:
        str: Новая тема для лекции
    """
    completed_topics_str = (
        "\n".join([f"- {topic}" for topic in completed_topics])
        if completed_topics
        else "Нет завершенных тем"
    )

    prompt = f"""На основе следующей экспертизы пользователя сгенерируй одну конкретную тему для лекции.

Экспертиза пользователя:
{expertise}

Уже завершенные темы (не повторяй их):
{completed_topics_str}

# ТВОЙ ПРОМПТ С КРИТЕРИЯМИ ГЕНЕРАЦИИ ТЕМЫ ЗДЕСЬ

Верни ТОЛЬКО название темы, без дополнительных объяснений."""

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()


def check_lecture(topic, lecture_text, expertise):
    """
    Проверяет текст лекции и возвращает фидбэк и статус

    Args:
        topic: Тема лекции
        lecture_text: Текст лекции от пользователя
        expertise: Экспертиза пользователя

    Returns:
        dict: {"status": "ok" или "not ok", "feedback": "текст фидбэка"}
    """
    prompt = f"""Проверь текст лекции на соответствие теме и качество изложения.

Тема: {topic}
Экспертиза автора: {expertise}

Текст лекции:
{lecture_text}

# ТВОЙ ПРОМПТ С КРИТЕРИЯМИ ОЦЕНКИ ЛЕКЦИИ ЗДЕСЬ

Верни ответ СТРОГО в формате JSON без дополнительного текста:
{{
    "status": "ok",
    "feedback": "подробный фидбэк с конкретными замечаниями или похвалой"
}}

или

{{
    "status": "not ok",
    "feedback": "подробный фидбэк с конкретными замечаниями"
}}"""

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content.strip()
    
    # Пытаемся извлечь JSON из ответа
    try:
        # Убираем markdown форматирование если есть
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Ищем JSON объект в тексте
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            content = content[start:end]
        
        result = json.loads(content)
        
        # Проверяем наличие обязательных полей
        if "status" not in result or "feedback" not in result:
            raise ValueError("Missing required fields")
        
        # Нормализуем статус
        if result["status"].lower() in ["ok", "good", "pass", "approved"]:
            result["status"] = "ok"
        else:
            result["status"] = "not ok"
        
        # Если feedback это словарь, преобразуем в текст
        if isinstance(result["feedback"], dict):
            feedback_parts = []
            for key, value in result["feedback"].items():
                if isinstance(value, dict):
                    feedback_parts.append(f"{key.replace('_', ' ').title()}:")
                    for subkey, subvalue in value.items():
                        feedback_parts.append(f"  - {subkey.replace('_', ' ').title()}: {subvalue}")
                else:
                    feedback_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            result["feedback"] = "\n".join(feedback_parts)
            
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # Если не удалось распарсить, возвращаем сам ответ как фидбэк
        return {
            "status": "not ok",
            "feedback": f"Не удалось обработать ответ ИИ. Ответ: {content[:500]}",
        }
