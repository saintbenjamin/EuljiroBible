# -*- coding: utf-8 -*-
"""
Main launcher script for the GUI version of EuljiroBible.

This script serves as the entry point when running EuljiroBible directly.
It delegates the actual initialization and application setup to the
`gui_main.py` module.

:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.
"""

from gui.gui_main import main as gui_main

if __name__ == "__main__":
    # When executed as a script, launch the main GUI application
    gui_main()