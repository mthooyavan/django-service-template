import os

import polib
from google.cloud import translate_v2 as translate

from backend_service.settings import base as settings


def translate_text(text, target_language):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    print(f"Translation: {result['input']} -> {result['translatedText']}")
    return result["translatedText"]


def update_po_file(file_path, target_language):
    po = polib.pofile(file_path)
    for entry in po:
        if not entry.msgstr:  # only translate empty msgstr
            translated_text = translate_text(entry.msgid, target_language)
            entry.msgstr = translated_text
    po.save()


def main():
    # Specify the languages you want to translate to
    target_languages = settings.LANGUAGES
    for target_language in target_languages:
        if target_language[0] == "en":
            continue
        for path in settings.LOCALE_PATHS:
            file_path = os.path.join(
                path, target_language[0], "LC_MESSAGES", "django.po"
            )
            update_po_file(file_path, target_language[0])


if __name__ == "__main__":
    main()
