# WikiArt & Renoir Package Cheatsheet

## Quick Start

```python
from renoir import ArtistAnalyzer
from renoir.color import ColorExtractor, ColorAnalyzer, ColorVisualizer

# Initialize
artist_analyzer = ArtistAnalyzer()
color_extractor = ColorExtractor()
color_analyzer = ColorAnalyzer()
visualizer = ColorVisualizer()
```

---

## Loading Data

### Load Full Dataset
```python
dataset = artist_analyzer.load_dataset()
print(f"Total artworks: {len(dataset)}")  # ~81,000 artworks
```

### Extract Artist Works
```python
works = artist_analyzer.extract_artist_works('claude-monet', limit=20)
for work in works:
    image = work['image']        # PIL Image
    title = work.get('title')    # Artwork title
    genre = work.get('genre')    # Genre index
    style = work.get('style')    # Style index
```

---

## Dataset Fields

| Field | Type | Description |
|-------|------|-------------|
| `image` | PIL.Image | The artwork image |
| `title` | str | Artwork title |
| `artist` | int | Artist index (use `features['artist'].names`) |
| `genre` | int | Genre index (portrait, landscape, etc.) |
| `style` | int | Style/movement index |

### Decode Indices
```python
# Get artist names
artist_names = dataset.features['artist'].names
artist_name = artist_names[work['artist']]

# Get genre names
genre_names = dataset.features['genre'].names
genre_name = genre_names[work['genre']]

# Get style names
style_names = dataset.features['style'].names
style_name = style_names[work['style']]
```

---

## Color Extraction

### Extract Dominant Colors
```python
# Returns list of RGB tuples
palette = color_extractor.extract_dominant_colors(
    image,
    n_colors=5  # Number of colors to extract
)
# palette = [(R, G, B), (R, G, B), ...]
```

### Convert Colors
```python
# RGB to HEX
hex_color = color_extractor.rgb_to_hex((255, 128, 64))
# Returns: '#ff8040'

# RGB to HSV
hsv = color_analyzer.rgb_to_hsv((255, 128, 64))
# Returns: (hue, saturation, value)
# hue: 0-360, saturation: 0-100, value: 0-100

# HSV to RGB
rgb = color_analyzer.hsv_to_rgb((30, 75, 100))
```

---

## Color Analysis

### Palette Statistics
```python
stats = color_analyzer.analyze_palette_statistics(palette)
# Returns:
# {
#   'mean_rgb': (R, G, B),
#   'mean_hue': float,        # 0-360
#   'mean_saturation': float, # 0-100
#   'mean_value': float,      # 0-100
#   'std_hue': float,
#   'std_saturation': float,
#   'std_value': float
# }
```

### Temperature Distribution
```python
temp = color_analyzer.analyze_color_temperature_distribution(palette)
# Returns:
# {
#   'warm_count': int,
#   'cool_count': int,
#   'neutral_count': int,
#   'warm_percentage': float,
#   'cool_percentage': float,
#   'neutral_percentage': float,
#   'dominant_temperature': str  # 'warm', 'cool', or 'neutral'
# }
```

### Diversity & Scores
```python
diversity = color_analyzer.calculate_color_diversity(palette)    # 0-1
saturation = color_analyzer.calculate_saturation_score(palette)  # 0-100
brightness = color_analyzer.calculate_brightness_score(palette)  # 0-100
```

### Color Harmony
```python
harmony = color_analyzer.analyze_color_harmony(palette)
# Returns:
# {
#   'harmony_counts': {
#       'complementary': int,
#       'triadic': int,
#       'analogous': int,
#       'split_complementary': int,
#       'tetradic': int
#   },
#   'harmony_score': float,      # 0-1
#   'dominant_harmony': str,
#   'total_harmonies': int,
#   'complementary_pairs': [...],
#   'triadic_sets': [...],
#   'analogous_groups': [...],
#   'split_complementary_sets': [...],
#   'tetradic_sets': [...]
# }
```

### Temperature Classification
```python
temp = color_analyzer.classify_color_temperature((R, G, B))
# Returns: 'warm', 'cool', or 'neutral'
```

---

## Visualization

### Plot Palette
```python
visualizer.plot_palette(
    palette,
    title="My Palette"
)
```

### Plot Color Wheel
```python
visualizer.plot_color_wheel(
    palette,
    title="Color Distribution"
)
```

---

## Common Artists (Sample)

