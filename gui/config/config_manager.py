# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/config/config_manager.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Configuration manager for the EuljiroBible GUI.

This module provides a single entry point for loading, saving, and updating user
settings (JSON) used by the GUI. It also includes platform-aware defaults and
utilities related to font selection.

Key responsibilities:

- Read and write the settings JSON file (with UTF-8 encoding).
- Recover safely from missing, corrupted, or invalid settings files by
    falling back to ``DEFAULT_SETTINGS``.
- Provide OS-specific reasonable default font selection.

Note:
    - This module may show GUI error dialogs when a QApplication instance exists. If not, it falls back to console output.
"""

import os
import json
import platform
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFontDatabase, QFont

from core.config import paths
from core.utils.logger import log_debug
from gui.utils.logger import log_error_with_dialog


# Default fallback settings
DEFAULT_SETTINGS = {
    "last_language": "en",
    "font_family": "Arial",
    "font_size": 12,
    "dark_mode": False,
    "last_versions": ["영어 King James Version (1611)"],
    "last_book": "Genesis",
    "last_chapter": 1,
    "last_verse": "1",
    "display_font_family": "Arial",
    "display_font_size": 128,
    "display_text_color": "#ffffff",
    "display_bg_color": "#000000",
    "display_bg_alpha": 0.91,
    "display_overlay_mode": "resizable",
    "display_index": 0,
    "auto_overlay_on_fill": True,
    "always_show_on_off_buttons": False,
    "output_path": "verse_output.txt",
    "poll_enabled": False,
    "poll_interval": 500
}


class ConfigManager:
    """
    Manages loading, saving, and modifying user settings for the application.

    This class centralizes access to the GUI settings JSON file and provides helpers
    for applying safe defaults when the settings file is missing or invalid. All
    methods are static to keep the API simple and to avoid accidental state drift.

    Attributes:
        BASE_DIR (str):
            Absolute path to the application/project base directory.

        DEFAULT_OUTPUT_PATH (str):
            Default verse output path used when ``output_path`` is missing from the
            settings file. Typically ``<BASE_DIR>/verse_output.txt``.
    """

    BASE_DIR = paths.BASE_DIR
    DEFAULT_OUTPUT_PATH = os.path.join(paths.BASE_DIR, "verse_output.txt")

    @staticmethod
    def get_icon_dir():
        """
        Return the absolute path to the application's icon directory.

        Returns:
            str:
                Absolute path to the icon directory (e.g., ``paths.ICON_DIR``).
        """
        return paths.ICON_DIR

    @staticmethod
    def get_bible_data_dir():
        """
        Return the directory path where Bible text JSON files are stored.

        Returns:
            str:
                Absolute path to the Bible text data directory (e.g., ``paths.BIBLE_DATA_DIR``).
        """
        return paths.BIBLE_DATA_DIR

    @staticmethod
    def load():
        """
        Load user settings from disk with safe fallback behavior.

        This method reads the JSON settings file defined by ``paths.SETTINGS_FILE``.
        If the file does not exist, it is created using ``DEFAULT_SETTINGS``.
        If the file exists but is corrupted or not a JSON object, a GUI error dialog
        may be shown (when a QApplication instance exists) and the method falls back to
        ``DEFAULT_SETTINGS``.

        Backward compatibility:
            - Ensures ``output_path`` exists in the loaded settings; if missing, it is populated with ``DEFAULT_OUTPUT_PATH``.

        Returns:
            dict:
                A settings dictionary. If loading fails, returns ``DEFAULT_SETTINGS``.

        Raises:
            None:
                This method is intentionally non-throwing and recovers internally.
        """
        log_debug("[ConfigManager] settings loaded")

        # If no settings file, write defaults first
        if not os.path.exists(paths.SETTINGS_FILE):
            ConfigManager.save(DEFAULT_SETTINGS)

        try:
            with open(paths.SETTINGS_FILE, encoding="utf-8") as f:
                settings = json.load(f)

                if not isinstance(settings, dict):
                    raise ValueError("invalid_settings_format")

                # Backward compatibility: ensure key exists
                if "output_path" not in settings:
                    settings["output_path"] = ConfigManager.DEFAULT_OUTPUT_PATH

                return settings

        except (FileNotFoundError, ValueError) as e:
            # Invalid format or missing
            log_error_with_dialog(e)
            title = "Settings File Error (File-Not-Found Error or Value Error)"
            msg = "The settings file format is invalid. Resetting to default settings."

        except json.JSONDecodeError as e:
            # JSON parse error
            log_error_with_dialog(e)
            title = "Settings File Error (JSON Decode Error)"
            msg = "The settings file is corrupted (JSON error). Resetting to default settings."

        except Exception as e:
            # Other unknown error
            log_error_with_dialog(e)
            title = "Settings File Error (Unknown)"
            msg = "An unexpected error occurred. Resetting to default settings."

        # Show error dialog if GUI is active
        app = QApplication.instance()
        if app:
            QMessageBox.critical(None, title, msg)
        else:
            print(f"[Error] {title}: {msg}")

        return DEFAULT_SETTINGS

    @staticmethod
    def save(data):
        """
        Save the given settings dictionary to the settings JSON file.

        The settings are written to ``paths.SETTINGS_FILE`` using UTF-8 encoding and
        pretty-printed JSON for readability.

        Args:
            data (dict):
                The full settings dictionary to write.

        Raises:
            Exception:
                Re-raises any I/O or serialization error after logging via
                ``log_error_with_dialog``.
        """
        log_debug("[ConfigManager] settings saved")
        try:
            with open(paths.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_error_with_dialog(e)
            raise

    @staticmethod
    def update_partial(data):
        """
        Update part of the settings dictionary and persist it.

        This method loads the current settings, applies the given partial update
        (overwriting existing keys), and saves the result back to disk.

        Args:
            data (dict):
                Partial key-value pairs to merge into the current settings.

        Raises:
            Exception:
                Propagates exceptions from ``load()`` or ``save()`` if saving fails.
        """
        log_debug(f"[ConfigManager] settings partially updated: {data}")
        settings = ConfigManager.load()
        settings.update(data)
        ConfigManager.save(settings)

    @staticmethod
    def get_default_font():
        """
        Return the best available default font family for the current platform.

        This method inspects available system fonts (via ``QFontDatabase``) and selects
        a preferred font from a platform-specific candidate list. If none of the
        candidates are available, it falls back to Qt's default font family.

        Returns:
            str:
                Font family name that is expected to exist on the current system.
        """
        font_db = QFontDatabase()
        system = platform.system()

        if system == "Windows":
            candidates = ["Malgun Gothic", "Segoe UI", "Arial"]
        elif system == "Darwin":
            candidates = ["Apple SD Gothic Neo", "Helvetica", "Arial"]
        else:
            candidates = ["Noto Sans CJK KR", "Noto Sans", "DejaVu Sans"]

        for font in candidates:
            if font in font_db.families():
                return font

        # Fallback to Qt default
        return QFont().defaultFamily()

    @staticmethod
    def save_font(family, size, weight):
        """
        Update and persist the application's main UI font preferences.

        This method updates ``font_family``, ``font_size``, and ``font_weight`` in the
        settings file and saves them immediately.

        Args:
            family (str):
                Font family name.

            size (int):
                Font point size.

            weight (int):
                Font weight value. Typically a Qt weight integer (e.g., values aligned
                with ``QFont.Weight``).
        """
        settings = ConfigManager.load()
        settings.update({
            "font_family": family,
            "font_size": size,
            "font_weight": weight
        })
        ConfigManager.save(settings)