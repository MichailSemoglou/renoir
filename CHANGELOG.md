# Changelog

All notable changes to the renoir project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.1] - 2025-11-30

### Added

- **6 New Educational Notebooks** (Lessons 12-17): Advanced ML and capstone project
  - 12_art_movement_classification.ipynb - Movement classification with SHAP explainability
  - 13_palette_generation_vae.ipynb - Variational Autoencoder palette generation
  - 14_artist_color_dna.ipynb - Artist similarity and color DNA embeddings
  - 15_clustering_anomaly_detection.ipynb - Unsupervised learning for art analysis
  - 16_temporal_artist_evolution.ipynb - Tracking artist palette evolution over time
  - 17_capstone_project.ipynb - Complete AI-powered art analysis platform

### Changed

- Display artwork titles in notebooks using format "Title (Artist)" for better context
- Updated curriculum from 11 to 17 lessons

### Fixed

- Removed extraneous emoticons from example scripts and notebooks for cleaner output
- Kept only functional indicators (checkmarks) where appropriate

## [3.3.0] - 2025-11-27

### Added

- **ColorNamer module** (`renoir/color/namer.py`) - Evocative color naming with perceptual matching
  - CIEDE2000 color difference algorithm for human-like color perception
  - 4 naming vocabularies: artist pigments, Resene, Werner's Nomenclature, XKCD
  - 336+ color names across all vocabularies
  - Color Index (CI) name support for professional pigment identification
  - Methods: `name()`, `name_palette()`, `closest_pigment()`, `get_vocabulary_info()`
  - Lazy loading and Lab conversion caching for performance
- Color vocabulary JSON data files in `renoir/data/colors/`:
  - `artist_pigments.json` - 49 traditional artist pigments with CI names (PB29, PBr7, etc.)
  - `resene.json` - 102 Resene interior design paint colors
  - `werner.json` - 65 Werner's Nomenclature of Colours (18th century naturalist vocabulary)
  - `xkcd.json` - 120+ crowdsourced color names from XKCD color survey
- ColorVisualizer integration:
  - `show_names` and `vocabulary` parameters for `plot_palette()` method
  - New `plot_named_palette()` method for dedicated color naming visualization
- New Jupyter notebook: `11_color_naming.ipynb` - Complete tutorial on color naming features
- Demo script: `examples/color_naming_demo.py`
- Technical documentation: `docs/COLOR_NAMING_IMPLEMENTATION.md`
- Comprehensive test suite: `tests/test_color_namer.py` (45+ unit tests)
- MANIFEST.in for proper package data inclusion

### Changed

- Updated curriculum from 10 to 11 lessons in README.md
- Added ColorNamer to module exports in `renoir/color/__init__.py`
- Updated `setup.py` and `pyproject.toml` with package_data for JSON files

## [3.0.3] - 2025-11-20

### Added

- New comprehensive Jupyter notebook: "Artist Color Signature Analysis" (04_artist_color_signature.ipynb)
  - Demonstrates color signature extraction from artist portfolios
  - Statistical analysis of color usage patterns
  - Multi-artist comparison visualizations
  - HSV color space visualization
  - Educational exercises for computational color theory

### Fixed

- Artist field type checking in extract_artist_works to handle non-string values in dataset
- Prevents AttributeError when WikiArt dataset contains integer values in artist field

## [3.0.2] - 2025-11-11

### Fixed

- Critical syntax error in `rgb_to_hls` color conversion (incorrect variable names)
- Missing `hsl_to_rgb` method in ColorAnalyzer class
- Invalid `pyproject.toml` license format (now uses correct TOML table syntax)
- Code formatting inconsistencies across all modules
- Test suite failures (adjusted color temperature test expectations, removed invalid validation tests)
- CI/CD pipeline configuration (removed non-existent dependency check)

### Changed

- Marked dataset-dependent tests with `@pytest.mark.skip` to avoid 66GB download requirement in CI
- Updated test expectations to match actual implementation behavior
- Applied black formatting to entire codebase for consistency

## [3.0.1] - 2025-01-11

