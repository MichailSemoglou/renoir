# renoir

A computational tool for analyzing artist-specific works from WikiArt with comprehensive color analysis capabilities. Designed for teaching computational color theory and data analysis to art and design students through culturally meaningful examples.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17573993.svg)](https://doi.org/10.5281/zenodo.17573993)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/renoir-wikiart.svg)](https://pypi.org/project/renoir-wikiart/)

## Overview

`renoir` bridges traditional art history with computational methods, providing accessible tools for art data analysis and color theory education. Unlike computer vision tools focused on algorithmic complexity, it emphasizes pedagogical clarity and visual communication for art and design practitioners and educators.

**Version 3.2.0** includes a complete 10-lesson curriculum covering color extraction, analysis, harmony detection, psychology, movement evolution, and machine learning classification.

## Key Features

### Artist Analysis

- Extract and analyze works by 100+ artists from WikiArt
- Built-in visualizations for genre and style distributions
- Temporal analysis of artistic development
- Comparative analysis across artists and movements

### Color Analysis

- **Color Extraction**: K-means clustering for intelligent palette extraction
- **Color Naming**: Evocative, artist-friendly color names (Burnt Sienna, Prussian Blue, etc.)
  - 4 naming vocabularies: artist pigments, Resene, Werner's, XKCD
  - CIEDE2000 perceptually accurate color matching
  - Color Index names for physical paint matching
- **Color Space Analysis**: RGB, HSV, and HSL conversions
- **Statistical Metrics**: Color diversity, saturation, brightness, temperature
- **Color Relationships**: Complementary detection, WCAG contrast ratios
- **Color Harmony Detection**: Triadic, analogous, split-complementary, tetradic schemes
- **8 Visualization Types**: Palettes, color wheels, distributions, 3D spaces
- **Export Capabilities**: CSS variables and JSON formats

### Educational Focus

- **11 Complete Jupyter Notebooks** - Progressive curriculum from basics to ML
- Designed specifically for classroom use and student projects
- Publication-ready visualizations
- WikiArt cheatsheet for quick reference
- Pure Python with minimal dependencies

## Applications

- **Creative Coding Courses**: Teach programming through culturally meaningful datasets
- **Computational Color Theory**: Bridge traditional color theory with data science
- **Art and Design Research**: Quantitative analysis of visual patterns and influences
- **Computational Design**: Explore historical precedents through data-driven methods
- **Digital Humanities**: Generate publication-ready visualizations for academic work

## Installation

### Basic Installation

```bash
pip install renoir-wikiart
```

### With Visualization Support (Recommended)

```bash
pip install 'renoir-wikiart[visualization]'
```

### From Source

```bash
git clone https://github.com/MichailSemoglou/renoir.git
cd renoir
pip install -e .[visualization]
```

## Quick Start

### Basic Artist Analysis

```python
from renoir import quick_analysis

# Text-based analysis
quick_analysis('pierre-auguste-renoir')

# With visualizations
quick_analysis('pierre-auguste-renoir', show_plots=True)
```

### Color Palette Extraction

```python
from renoir import ArtistAnalyzer
from renoir.color import ColorExtractor, ColorVisualizer

# Get artist's works
analyzer = ArtistAnalyzer()
works = analyzer.extract_artist_works('claude-monet', limit=10)

# Extract color palette
extractor = ColorExtractor()
colors = extractor.extract_dominant_colors(works[0]['image'], n_colors=5)

# Visualize with evocative names
visualizer = ColorVisualizer()
visualizer.plot_palette(colors, title="Monet's Palette", show_names=True, vocabulary="artist")
```

### Color Naming

```python
from renoir.color import ColorNamer

namer = ColorNamer(vocabulary="artist")

# Name a single color
name = namer.name((255, 87, 51))
print(name)  # "Burnt Sienna"

# Get detailed information including Color Index name
result = namer.name((0, 49, 83), return_metadata=True)
print(f"{result['name']} ({result['ci_name']})")  # "Prussian Blue (PB27)"

# Find closest physical pigment for digital-to-physical matching
pigment = namer.closest_pigment((100, 150, 220))
print(f"Paint with: {pigment['name']} ({pigment['ci_name']})")
```

### Color Analysis

```python
from renoir.color import ColorAnalyzer

analyzer = ColorAnalyzer()

# Analyze palette statistics
stats = analyzer.analyze_palette_statistics(colors)
print(f"Mean Saturation: {stats['mean_saturation']:.1f}%")
print(f"Mean Brightness: {stats['mean_value']:.1f}%")

# Calculate color diversity
diversity = analyzer.calculate_color_diversity(colors)
print(f"Color Diversity: {diversity:.3f}")

# Analyze color temperature
temp = analyzer.analyze_color_temperature_distribution(colors)
print(f"Warm: {temp['warm_percentage']:.1f}%")
print(f"Cool: {temp['cool_percentage']:.1f}%")

# Detect color harmonies
harmony = analyzer.analyze_color_harmony(colors)
print(f"Harmony Score: {harmony['harmony_score']:.2f}")
print(f"Dominant harmony: {harmony['dominant_harmony']}")
```

## Jupyter Notebooks - Complete 11-Lesson Curriculum

All notebooks are in `examples/color_analysis/`:

### Fundamentals (Lessons 1-3)

1. **01_color_palette_extraction.ipynb** - Introduction to k-means clustering through art
2. **02_color_space_analysis.ipynb** - Understanding RGB vs HSV color spaces
3. **03_comparative_artist_analysis.ipynb** - Comparing artistic movements statistically

### Intermediate (Lessons 4-6)

4. **04_artist_color_signature.ipynb** - Identifying unique color signatures of artists
5. **05_color_harmony_principles.ipynb** - Advanced color harmony detection and analysis
6. **06_thematic_color_analysis.ipynb** - Analyzing portraits, landscapes, and still life

### Advanced (Lessons 7-11)

7. **07_color_analysis_pipeline.ipynb** - Building a complete analysis workflow from scratch
8. **08_movement_color_evolution.ipynb** - Tracing color evolution across art movements
9. **09_color_psychology.ipynb** - Exploring emotional associations of colors in art
10. **10_style_classifier.ipynb** - Building a ML classifier with color features
11. **11_color_naming.ipynb** - **NEW!** Evocative color naming with artist pigments, XKCD, Werner's, and Resene vocabularies

## Documentation

- **[WikiArt Cheatsheet](docs/wikiart_cheatsheet.md)** - Quick reference for all API methods, common artists, genres, styles, and code snippets
- **[Color Naming Implementation](docs/COLOR_NAMING_IMPLEMENTATION.md)** - Technical details of the ColorNamer module

## Advanced Usage

### Artist Work Extraction

```python
from renoir import ArtistAnalyzer

analyzer = ArtistAnalyzer()

# Extract works by specific artist
works = analyzer.extract_artist_works('pierre-auguste-renoir')

# Analyze distributions
genres = analyzer.analyze_genres(works)
styles = analyzer.analyze_styles(works)

print(f"Found {len(works)} works")
print(f"Genres: {genres}")
print(f"Styles: {styles}")
```

### Visualization Examples

```python
# Single artist visualizations
analyzer.plot_genre_distribution('pierre-auguste-renoir')
analyzer.plot_style_distribution('pablo-picasso')

# Compare multiple artists
analyzer.compare_artists_genres(['claude-monet', 'pierre-auguste-renoir', 'edgar-degas'])

# Comprehensive overview
analyzer.create_artist_overview('vincent-van-gogh')

# Save to file
analyzer.plot_genre_distribution('monet', save_path='monet_genres.png')
```

### Color Space Conversions

```python
from renoir.color import ColorAnalyzer

analyzer = ColorAnalyzer()

# Convert RGB to HSV
hsv = analyzer.rgb_to_hsv((255, 87, 51))
print(f"HSV: Hue={hsv[0]:.0f}°, Sat={hsv[1]:.0f}%, Val={hsv[2]:.0f}%")

# Detect complementary colors
complementary = analyzer.detect_complementary_colors(colors)

# Detect triadic harmonies
triadic = analyzer.detect_triadic_harmony(colors)

# Detect analogous color groups
analogous = analyzer.detect_analogous_harmony(colors)

# Calculate contrast ratio
ratio = analyzer.calculate_contrast_ratio((255, 255, 255), (0, 0, 0))
print(f"Contrast ratio: {ratio:.2f}:1")
```

### Advanced Color Visualizations

```python
from renoir.color import ColorVisualizer

visualizer = ColorVisualizer()

# Color wheel visualization
visualizer.plot_color_wheel(colors)

# RGB distribution
visualizer.plot_rgb_distribution(colors)

# HSV distribution
visualizer.plot_hsv_distribution(colors)

# 3D color space
visualizer.plot_3d_rgb_space(colors)

# Compare two palettes
visualizer.compare_palettes(colors1, colors2, labels=("Artist 1", "Artist 2"))

# Comprehensive report
visualizer.create_artist_color_report(colors, "Claude Monet")
```

### Export Color Palettes

```python
from renoir.color import ColorExtractor

extractor = ColorExtractor()

# Export as CSS variables
extractor.export_palette_css(colors, 'palette.css', prefix='monet')

# Export as JSON
extractor.export_palette_json(colors, 'palette.json')
```

## Dataset Information

Uses the [WikiArt dataset](https://huggingface.co/datasets/huggan/wikiart) from HuggingFace:

- Over 81,000 artworks
- Works by 129 artists
- Rich metadata including genre, style, and artist information

## Requirements

### Core Requirements

- Python 3.8+
- datasets >= 2.0.0
- Pillow >= 8.0.0
- numpy >= 1.20.0
- scikit-learn >= 1.0.0
- pandas >= 1.3.0

### Visualization Requirements (Optional)

- matplotlib >= 3.5.0
- seaborn >= 0.11.0

Install with: `pip install 'renoir-wikiart[visualization]'`

## Educational Philosophy

`renoir` is built on these pedagogical principles:

1. **Cultural Relevance**: Uses art history to teach computational concepts
2. **Progressive Complexity**: From simple function calls to advanced ML
3. **Visual Learning**: Students see immediate, meaningful results
4. **Real Data**: Works with actual cultural heritage data, not toy examples
5. **Extensible**: Students can fork and extend for their own projects

## API Overview

### Artist Analysis

- `ArtistAnalyzer` - Main class for artist work extraction and analysis
- `quick_analysis()` - Convenience function for quick exploration

### Color Analysis

- `ColorExtractor` - Extract color palettes using k-means clustering
- `ColorAnalyzer` - Analyze colors across multiple color spaces
- `ColorVisualizer` - Create publication-quality color visualizations

## Citation

If you use this software in your research or teaching, please cite:

```bibtex
@software{semoglou2025renoir,
  author = {Semoglou, Michail},
  title = {renoir: A Python Tool for Analyzing Artist-Specific Works from WikiArt},
  year = {2025},
  version = {3.2.0},
  doi = {10.5281/zenodo.17573993},
  url = {https://github.com/MichailSemoglou/renoir}
}
```

## Contributing

Contributions are welcome, especially:

- Additional pedagogical examples
- Classroom exercises and assignments
- Educational notebooks
- Documentation improvements
- Bug fixes

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- WikiArt dataset creators
- HuggingFace Datasets library
- Students at Tongji University and University of Ioannina whose feedback shaped this tool
- College of Design and Innovation, Tongji University
- School of Fine Arts, University of Ioannina

## Contact

For questions about using this tool in your classroom or research:

- Email: [m.semoglou@tongji.edu.cn](mailto:m.semoglou@tongji.edu.cn)
- Issues: [GitHub Issues](https://github.com/MichailSemoglou/renoir/issues)

## What's New

### v3.2.0 (Latest)

- **5 New Educational Notebooks**: Complete 10-lesson curriculum
  - Thematic Color Analysis (portraits, landscapes, still life)
  - Building Your Own Color Analysis Pipeline
  - Artistic Movement Color Evolution (Renaissance to Abstract)
  - Color Psychology in Art History
  - Building a Style Classifier with Machine Learning
- **WikiArt Cheatsheet**: Quick reference documentation for all API methods
- **Extended Examples**: More code samples and recipes

### v3.1.0

- **Color Harmony Detection**: Detect triadic, analogous, split-complementary, and tetradic color schemes
- **5 New Analysis Methods**: Comprehensive harmony analysis for computational color theory
- **Educational Notebook**: Complete lesson on color harmony principles with interactive examples
- **Multi-Artist Comparison**: Compare harmony preferences across artistic movements

### v3.0.0

- **Color Extraction**: K-means clustering for palette extraction
- **Color Analysis**: Multi-space analysis (RGB, HSV, HSL)
- **Statistical Metrics**: Diversity, saturation, brightness, temperature
- **8 Visualization Types**: Comprehensive color visualization suite
- **Educational Materials**: Complete Jupyter notebooks for teaching
- **Export Capabilities**: CSS and JSON export formats

See [CHANGELOG](https://github.com/MichailSemoglou/renoir/releases) for full details.
