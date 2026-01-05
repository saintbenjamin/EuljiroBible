# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/cli/cli_main.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.


Command-line entry point for the EuljiroBible CLI interface.

This module provides a minimal command dispatcher for the CLI. It parses
``sys.argv`` and routes execution to the appropriate command handler.

Supported commands:

- ``bible``: Bible lookup / verse output workflow handled by
  :func:`cli.commands.run_bible_command`.
- ``search``: Keyword search workflow handled by
  :func:`cli.commands.run_search_command`.

Dispatch behavior:

- If no arguments are provided, this module calls ``run_bible_command([])``,
  which is expected to display CLI usage and available versions.
- If the first token is an unknown command, this module falls back to treating
  the entire argument list as a ``bible`` command. This preserves a simple UX
  where users can type version/book references directly without explicitly
  prefixing ``bible``.

Note:
    - This module intentionally keeps parsing and routing logic small. Command semantics, validation, I/O, and user-facing messages belong in :mod:`cli.commands`.
    - CLI error messages are expected to be English-only by project convention.

Example:
    Typical usage patterns::

        $ bible NKRV John 3:16
        $ bible search NKRV "God so loved"
        $ bible NKRV John 3:16   # falls back to 'bible' command
"""

import sys
from cli.commands import run_bible_command, run_search_command


def main():
    """
    Main entry point for the CLI version of EuljiroBible.

    This function reads command-line arguments from ``sys.argv`` and dispatches
    execution to the appropriate command handler.

    Behavior:
        - No arguments: show default Bible command usage (delegated).
        - First argument is ``bible``: dispatch to :func:`cli.commands.run_bible_command`.
        - First argument is ``search``: dispatch to :func:`cli.commands.run_search_command`.
        - Otherwise: fallback to :func:`cli.commands.run_bible_command` with the
          full argument list.

    Returns:
        None
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