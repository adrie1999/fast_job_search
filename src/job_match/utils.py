from langdetect import detect
import pycountry
from typing import Optional


def get_language_name(text: str) -> Optional[str]:
    """
    Detects the language of the provided text and returns the corresponding language name.

    Args:
        text (str): The input text for which the language needs to be detected.

    Returns:
        Optional[str]: The name of the detected language or None if the language is not found.
    """
    try:
        language_code = detect(text)
        language = pycountry.languages.get(alpha_2=language_code)
        if language:
            return language.name
        return None
    except Exception as e:
        print(f"Error detecting language: {e}")
        return None
