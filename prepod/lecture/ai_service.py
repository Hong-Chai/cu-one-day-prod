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

Требования к теме:
- Тема должна быть микро-темой: конкретной, узкой, раскрываемой в одной лекции
- Она должна точно соответствовать области экспертизы пользователя
- Не повторяй завершённые темы по содержанию и углу подачи

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
    prompt = f"""Ты — строгий, но справедливый методист с опытом преподавания в университете.
Твоя задача — найти в тексте лекции настоящие bottleneck'и восприятия: места, где
студент споткнётся и потеряет нить. Не придирайся к мелочам.
Ты общаешься напрямую с преподавателем. Объясняй ему проблемы понятно, по делу.

Тема лекции: {topic}
Экспертиза автора: {expertise}

Текст лекции:
{lecture_text}

ТВОИ КРИТЕРИИ (только они, ничего лишнего):
1. СООТВЕТСТВИЕ ТЕМЕ — лекция раскрывает именно заявленную тему, не уходит в сторону и не оставляет её нераскрытой.
2. ПОТЕРЯННЫЙ КОНТЕКСТ — термин или понятие введено без объяснения, хотя студент его точно не знает.
3. ЛОГИЧЕСКИЙ РАЗРЫВ — автор перешёл от A к C, не объяснив B. Студент не поймёт, откуда взялся вывод.
4. АБСТРАКЦИЯ БЕЗ ПРИМЕРА — сложная идея изложена только теоретически, нет ни одного конкретного примера или аналогии.
5. ПЕРЕГРУЗ — в одном абзаце одновременно вводятся 3+ новых понятия без паузы на усвоение.

Не придирайся!!!  Если нет критической ошибки, то все ок!! Если можно оценить по критерию больше 2/10 (ВСЮ ЛЕКЦИЮ) то все ОК ставь по критерию.

ФОРМАТ ОТВЕТА:
— Найди не более 3 проблем (только самые критичные).
— Для каждой: процитируй проблемное место (поле quote), назови тип проблемы из списка выше (поле problem_type), объясни преподавателю одним предложением почему студент споткнётся именно здесь (поле explanation).
— В конце: одна строка общего вывода — готова ли лекция или нет (поле conclusion).

ЗАПРЕЩЕНО:
— Комментировать стиль, орфографию, длину текста.
— Хвалить автора.
— Предлагать переписать текст за него — только указывать на проблему.

ВАЖНО: В поле quote используй \\n для переносов строк, чтобы JSON был валидным.

Верни ответ СТРОГО в формате JSON без дополнительного текста:
{{
    "status": "ok",
    "feedback": [],
    "conclusion": "Лекция готова: тема раскрыта полностью, логика изложения понятна."
}}

или

{{
    "status": "not ok",
    "feedback": [
        {{
            "quote": "проблемный фрагмент текста (используй \\\\n для переносов)",
            "problem_type": "ТИП ПРОБЛЕМЫ",
            "explanation": "почему это проблема для студента"
        }}
    ],
    "conclusion": "Лекция требует доработки: краткое резюме проблем."
}}"""

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content.strip()

    try:
        # Убираем ТОЛЬКО внешние markdown блоки, не трогая содержимое
        if content.startswith("```json"):
            lines = content.split("\n")
            # Удаляем первую строку с ```json
            lines = lines[1:]
            # Ищем закрывающий ``` с конца
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == "```":
                    lines = lines[:i]
                    break
            content = "\n".join(lines)
        elif content.startswith("```"):
            lines = content.split("\n")
            lines = lines[1:]
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == "```":
                    lines = lines[:i]
                    break
            content = "\n".join(lines)

        # Исправляем неэкранированные переносы строк внутри JSON строк
        fixed_content = []
        in_string = False
        escape_next = False

        for char in content:
            if escape_next:
                fixed_content.append(char)
                escape_next = False
                continue

            if char == "\\":
                fixed_content.append(char)
                escape_next = True
                continue

            if char == '"':
                in_string = not in_string
                fixed_content.append(char)
                continue

            if in_string and char == "\n":
                fixed_content.append("\\n")
            elif in_string and char == "\r":
                continue
            else:
                fixed_content.append(char)

        content = "".join(fixed_content)

        # Парсим JSON
        result = json.loads(content)

        # Проверяем обязательные поля
        if "status" not in result or "feedback" not in result:
            raise ValueError("Missing required fields")

        # Нормализуем статус
        result["status"] = "ok" if result["status"].lower() == "ok" else "not ok"

        # Преобразуем feedback в текст
        if isinstance(result["feedback"], list):
            parts = []
            for i, item in enumerate(result["feedback"], 1):
                parts.append(f"{i}. {item.get('problem_type', 'Проблема')}")
                if "quote" in item:
                    parts.append(f"\nЦитата: \"{item['quote']}\"\n")
                if "explanation" in item:
                    parts.append(f"{item['explanation']}\n")

            if "conclusion" in result:
                parts.append(f"\nВывод: {result['conclusion']}")

            result["feedback"] = "\n".join(parts)

        return result

    except Exception as e:
        original = response.choices[0].message.content.strip()
        return {
            "status": "not ok",
            "feedback": f"Ошибка обработки ответа: {str(e)}\n\nИсходный ответ AI (первые 500 символов):\n{original[:500]}",
        }
