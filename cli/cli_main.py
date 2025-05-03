# -*- coding: utf-8 -*-
"""
File: EuljiroBible/cli/cli_main.py

Command-line entry point for the EuljiroBible CLI interface.

This module parses command-line arguments and delegates
the logic to the CLI command engine.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import sys
from cli.commands import run_bible_command, run_search_command


def main():
    """
    Main entry point for the CLI version of EuljiroBible.

    Parses arguments from the command line and executes the relevant logic.
    """
    args = sys.argv[1:]  # Exclude the script name itself

    if not args:
        run_bible_command([])
        return

    cmd = args[0]
    rest = args[1:]

    if cmd == "bible":
        run_bible_command(rest)
    elif cmd == "search":
        run_search_command(rest)
    else:
        # fallback: treat whole args as bible command
        run_bible_command(args)


if __name__ == "__main__":
    # If this script is executed directly, run the CLI interface
    main()