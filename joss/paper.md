---
title: "renoir: A Python Tool for Analyzing Artist-Specific Works from WikiArt"
tags:
  - Python
  - art history
  - digital humanities
  - computational design
  - education
  - datasets
authors:
  - name: Michail Semoglou
    orcid: 0009-0003-3268-5657
    affiliation: "1, 2"
affiliations:
  - name: Tongji University, College of Design and Innovation
    index: 1
  - name: University of Ioannina, School of Fine Arts
    index: 2
date: 13 October 2025
bibliography: paper.bib
---

# Summary

`renoir` is a lightweight Python package designed to facilitate the teaching of computational methods in design and digital humanities courses. It provides an accessible interface for extracting and analyzing works by specific artists from the WikiArt dataset [@wikiart], enabling students to learn data analysis concepts through the lens of art history. Unlike existing computer vision and machine learning tools that focus on algorithmic sophistication, `renoir` prioritizes pedagogical clarity and ease of use for students encountering cultural datasets for the first time.

# Statement of Need

Computational design and digital humanities educators face a persistent challenge: introducing students to data analysis concepts using culturally meaningful datasets while maintaining technical accessibility. While numerous tools exist for advanced machine learning on art datasets [@elgammal2018; @tan2016], few are designed specifically for educational contexts where the goal is to teach fundamental data manipulation, exploration, and analysis skills.

The WikiArt dataset, available through HuggingFace [@wolf2020], contains over 100,000 artworks with rich metadata, making it ideal for teaching. However, its structure requires substantial boilerplate code for basic operations like extracting an artist's complete works or analyzing their genre distributions—operations that should be simple enough for first-day classroom demonstrations. `renoir` fills this gap by providing a clean, documented API specifically designed for educational use.

Key pedagogical advantages include:

1. **Artist-centric analysis**: Unlike dataset-wide tools, focuses on individual artists, aligning with how art history is typically taught
2. **Minimal dependencies**: Requires only the `datasets` library, reducing installation friction in classroom settings
3. **Clear code structure**: Written to be read and understood by students learning Python
4. **Extensibility**: Designed as a starting point for student projects and assignments

# Target Audience

`renoir` is designed for:

- Instructors teaching computational design, digital humanities, or data science courses
- Students learning to work with cultural datasets
- Researchers needing quick exploratory analysis of artist-specific collections
- Workshop facilitators introducing data analysis through art history

# Functionality

The package provides two main usage patterns:

**Quick analysis** for classroom demonstrations:

```python
from renoir import quick_analysis
quick_analysis('pierre-auguste-renoir')
```

**Programmatic access** for student assignments:

```python
from renoir import ArtistAnalyzer

analyzer = ArtistAnalyzer()
works = analyzer.extract_artist_works('claude-monet')
genres = analyzer.analyze_genres(works)
styles = analyzer.analyze_styles(works)
```

Core functionality includes:

- Artist work extraction from WikiArt
- Genre distribution analysis
- Style distribution analysis
- Artist listing and search
- Extensible base for student projects

# Pedagogical Applications

In classroom settings, `renoir` has been used to teach:

1. **Data structures**: Understanding nested dictionaries and lists through artwork metadata
2. **APIs and datasets**: Working with HuggingFace datasets as a first API experience
3. **Exploratory data analysis**: Using `Counter` objects and distribution analysis
4. **Comparative analysis**: Contrasting multiple artists' genre preferences
5. **Data visualization**: Creating charts from analysis results as a follow-up exercise

The tool serves as a foundation for extended projects, such as timeline visualization, style evolution analysis, or comparative studies across artistic movements.

# Comparison to Existing Tools

While several tools work with art datasets, `renoir` is distinguished by its educational focus:

- **ArtGAN** [@elgammal2018]: Focuses on generative models, not exploratory analysis
- **WikiArt Retriever** [@tan2016]: Emphasizes image retrieval, not metadata analysis
- **HuggingFace Datasets**: Provides raw dataset access but requires substantial code for artist-specific operations

`renoir` intentionally avoids machine learning complexity to maintain accessibility for introductory courses.

# Acknowledgements

This tool was developed through teaching computational design courses and observing student needs when working with cultural datasets. Thanks to students whose feedback shaped the API design, and to the WikiArt and HuggingFace teams for making cultural datasets accessible.

# References
