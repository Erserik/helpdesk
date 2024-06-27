# core/context_processors.py

from django.utils.translation import get_language, get_language_info
from django.conf import settings

def language_context(request):
    languages = [
        {
            'code': lang_code,
            'name_local': get_language_info(lang_code)['name_local']
        }
        for lang_code, _ in settings.LANGUAGES
    ]
    current_language = get_language()

    return {
        'languages': languages,
        'LANGUAGE_CODE': current_language,
    }
