Changelog
=========

3.3.1 (2026-04-19)
------------------

- Version numbers synchronised across all package files
- ``extract_dominant_colors``: added ``random_state`` parameter (default: 42) for
  reproducible pixel sampling and k-means clustering
- ``extract_dominant_colors``: added ``filter_extremes`` parameter (default: True)
  to make pure black/white filtering explicit and configurable
- ``export_palette_css`` / ``export_palette_json``: reject filenames containing
  path-traversal components (``..``)
- Development status classifier updated to ``Production/Stable``
- Dropped Python 3.8 (EOL); minimum is now Python 3.9
- GitHub Actions updated: ``actions/checkout@v4``, ``actions/setup-python@v5``,
  ``codecov/codecov-action@v4``
- Removed duplicate ``setup.py``; ``pyproject.toml`` is the sole build configuration

3.3.0 (2026-03-15)
------------------

- 6 novel algorithmic features: PEMD, CCI, HPP, CPS, Cross-Vocabulary Translation,
  GenAI Colour Prompt Generation
- 17-notebook pedagogical curriculum (complete rewrite of examples)
- Test coverage raised to 78% (166 tests)

3.0.3 (2025-12-01)
------------------

- Bug fixes and documentation improvements

3.0.0 (2025-11-10)
------------------

- Complete colour analysis module (``renoir.color``)
- Four naming vocabularies: artist pigments, Resene, Werner's, XKCD
- CIEDE2000 perceptual colour matching
- 8 visualisation types
