# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/config/config_manager.py
Handles loading, saving, and updating user settings for EuljiroBible GUI.
Includes utility for font selection and safe default fallback for corrupted or missing settings.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
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
    """

    BASE_DIR = paths.BASE_DIR
    DEFAULT_OUTPUT_PATH = os.path.join(paths.BASE_DIR, "verse_output.txt")

    @staticmethod
    def get_icon_dir():
        """
        Returns the path to the application's icon directory.

        Returns:
            str: Absolute path to the icon directory.
        """
        return paths.ICON_DIR

    @staticmethod
    def get_bible_data_dir():
        """
        Returns the directory path where Bible JSON files are stored.

        Returns:
            str: Path to Bible text data directory.
        """
        return paths.BIBLE_DATA_DIR

    @staticmethod
    def load():
        """
        Loads the user settings from disk. If missing or invalid, falls back to default.

        Returns:
            dict: Loaded settings or default settings on failure.
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
        Saves the given settings dictionary to the `settings.json` file.

        Args:
            data (dict): The settings to save.
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
        Updates part of the settings dictionary and saves the result.

        Args:
            data (dict): Partial key-value pairs to update.
        """
        log_debug(f"[ConfigManager] settings partially updated: {data}")
        settings = ConfigManager.load()
        settings.update(data)
        ConfigManager.save(settings)

    @staticmethod
    def get_default_font():
        """
        Returns a default font based on the operating system.
        Checks several commonly available fonts in system preference order.

        Returns:
            str: Best available font family for the platform.
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
        Updates and persists the UI font preferences.

        Args:
            family (str): Font family name.
            size (int): Font size.
            weight (int): Font weight value.
        """
        settings = ConfigManager.load()
        settings.update({
            "font_family": family,
            "font_size": size,
            "font_weight": weight
        })
        ConfigManager.save(settings)