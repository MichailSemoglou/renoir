Changelog
=========

3.4.0 (2026-04-21)
------------------

Added
~~~~~

- ``PromptGenerator`` module (``renoir/color/prompt.py``) -- generate descriptive
  color prompts for generative AI workflows from extracted palettes
- ``translate()`` and ``translate_all_vocabularies()`` methods in ``ColorNamer`` --
  cross-vocabulary color name translation (artist, Resene, Werner's, XKCD)
- ``ColorAnalyzer.palette_earth_movers_distance()`` -- optimal-transport perceptual
  distance between palettes using CIEDE2000 as ground metric
- ``ColorAnalyzer.calculate_color_complexity()`` -- information-theoretic measure
  combining hue entropy, perceptual spread, proportion evenness, and harmony
- ``ColorNamer.historical_pigment_probability()`` -- Bayesian estimation of which
  historical pigments could produce a color at a given date; all 49 pigments in
  ``artist_pigments.json`` carry ``year_introduced`` fields
- ``ColorAnalyzer.colour_provenance_score()`` -- weighted pigment-probability score
  per palette with anachronism flagging
- ``ColorVisualizer.plot_historical_pigment_probability()`` -- render an input color
  alongside its candidate historical pigments with probability bars
- ``ColorVisualizer.plot_pemd_comparison()`` -- visualize palette earth-mover's
  distance comparisons between two or more palettes
- ``ColorVisualizer.plot_cross_vocabulary_naming()`` -- compare color naming across
  multiple vocabularies (artist, Resene, Werner's, XKCD) in a single chart

Fixed
~~~~~

- ``_validate_export_filename`` rewritten to use path-component inspection instead
  of ``os.path.commonpath``, resolving false-positive rejections for ``/tmp/`` and
  other out-of-cwd export paths (Windows drive-letter compatibility included)
- Restored ``np.random.RandomState`` (MT19937) for reproducible pixel sampling in
  ``extract_dominant_colors``, matching the documented ``random_state`` contract

Changed
~~~~~~~

- Test coverage raised from 77% to 85% with 27 new parametrized test cases covering
  validation edge-cases, grayscale/all-black images, named-palette visualizations,
  temperature-distribution charts, and save-path branches

3.3.1 (2025-11-30)
------------------

Added
~~~~~

- Six new educational notebooks (Lessons 12--17): advanced ML and capstone project

  - ``12_art_movement_classification.ipynb`` -- movement classification with SHAP
    explainability
  - ``13_palette_generation_vae.ipynb`` -- Variational Autoencoder palette generation
  - ``14_artist_color_dna.ipynb`` -- artist similarity and color DNA embeddings
  - ``15_clustering_anomaly_detection.ipynb`` -- unsupervised learning for art
    analysis
  - ``16_temporal_artist_evolution.ipynb`` -- tracking artist palette evolution
    over time
  - ``17_capstone_project.ipynb`` -- complete AI-powered art analysis platform

Changed
~~~~~~~

- Display artwork titles in notebooks using format "Title (Artist)" for better
  context
- Updated curriculum from 11 to 17 lessons

Fixed
~~~~~

- Removed extraneous emoticons from example scripts and notebooks for cleaner output

3.3.0 (2025-11-27)
------------------

Added
~~~~~

- ``ColorNamer`` module (``renoir/color/namer.py``) -- evocative color naming with
  perceptual matching

  - CIEDE2000 color difference algorithm for human-like color perception
  - Four naming vocabularies: artist pigments, Resene, Werner's Nomenclature, XKCD
  - 336+ color names across all vocabularies
  - Color Index (CI) name support for professional pigment identification
  - Methods: ``name()``, ``name_palette()``, ``closest_pigment()``,
    ``get_vocabulary_info()``
  - Lazy loading and Lab conversion caching for performance

- Color vocabulary JSON data files in ``renoir/data/colors/``

  - ``artist_pigments.json`` -- 49 traditional artist pigments with CI names
  - ``resene.json`` -- 102 Resene interior design paint colors
  - ``werner.json`` -- 65 Werner's Nomenclature of Colors entries
  - ``xkcd.json`` -- 120+ crowdsourced color names from the XKCD color survey

- ``show_names`` and ``vocabulary`` parameters for ``ColorVisualizer.plot_palette()``
- New ``ColorVisualizer.plot_named_palette()`` method
- New Jupyter notebook: ``11_color_naming.ipynb``
- Demo script: ``examples/color_naming_demo.py``
- Technical documentation: ``docs/COLOR_NAMING_IMPLEMENTATION.md``
- ``MANIFEST.in`` for proper package data inclusion

Changed
~~~~~~~

- Added ``ColorNamer`` to module exports in ``renoir/color/__init__.py``
- Updated ``pyproject.toml`` with ``package_data`` for JSON files

3.0.3 (2025-11-20)
------------------

Added
~~~~~

- New Jupyter notebook: ``04_artist_color_signature.ipynb`` -- artist color
  signature analysis with statistical comparison and HSV visualization

Fixed
~~~~~

- Artist field type checking in ``extract_artist_works`` to handle non-string values
  in dataset (prevents ``AttributeError`` when WikiArt dataset contains integer
  values in the artist field)

3.0.2 (2025-11-11)
------------------

Fixed
~~~~~

- Critical syntax error in ``rgb_to_hls`` color conversion (incorrect variable
  names)
- Missing ``hsl_to_rgb`` method in ``ColorAnalyzer``
- Invalid ``pyproject.toml`` license format (now uses correct TOML table syntax)
- Code formatting inconsistencies across all modules
- Test suite failures (adjusted color temperature test expectations, removed
  invalid validation tests)
- CI/CD pipeline configuration (removed non-existent dependency check)

Changed
~~~~~~~

- Applied black formatting to entire codebase for consistency

3.0.1
-----

Added
~~~~~

- Comprehensive error handling and input validation across all modules
- 85 new test functions covering all features (80%+ code coverage)
- Complete Jupyter notebook tutorials for color analysis
- Integration tests for full workflows
- CI/CD pipeline with GitHub Actions
- Visualization methods in ``ArtistAnalyzer``
- Input validation for all public API methods

Fixed
~~~~~

- Documentation-code alignment issues
- Empty/invalid input handling across all methods

3.0.0 (2025-11-10)
------------------

Added
~~~~~

- Complete color analysis module (``renoir.color``)

  - K-means clustering for palette extraction
  - Multi-space color analysis (RGB, HSV, HSL)
  - Statistical metrics (diversity, saturation, brightness, temperature)
  - Eight visualization types for color data
  - WCAG contrast ratio calculation
  - Complementary color detection

- Export capabilities (CSS variables, JSON)
- ``ColorExtractor``, ``ColorAnalyzer``, and ``ColorVisualizer`` classes
- Three educational Jupyter notebooks
- Comprehensive documentation with examples

2.0.0 (2024-10-13)
------------------

Added
~~~~~

- Visualization capabilities with matplotlib and seaborn
- Genre and style distribution plotting
- Temporal analysis visualizations
- Artist comparison features
- ``quick_analysis()`` convenience function

1.0.0 (2024-10-01)
------------------

- Initial release
- Basic artist work extraction from WikiArt
- Genre, style, and temporal distribution analysis
- MIT License