| Artist ID | Name |
|-----------|------|
| `claude-monet` | Claude Monet |
| `vincent-van-gogh` | Vincent van Gogh |
| `pierre-auguste-renoir` | Pierre-Auguste Renoir |
| `pablo-picasso` | Pablo Picasso |
| `edgar-degas` | Edgar Degas |
| `paul-cezanne` | Paul Cézanne |
| `henri-matisse` | Henri Matisse |
| `edvard-munch` | Edvard Munch |
| `wassily-kandinsky` | Wassily Kandinsky |
| `rembrandt` | Rembrandt |
| `johannes-vermeer` | Johannes Vermeer |
| `gustave-klimt` | Gustav Klimt |
| `frida-kahlo` | Frida Kahlo |
| `salvador-dali` | Salvador Dalí |
| `jackson-pollock` | Jackson Pollock |
| `mark-rothko` | Mark Rothko |

---

## Common Genres

| Genre | Description |
|-------|-------------|
| `portrait` | Human subjects |
| `landscape` | Natural scenes |
| `still-life` | Arranged objects |
| `genre-painting` | Daily life scenes |
| `religious-painting` | Religious subjects |
| `mythological-painting` | Mythological scenes |
| `nude-painting-nu` | Figure studies |
| `cityscape` | Urban scenes |
| `marina` | Seascapes |
| `flower-painting` | Floral subjects |

---

## Common Styles/Movements

| Style | Period |
|-------|--------|
| `renaissance` | 1400-1600 |
| `baroque` | 1600-1750 |
| `romanticism` | 1780-1850 |
| `realism` | 1840-1880 |
| `impressionism` | 1860-1890 |
| `post-impressionism` | 1886-1905 |
| `expressionism` | 1905-1920 |
| `cubism` | 1907-1920s |
| `surrealism` | 1920s-1950s |
| `abstract-expressionism` | 1940s-1960s |

---

## Filtering by Style/Genre

```python
def extract_by_style(dataset, style_name, limit=20):
    style_names = dataset.features['style'].names
    target_idx = None
    for idx, name in enumerate(style_names):
        if style_name.lower() in name.lower():
            target_idx = idx
            break

    if target_idx is None:
        return []

    works = []
    for item in dataset:
        if item['style'] == target_idx:
            works.append(item)
            if len(works) >= limit:
                break
    return works

# Usage
impressionist_works = extract_by_style(dataset, 'impressionism', limit=30)
```

---

## HSV Color Reference

| Hue Range | Color |
|-----------|-------|
| 0-30 | Red/Orange |
| 30-60 | Orange/Yellow |
| 60-90 | Yellow/Yellow-Green |
| 90-150 | Green |
| 150-210 | Cyan/Blue-Green |
| 210-270 | Blue/Purple |
| 270-330 | Purple/Magenta |
| 330-360 | Magenta/Red |

---

## Color Temperature Reference

| Temperature | Hue Range |
|-------------|-----------|
| **Warm** | 0-60° and 300-360° (reds, oranges, yellows) |
| **Cool** | 150-270° (blues, greens, purples) |
| **Neutral** | 60-150° or desaturated colors |

---

## Quick Recipes

### Analyze an Artist's Color Signature
```python
works = artist_analyzer.extract_artist_works('claude-monet', limit=15)
all_colors = []
for work in works:
    palette = color_extractor.extract_dominant_colors(work['image'], n_colors=5)
    all_colors.extend(palette)

stats = color_analyzer.analyze_palette_statistics(all_colors)
temp = color_analyzer.analyze_color_temperature_distribution(all_colors)
harmony = color_analyzer.analyze_color_harmony(all_colors)

print(f"Mean Saturation: {stats['mean_saturation']:.1f}%")
print(f"Dominant Temperature: {temp['dominant_temperature']}")
print(f"Harmony Score: {harmony['harmony_score']:.2f}")
```

### Compare Two Artists
```python
def get_artist_stats(artist_id, n_works=10):
    works = artist_analyzer.extract_artist_works(artist_id, limit=n_works)
    colors = []
    for work in works:
        palette = color_extractor.extract_dominant_colors(work['image'], n_colors=5)
        colors.extend(palette)
    return color_analyzer.analyze_palette_statistics(colors)

monet = get_artist_stats('claude-monet')
vangogh = get_artist_stats('vincent-van-gogh')

print(f"Monet saturation: {monet['mean_saturation']:.1f}%")
print(f"Van Gogh saturation: {vangogh['mean_saturation']:.1f}%")
```

---

## Installation

```bash
pip install renoir-wikiart

# With visualization support
pip install renoir-wikiart[visualization]

# Development install
pip install renoir-wikiart[dev]
```

---

## Resources

- **GitHub**: https://github.com/MichailSemoglou/renoir
- **PyPI**: https://pypi.org/project/renoir-wikiart/
- **WikiArt Dataset**: HuggingFace `huggan/wikiart`

---

*Renoir Package v3.1.3 - Educational tool for art color analysis*
