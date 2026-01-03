import os
import sys

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# Add the project root directory to sys.path so that Sphinx can import
# EuljiroBible modules for autodoc.
#
# This assumes the following structure:
#   EuljiroBible/
#     ├── cli/
#     ├── core/
#     ├── data/
#     ├── docs/
#     │     └── source/
#     │           └── conf.py  <-- (this file)
#     ├── gui/
#     ├── json/
#     ├── EuljiroBible.py  (main entry point)
#
# Therefore, "../.." points to the project root.
sys.path.insert(0, os.path.abspath("../.."))

# ---------------------------------------------------------------------------
# Project information
# ---------------------------------------------------------------------------
project = "EuljiroBible"
copyright = "2025, Benjamin J. Choi"
author = "Benjamin J. Choi"
release = "1.5"  # Update this to match the project version if needed

# ---------------------------------------------------------------------------
# General configuration
# ---------------------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",    # Automatically generate documentation from docstrings
    "sphinx.ext.napoleon",   # Support Google/NumPy-style docstrings
    "sphinx.ext.viewcode",   # Add links to highlighted source code
]

templates_path = ["_templates"]
exclude_patterns = []

# ---------------------------------------------------------------------------
# HTML output options
# ---------------------------------------------------------------------------
html_theme = "sphinx_rtd_theme"

# Avoid WARNING: html_static_path entry '_static' does not exist
# If you actually need static assets later, create: docs/source/_static/
_static_dir = os.path.join(os.path.dirname(__file__), "_static")
html_static_path = ["_static"] if os.path.isdir(_static_dir) else []

# ---------------------------------------------------------------------------
# Autodoc configuration
# ---------------------------------------------------------------------------
# Mock imports that are unavailable or unnecessary in the Read the Docs
# build environment (e.g., GUI or runtime-only dependencies).
#
# NOTE:
# - PySide6 may be unavailable in RTD build env (if EuljiroBible imports it anywhere).
# - Other optional deps can be added here if autodoc fails due to missing packages.
autodoc_mock_imports = [
    "PySide6",
    "qdarkstyle",
    "psutil"
]

# Keep output stable and readable
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Make autodoc pages more complete by default (optional but usually helpful)
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "show-inheritance": True,
}

# Napoleon: assume Google-style Args/Returns docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# Reduce noisy warnings if you want (optional)
# nitpicky = False