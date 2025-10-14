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

`renoir` is a lightweight Python package designed for art and design education and research, addressing a significant gap in computational tools for the art and design community. It provides an accessible interface for extracting and analyzing works by specific artists from the WikiArt dataset [@wikiart], enabling design practitioners, educators, and students to explore visual culture through computational methods. Unlike existing computer vision and machine learning tools that focus on algorithmic sophistication, `renoir` prioritizes visual communication and analytical clarity, making it suitable for creative coding courses, design research, and digital humanities applications where practitioners need to bridge traditional design practice with computational analysis.

# Statement of Need

The art and design research community faces a significant tool gap when working with visual culture datasets. While numerous tools exist for advanced machine learning on art datasets [@elgammal2018; @tan2016], few are designed for art and design practitioners who need accessible analytical capabilities without algorithmic complexity. Art and design educators teaching creative coding, computational design, and digital humanities require tools that bridge traditional art and design practice with data-driven methods, maintaining both pedagogical clarity and research utility.

The WikiArt dataset, available through HuggingFace [@wolf2020], contains over 81,000 artworks with rich metadata covering 129 artists, making it ideal for teaching. However, its structure requires substantial boilerplate code for basic operations like extracting an artist's complete works or analyzing their genre distributions—operations that should be simple enough for first-day classroom demonstrations. `renoir` fills this gap by providing a clean, documented API specifically designed for educational use.

Key pedagogical advantages include:

1. **Artist-centric analysis**: Unlike dataset-wide tools, focuses on individual artists, aligning with how art history is typically taught
2. **Minimal dependencies**: Requires only the `datasets` library, reducing installation friction in classroom settings
3. **Clear code structure**: Written to be read and understood by students learning Python
4. **Extensibility**: Designed as a starting point for student projects and assignments

# Target Audience

`renoir` serves the art and design research and education community:

- **Art and design researchers** studying visual culture, artistic movements, and creative processes
- **Art and design educators** teaching creative coding, computational design, and digital humanities
- **Graduate students** in art and design programs conducting research on visual culture and artistic practice
- **Digital humanities scholars** working with art historical datasets
- **Art and design practitioners** exploring data-driven approaches to understanding visual culture
- **Interdisciplinary researchers** at the intersection of art, design, technology, and cultural analysis

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

# Applications in Design Education and Research

`renoir` supports both pedagogical and research applications:

**Educational Applications:**

1. **Creative coding courses**: Teaching programming through visual culture analysis
2. **Computational design**: Integrating historical research with contemporary practice
3. **Data structures and APIs**: Using cultural datasets to teach technical concepts
4. **Visual analysis methods**: Introducing quantitative approaches to design research
5. **Research methodology**: Combining traditional design inquiry with computational analysis

**Research Applications:**
The tool enables advanced projects including timeline visualization, style evolution analysis, artistic movement comparison, and influence mapping across historical periods. Its extensible architecture supports custom analysis methods for specialized design research questions.

# Comparison to Existing Tools

While several tools work with art datasets, `renoir` is distinguished by its educational focus:

- **ArtGAN** [@elgammal2018]: Focuses on generative models, not exploratory analysis
- **WikiArt Retriever** [@tan2016]: Emphasizes image retrieval, not metadata analysis
- **HuggingFace Datasets**: Provides raw dataset access but requires substantial code for artist-specific operations

`renoir` intentionally avoids machine learning complexity to maintain accessibility for introductory courses.

# Acknowledgements

This tool was developed through teaching computational design courses and observing student needs when working with cultural datasets. Thanks to students whose feedback shaped the API design, and to the WikiArt and HuggingFace teams for making cultural datasets accessible.

# References
