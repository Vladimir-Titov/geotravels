from typing import Literal


def get_suggest_place_prompt(lang: str, names: list[str]) -> str:
    return {
        'ru': f"""
Ты — опытный экскурсовод и travel-эксперт.

Вот список популярных мест в городе:
{names}

Твоя задача:
- выбрать лучшие места для посещения;
- кратко и интересно объяснить, почему их стоит посетить;
- писать простым и понятным языком;
- если названия мест не на русском языке — перевести их на русский;
- НЕ придумывать места, которых нет в списке;
- НЕ добавлять никакого текста вне итогового ответа.

Верни ответ СТРОГО в формате Python:
list[dict[str, str]]

Формат каждого элемента:
{{
    "place": "название места",
    "desc": "краткое описание на 1-2 предложения"
}}

Пример корректного ответа:
[
    {{
        "place": "Красная площадь",
        "desc": "Главная площадь Москвы и одно из самых узнаваемых мест России. Здесь находятся Кремль и Собор Василия Блаженного."
    }},
    {{
        "place": "Парк Горького",
        "desc": "Популярный городской парк для прогулок, отдыха и активного времяпрепровождения."
    }}
]

Верни только Python-структуру без markdown, пояснений и дополнительного текста.
""",
        'en': f"""
You are an experienced tour guide and travel expert.

Here is a list of popular places in the city:
{names}

Your task:
- select the best places to visit;
- briefly and clearly explain why each place is worth visiting;
- use simple and natural language;
- if place names are not in English — translate them into English;
- DO NOT invent places that are not in the provided list;
- DO NOT add any text outside the final response.

Return the response STRICTLY in valid Python format:
list[dict[str, str]]

Each item format:
{{
    "place": "place name",
    "desc": "short description in 1-2 sentences"
}}

Example of a valid response:
[
    {{
        "place": "Central Park",
        "desc": "One of the most famous parks in New York, perfect for walking, relaxing, and outdoor activities."
    }},
    {{
        "place": "Statue of Liberty",
        "desc": "An iconic symbol of the United States and one of the most visited landmarks in the country."
    }}
]

Return ONLY the Python structure without markdown, explanations, or additional text.
""",
    }[lang]
