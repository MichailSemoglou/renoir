# Changelog

All notable changes to the renoir project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.8.0] - 2026-07-29

### Added

- **Structured logging helper** `renoir.setup_notebook_logging()`: attaches a
  `StreamHandler` to the `renoir` logger namespace so progress messages
  appear in Jupyter notebooks without extra configuration. The handler is
  idempotent; calling the function multiple times does not add duplicates.
  Exported from `renoir.__init__` and implemented in `renoir/logging.py`.
- **Progress callback** on long-running methods:
  `ArtistAnalyzer._extract_work_palettes`, `ArtistAnalyzer.artist_color_signature`,
  `ArtistAnalyzer.analyze_works_color_signature`, and
  `ColorNamer.historical_pigment_probability` now accept an optional
  `progress_callback: Callable[[int, int], None]` parameter. The callback
  is invoked as `callback(completed, total)` after each item, enabling
  integration with `tqdm`, `rich`, or custom progress reporters.
- **CLI with subcommands** in `renoir/cli.py`, using `click` as an
  optional `cli` extra. Four subcommands:
  - `renoir artist <slug>` — metadata and genre/style distributions
  - `renoir extract <image>` — dominant-color palette as JSON or CSS
  - `renoir name <color>` — perceptually accurate color naming via CIEDE2000
  - `renoir prompt <image>` — GenAI prompt from image palette
    Stdout is machine-readable; progress writes to stderr. Install with
    `pip install renoir-wikiart[cli]`.
- **DSP palette extraction** in `renoir/color/dsp.py` — Distinctness-First
  Palette Selection, a constrained greedy algorithm that maximises perceptual
  distinctness (minimum pairwise ΔE₂₀₀₀) and guarantees at least one WCAG
  AA-compliant contrast pair. Available via
  `ColorExtractor.extract_dominant_colors(method="dsp")` and the CLI
  `--method dsp` flag. Includes semantic role assignment (Surface,
  On-Surface, Primary, Secondary, Accent) for design-token schemas.
- **Shared colorimetry module** `renoir/color/_colorimetry.py`: consolidated
  six duplicated implementations of `srgb_to_lab`, `delta_e2000`,
  `relative_luminance`, `wcag_contrast`, `hex_to_rgb`, and
  `rgb_to_hex` into a single source of truth. `dsp.py`, `namer.py`,
  `analysis.py`, and `extraction.py` now import from this module.
- **DSP refactor**: `_select_from_candidates` split into six single-purpose
  functions (`_greedy_expand_palette`, `_relax_and_retry`,
  `_apply_wcag_replacement`, `_palette_has_aa_pair`, `_intra_min_de`).
  Zero nested closures remain.
- **Progress callback tests**: `historical_pigment_probability` and
  `analyze_works_color_signature` now have unit tests verifying that
  `progress_callback` is invoked and that the final call reports
  `completed == total`.

### Fixed

- **WCAG contrast gamma threshold**: `ColorAnalyzer.calculate_contrast_ratio`
  used an sRGB linearisation threshold of `0.03928` (an approximation)
  instead of the correct IEC 61966-2-1 value of `0.04045`. This could
  produce different contrast ratios from the same input as the DSP module
  and is now unified via `_colorimetry.py`.

## [3.7.0] - 2026-07-28

### Added

- **Automated test suite expansion**: 295 tests (up from 255), 90% code coverage.
  New `tests/conftest.py` with shared fixtures, `tests/test_color_harmony.py`
  (26 tests for harmony detection), and expanded coverage in `test_color_analysis.py`,
  `test_color_visualization.py`, `test_analyzer.py`, and `test_prompt.py`.
- **`tests/helpers.py`**: shared `make_solid_image` utility extracted from
  `test_analyzer.py`, removing the duplicate `_make_image` function.
- **Integration test opt-in**: `pytest_collection_modifyitems` hook in
  `tests/conftest.py` skips integration tests by default and enables them when
  `RUN_INTEGRATION=1` is set or `-m integration` is passed. The previous
  hardcoded `-m "not integration"` in `addopts` did not honor the environment
  variable.
- **Regression test** for `create_artist_overview` on dateless works (the default
  WikiArt dataset shape).
- **Regression test** `test_signature_without_sklearn`: verifies that
  `analyze_works_color_signature` completes without error when sklearn is absent.
- **Regression test** `test_export_palette_css_prefix_with_newline`: verifies
  that a `prefix` ending with a newline character is rejected.

### Fixed

- `create_artist_overview` no longer crashes with `TypeError` when works lack a
  `date` key. The `date_range` ternary now guards both index accesses.
- `compare_palettes([], [])` no longer crashes with `KeyError`. Returns a neutral
  zero-diff dictionary instead.
- `palette_to_prompt_keywords([])` no longer crashes with `ZeroDivisionError`.
  Returns `[]` for empty input, matching sibling methods.
- `extract_artist_works` no longer raises `KeyError` on datasets without an
  `"artist"` feature column. Uses `dataset.features.get("artist")` with a `None`
  guard, matching `list_artists`.
- `analyze_color_temperature_distribution` now returns a neutral dictionary for
  empty input instead of raising `ZeroDivisionError`.