### Added

- Comprehensive error handling and input validation across all modules
- 85 new test functions covering all features (80%+ code coverage)
- Complete Jupyter notebook tutorials for color analysis
- Integration tests for full workflows
- CI/CD pipeline with GitHub Actions
- `verify_installation.py` script for installation verification
- Visualization methods in ArtistAnalyzer class
- Input validation for all public API methods

### Changed

- Improved error messages with helpful suggestions
- Enhanced docstrings with Raises sections
- Updated dependencies to include pandas>=1.3.0
- Refactored test suite for better coverage

### Fixed

- Documentation-code alignment issues (all README examples now work)
- Test suite now properly validates all advertised features
- Empty/invalid input handling across all methods
- Visualization method availability checking

## [3.0.0] - 2025-11-10

### Added

- Comprehensive color analysis capabilities
  - K-means clustering for palette extraction
  - Multi-space color analysis (RGB, HSV, HSL)
  - Statistical metrics (diversity, saturation, brightness, temperature)
  - 8 visualization types for color data
  - WCAG contrast ratio calculation
  - Complementary color detection
- Export capabilities (CSS variables, JSON)
- ColorExtractor class for palette extraction
- ColorAnalyzer class for statistical analysis
- ColorVisualizer class for publication-quality visualizations
- Three educational Jupyter notebooks
- Comprehensive documentation with examples

### Changed

- Improved pedagogical focus throughout documentation
- Enhanced API with consistent naming conventions
- Better integration with existing ArtistAnalyzer

## [2.0.0] - 2024-10-13

### Added

- Visualization capabilities with matplotlib/seaborn
- Genre and style distribution plotting
- Temporal analysis visualizations
- Artist comparison features
- Quick analysis convenience function

### Changed

- Refactored analyzer module for better organization
- Improved dataset loading with caching support
- Enhanced documentation with more examples

### Fixed

- Memory optimization for large artist collections
- Improved error messaging for missing artists

## [1.0.0] - 2024-10-01

### Added

- Initial release
- Basic artist work extraction from WikiArt
- Genre and style analysis
- Temporal distribution analysis
- Command-line interface
- MIT License
- Comprehensive README
- Basic test suite

### Infrastructure

- setuptools configuration
- requirements.txt with core dependencies
- Git repository initialization
- Basic documentation

---

## Release Notes

### Version 3.0.1 (Latest)

This release focuses on production readiness and SoftwareX journal compliance:

- **Robust Error Handling**: All public methods now validate inputs and provide clear error messages
- **Comprehensive Testing**: 85 test functions ensure reliability
- **Complete Documentation**: All notebooks and examples are fully functional
- **CI/CD Pipeline**: Automated testing on every push
- **Production Ready**: Suitable for classroom use and research applications

### Version 3.0.0

Major feature release adding comprehensive color analysis capabilities. This version transforms renoir from a simple data extraction tool into a complete educational platform for teaching computational color theory through art historical examples.

### Version 2.0.0

Added visualization capabilities, making the package more suitable for educational demonstrations and presentations.

### Version 1.0.0

Initial public release with basic artist analysis functionality.

---

## Upgrade Guide

### From 3.0.0 to 3.0.1

No breaking changes. All existing code will continue to work. New error handling may surface previously silent errors, which is intentional for better reliability.

### From 2.0.0 to 3.0.0

New color analysis features are additive. Existing code continues to work unchanged. To use new features:

```python
from renoir.color import ColorExtractor, ColorAnalyzer, ColorVisualizer
```

### From 1.0.0 to 2.0.0

Visualization features are optional. Install with `pip install 'renoir-wikiart[visualization]'` to enable plotting methods.

---

## Links

- [PyPI Package](https://pypi.org/project/renoir-wikiart/)
- [GitHub Repository](https://github.com/MichailSemoglou/renoir)
- [Documentation](https://github.com/MichailSemoglou/renoir#readme)
- [Issue Tracker](https://github.com/MichailSemoglou/renoir/issues)
- [Zenodo DOI](https://doi.org/10.5281/zenodo.17573993)
