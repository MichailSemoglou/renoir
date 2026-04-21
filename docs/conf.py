# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Allow Sphinx to import the renoir package
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'renoir'
project_copyright = '2026, Michail Semoglou'
copyright = project_copyright  # noqa: A001 - required by Sphinx
author = 'Michail Semoglou'
release = '3.4.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx_autodoc_typehints',
]

autosummary_generate = True
autodoc_member_order = 'bysource'
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'en'

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo'
html_static_path = ['_static']

html_theme_options = {
    "source_repository": "https://github.com/MichailSemoglou/renoir",
    "source_branch": "main",
    "source_directory": "docs/",
}

html_title = "renoir documentation"
