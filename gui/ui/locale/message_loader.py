# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/locale/message_loader.py
Description: Provides multi-language UI message dictionaries and a function to load messages by language code for EuljiroBible.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import os, json
from core.config import paths

# Multi-language message dictionary
HARDCODED_MESSAGES = {
    "ko": {
        "program_title": "을지로교회 성경말씀 v{0}",
        "footer_copyright": "ⓒ 대한예수교장로회(통합) 을지로교회. All rights reserved.",
        "about_title": "을지로교회 성경말씀",
        "about_message": "을지로교회 성경말씀 v{0}\n"
                        "제작: Benjamin J. Choi\n"
                        "소속: 대한예수교장로회(통합) 을지로교회\n"
                        "본 프로그램의 저작권은 을지로교회에 있으며,\n" 
                        "무단 수정 및 배포를 금합니다."
    },
    "en": {
        "program_title": "Euljiro Bible v{0}",
        "footer_copyright": "ⓒ The Eulji-ro Presbyterian Church (TongHap). All rights reserved.",
        "about_title": "Euljiro Bible",
        "about_message": "Euljiro Bible v{0}\n"
                        "Developer: Benjamin J. Choi\n"
                        "Affiliation: Eulji-ro Presbyterian Church\n"
                        "This program is copyrighted by Eulji-ro Presbyterian Church.\n"
                        "Unauthorized modification or distribution is prohibited."
    }
}

DEFAULT_MESSAGES = {
    "language_name": "English",
    "language": "English",
    "menu_help": "Help",
    "menu_lang": "Language",
    "menu_about": "About",
    "menu_tools": "Tools",
    "menu_memory": "Memory monitor",
    "menu_test": "Error test",
    "toggle_btn_poll_enabled": "Worship mode",
    "toggle_btn_poll_disabled": "Meditation mode",
    "tab_verse": "Search verse",
    "tab_search": "Search keyword",
    "tab_font": "Settings",
    "label_alias_full": "Version (full):",
    "label_alias_short": "Version (short):",
    "label_book": "Book",
    "label_chapter": "Chapter",
    "label_verse": "Verse",
    "verse_input_hint": "e.g., 1 or 1-3",
    "btn_prev": "Previous",
    "btn_search": "Search",
    "btn_output": "ON",
    "btn_next": "Next",
    "btn_clear": "OFF",
    "msg_no_word": "No verse",
    "msg_nothing": "(None)",
    "search_keyword_hint": "e.g., God so loved",
    "search_location": "Reference",
    "search_verse": "Verse text",
    "search_summary": "Search summary",
    "search_summary": "Search summary",
    "total_results_label": "Total verses found:",
    "setting_main": "Main settings",
    "label_font_family": "Font",
    "label_font_size": "Size",
    "label_font_weight": "Weight",
    "btn_theme_toggle": "Toggle theme",
    "checkbox_show_on_off": "Always show presentation options",
    "setting_overlay": "Presentation settings",
    "label_display_select": "Display",
    "label_display_font_color": "Font color",
    "label_display_bg_color": "Background color",
    "label_display_bg_alpha": "Background opacity",
    "fullscreen": "Fullscreen",
    "resizable": "Windowed",
    "label_poll_interval": "Polling interval (ms)",
    "btn_poll_interval_save": "Save interval",
    "label_path": "Save location",
    "btn_browse": "Browse",
    "dialog_path": "Choose where to save",
    "info_no_results_title": "No Results",
    "info_no_results_msg": "No matching verses found.",
    "warn_input_title": "Input Error",
    "warn_input_msg": "Please enter a keyword/keywords.",
    "warn_jump_title": "Jump Not Allowed",
    "warn_jump_msg": "Cannot jump while a verse range is entered.",
    "warn_verse_input_title": "Verse Input Error",
    "warn_verse_input_msg": "Invalid verse input.\n(e.g., 1 or 1-3)",
    "warn_no_chapter_title": "No Chapter",
    "warn_no_chapter_msg": "No verses found in {0} chapter {1}.",
    "warn_range_title": "Range Error",
    "warn_range_min": "Verse must be at least 1.",
    "warn_range_max": "Verse range: 1-{0}.",
    "warn_verse_format_msg": "Invalid verse format.\n(e.g., 1 or 1-3)",
    "warn_selection_title": "Selection Error",
    "warn_selection_msg": "Please select verses to save.",
    "warn_range_invalid_order": "Start verse must be less than or equal to end verse.",
    "warn_version_title": "Version Not Selected",
    "warn_version_msg": "Please select at least one Bible version.",
    "warn_common_book_title": "No Common Books",
    "warn_common_book_msg": "Selected versions have no common books.",
    "warning_single_display_title": "Single Display Detected",
    "warning_single_display_msg": "Only one display is detected. Do you still want to launch the overlay?", 
    "error_verse_not_found": "Verse not found: {0}",
    "error_verse_input": "Verse input error: {0}\n(e.g., 1 or 1-3)",
    "error_loading_title": "Loading Error",
    "error_loading_msg": "Error loading {0}:\n{1}",
    "error_saving_title": "Save Error",
    "error_saving_msg": "Error saving file:\n{0}",
    "error_saving_msg_path": "Error saving file at {0}:\n{1}",
    "error_set_saving_title": "Settings Save Error",
    "error_set_saving_msg": "Error saving settings:\n{0}",
    "error_settings_title": "Settings Error",
    "error_settings_msg": "Invalid settings format. Resetting to default.",
    "error_unknown": "An unknown error occurred. Check logs.",
}

_cached_messages = {}
_available_languages = None # Cache to avoid re-reading directory repeatedly

def get_available_languages():
    """
    Returns a dict like { "ko": "한국어", "en": "English" } for all JSON files in translation folder.
    """
    global _available_languages
    if _available_languages is not None:
        return _available_languages

    langs = {}
    if not os.path.exists(paths.TRANSLATION_DIR):
        return langs

    for fname in os.listdir(paths.TRANSLATION_DIR):
        if fname.endswith(".json"):
            lang_code = os.path.splitext(fname)[0]
            path = os.path.join(paths.TRANSLATION_DIR, fname)
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    lang_name = data.get("language_name", lang_code)
                    langs[lang_code] = lang_name # e.g., 'en': 'English'
            except Exception:
                continue # Skip malformed or unreadable files

    _available_languages = langs
    return langs

def load_messages(lang_code):
    """
    Loads UI messages based on the selected language.

    Args:
        lang_code (str): Language code (e.g., 'ko', 'en').

    Returns:
        dict: Dictionary of translated UI messages.
    """
    if lang_code in _cached_messages:
        return _cached_messages[lang_code]

    path = os.path.join(paths.TRANSLATION_DIR, f"{lang_code}.json")
    try:
        with open(path, encoding="utf-8") as f:
            messages = json.load(f)
    except Exception:
        messages = {}

    if not messages:
        messages = DEFAULT_MESSAGES.copy()

    lang_for_hardcode = "ko" if lang_code == "ko" else "en"
    # Overlay hardcoded keys like about/program title,
    # even if translation JSON already has values
    for key, val in HARDCODED_MESSAGES[lang_for_hardcode].items():
        messages[key] = val

    _cached_messages[lang_code] = messages
    return messages