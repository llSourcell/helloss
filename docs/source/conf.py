
# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../../')) # Point to the project root

# -- Project information -----------------------------------------------------
project = 'Neuro-Analyst OS'
copyright = '2025, Your Name'
author = 'Your Name'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Core library for html generation from docstrings
    'sphinx.ext.napoleon',     # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',     # Add links to source code
    'sphinx_rtd_theme',        # Read the Docs theme
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