- `Dict[str, any]` type annotations corrected to `Dict[str, Any]` in
  `analysis.py` and `namer.py` (4 locations).
- `compare_artists_genres` display guard changed from `elif show` to `if show`
  so saving no longer suppresses display.
- `ColorNamer.name()` now raises `ValueError` (not `RuntimeError`) when no match
  is found, consistent with `closest_pigment()`.
- Narrowed broad `except Exception` blocks in `analyzer.py` (4 locations) and
  `extraction.py` to specific exception types.
- Removed 9 unused imports and 1 unused variable across 6 source files.
- Fixed README parameter name mismatch (`n` to `n_variations`).
- `_finalize_figure` in `visualization.py` and all save-path branches in
  `analyzer.py` (4 locations) now call `fig.savefig(...)` instead of
  `plt.savefig(...)`, preventing the wrong figure from being saved when another
  matplotlib figure is active.
- `_aggregate_palette` no longer raises `ImportError` when sklearn is absent;
  falls back to returning deduplicated unique colors.
- `_extract_work_palettes` no longer raises `ImportError` when sklearn is absent;
  `ConvergenceWarning` is imported conditionally and the filter is skipped when
  the class is unavailable.
- `export_palette_css` uses `re.fullmatch` instead of `re.match` to validate the
  `prefix` parameter, so strings ending with a newline are correctly rejected
  rather than passing the `$` anchor.
- `plot_named_palette` return type corrected from `Figure` to `Optional[Figure]`
  to match the `ImportError` path that returns `None`.
- `plot_cross_vocabulary_naming` now merges caller-provided `vocabulary_labels`
  over a full copy of the defaults instead of replacing them entirely, ensuring
  every vocabulary has a label before the later lookups.
- `PromptGenerator.generate()` empty-colors guard moved before the lazy
  `_get_namer()` and `_get_analyzer()` calls, avoiding unnecessary vocabulary
  loading on empty input.
- `detect_analogous_harmony` docstring note corrected: wrap-around colors (e.g.,
  350° and 10°) are detected correctly when adjacent after sorting; the actual
  limitation only occurs when intervening hues break the group anchor.
- `quick_analysis` docstring examples updated to doctest style, removing stale
  stdout-style terminal output from an earlier print-based implementation.

### Changed

- **`ColorNamer` thread safety**: `closest_pigment`, `translate`, and
  `historical_pigment_probability` now use temporary `ColorNamer` instances
  instead of mutating and restoring `self.vocabulary`. The class docstring
  documents the thread-safety contract.
- **`extract_artist_works` refactored** to use a single loop with a match
  predicate, eliminating duplicated branching between HuggingFace and
  simple-list code paths.
- **`analyzer.py` helpers extracted**: `_validate_artist_name`,
  `_validate_works_list`, `_count_field`, `_check_viz_or_warn`, and
  `_plot_distribution` replace repeated validation, guard, and plotting blocks.
- **`visualization.py` helpers extracted**: `_draw_palette_strip`,
  `_finalize_figure`, `_draw_candidate_panel`, and `_draw_cross_vocab_cell`
  replace 6 swatch-drawing loops, 12 save/show/return blocks, and two large
  inline rendering sections.
- **`analysis.py`**: `_largest_remainder` moved from an inner function in
  `palette_earth_movers_distance` to module level.
- **`prompt.py`**: `_build_opener`, `_describe_complexity`, and
  `_apply_model_suffixes` extracted from `generate()`.
- **`check_visualization_support`** in `__init__.py` now delegates to the
  `visualization.py` version when matplotlib is available, eliminating the
  duplicate implementation.
- `analyze_temporal_distribution` now calls `_parse_year` instead of duplicating
  the date-parsing logic.
- Plot methods return `return None` (explicit) instead of bare `return` on
  empty-data paths.
- `plot_named_palette` brightness calculation now uses the
  `_calculate_brightness` helper instead of an inline integer-arithmetic formula.
- Docstring notes added for known limitations: hue wrap-around in
  `detect_analogous_harmony`, false-positive risk in `detect_tetradic_harmony`,
  and O(n^3) growth in `palette_earth_movers_distance`.
- Minimum Pillow version raised from `>=8.0.0` to `>=10.3.0` to exclude
  versions with known CVEs.

## [3.6.0] - 2026-07-10

### Added

- **`ArtistAnalyzer.load_dataset()`** — public accessor for the lazily loaded
  WikiArt dataset.
- **`ArtistAnalyzer.list_artists()`** — list artist names available in the
  WikiArt dataset, with an optional limit.
- **Optional `show` parameter on all plotting methods** in `ColorVisualizer`
  and `ArtistAnalyzer`; methods now return a `matplotlib.figure.Figure`.
- **`ColorAnalyzer.color_provenance_score()`** — American-spelling alias for
  `colour_provenance_score()`.
- **`ColorNamer` is now exported at the top-level `renoir` package**.

### Fixed

- `examples/basic_usage.py` no longer tries to iterate genres as a dict or
  call a non-existent `list_artists()` method.
- `examples/visualization_examples.py` correctly labels the style chart as a
  bar chart.
- `docs/wikiart_cheatsheet.md` documents the public `load_dataset()` method.

## [3.5.0] - 2026-07-03

### Added

- **`ArtistAnalyzer.artist_color_signature()`** — high-level API to compute an
  artist's color signature directly from a WikiArt artist name, with temporal
  or random sampling of works and an optional per-period breakdown.
- **`ArtistAnalyzer.analyze_works_color_signature()`** — lower-level signature
  computation over an arbitrary list of works.
- Internal `_sample_works()` / `_aggregate_palette()` helpers supporting the
  new color signature API.

### Fixed

- Temporal sampling could undershoot the requested `limit` when an early
  decade had fewer candidate works than its allotted quota. Shortfalls are
  now redistributed across decades that still have unselected candidates.

## [3.4.1] - 2026-06-26

### Added

- **`ColorVisualizer.plot_historical_pigment_probability()`** — publication-quality panel figure
  for HPP output: color swatch, Color Index name, year of introduction, probability bar, and
  availability badge per candidate pigment.
- **`ColorVisualizer.plot_pemd_comparison()`** — visualizes Palette Earth Mover's Distance for
  one or more palette pairs as proportional color strips with PEMD values annotated between them.
- **`ColorVisualizer.plot_cross_vocabulary_naming()`** — comparative figure displaying color name
  translations across multiple vocabularies (Munsell, ISCC-NBS, historical pigment names, etc.).
- `historical_pigment_probability()` results now include `year_introduced` and `year_discontinued`
  fields per candidate pigment.

### Fixed

- **Brightness calculation in `plot_palette()`** — ITU-R BT.601 luma formula was accidentally
  divided by 1000 due to a line-wrap artifact, producing incorrect text contrast on dark swatches.
  Resolved by delegating to the new shared `_calculate_brightness()` helper.

### Removed

- `verify_installation.py` script and its CI job removed; coverage is provided by the test suite.

## [3.4.0] - 2026-04-21

### Added

- **PromptGenerator module** (`renoir/color/prompt.py`) — Generate descriptive color prompts for
  generative AI workflows from extracted palettes
- **`translate()` / `translate_all_vocabularies()`** methods in `ColorNamer` — Cross-vocabulary
  color name translation (artist ↔ resene ↔ natural ↔ xkcd)
- **Palette Earth Mover's Distance** (`ColorAnalyzer.palette_earth_movers_distance()`) — Optimal-
  transport perceptual distance between palettes using CIEDE2000 as ground metric
- **Color Complexity Index** (`ColorAnalyzer.calculate_color_complexity()`) — Information-theoretic
  measure combining hue entropy, perceptual spread, proportion evenness, and harmony
- **Historical Pigment Probability** (`ColorNamer.historical_pigment_probability()`) — Bayesian
  estimation of which historical pigments could produce a color at a given date; all 49 pigments
  in `artist_pigments.json` carry `year_introduced` fields
- **Color Provenance Score** (`ColorAnalyzer.colour_provenance_score()`) — Weighted pigment-
  probability score per palette with anachronism flagging

### Fixed

- `_validate_export_filename` rewritten to use path-component inspection instead of
  `os.path.commonpath`, resolving false-positive rejections for `/tmp/` and other
  out-of-cwd export paths (Windows drive-letter compatibility included)
- Restored `np.random.RandomState` (MT19937) for reproducible pixel sampling in
  `extract_dominant_colors`, matching the documented `random_state` contract

### Changed

- Test coverage raised from 77 % to 85 % with 27 new parametrized test cases covering
  validation edge-cases, grayscale/all-black images, named-palette visualizations,
  temperature-distribution charts, and save-path branches

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
  - `werner.json` - 65 Werner's Nomenclature of Colors (18th century naturalist vocabulary)
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

## [3.0.1]

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

## Upgrade Guide

### From 3.6.0 to 3.7.0

One breaking behavioral change: `ColorNamer.name()` now raises `ValueError`
instead of `RuntimeError` when no match is found. Callers catching
`RuntimeError` must update their exception handlers. Other behavioral
differences:

- `compare_palettes` and `palette_to_prompt_keywords` now return neutral values
  for empty input instead of raising exceptions.
- `ColorNamer` methods `closest_pigment`, `translate`, and
  `historical_pigment_probability` no longer mutate `self.vocabulary`. Instances
  are now safe to share across threads for read-only operations.
- Integration tests are deselected by default. Run them explicitly with
  `pytest -m integration` or set the `RUN_INTEGRATION=1` environment variable.

### From 3.3.x to 3.4.0

No breaking changes. New imports available:

- `from renoir.color import PromptGenerator`

New `ColorNamer` methods: `translate()`, `translate_all_vocabularies()`, `historical_pigment_probability()`

New `ColorAnalyzer` methods: `palette_earth_movers_distance()`, `calculate_color_complexity()`, `colour_provenance_score()`

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
- [Documentation](https://renoir-wikiart.readthedocs.io)
- [Issue Tracker](https://github.com/MichailSemoglou/renoir/issues)
- [Zenodo DOI](https://doi.org/10.5281/zenodo.17355170)
