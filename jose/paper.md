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

`renoir` is a lightweight Python package specifically designed for art and design education, addressing a critical pedagogical gap in computational tools for creative disciplines. It provides an accessible, learner-centered interface for extracting and analyzing works by specific artists from the WikiArt dataset [@wikiart], enabling educators to teach data analysis concepts through culturally relevant content that resonates with art and design students. The package prioritizes educational clarity over algorithmic complexity, employing scaffolded learning approaches that allow students to progress from simple demonstrations to complex analytical projects, making it an effective tool for creative coding curricula, computational design courses, and digital humanities pedagogy.

# Statement of Need

Art and design educators face a critical pedagogical challenge when teaching computational methods to creative practitioners. Traditional data science tools often intimidate students from creative backgrounds, creating barriers to learning essential 21st-century skills. While advanced tools like CAN [@elgammal2017] and ArtGAN [@tan2019] exist for research, they lack the pedagogical scaffolding necessary for classroom instruction. Art and design students learn most effectively when abstract computational concepts are grounded in familiar cultural content, yet existing tools require students to work with unfamiliar datasets that disconnect learning from their creative interests and career goals.

This approach aligns with the principles of distant reading [@moretti2013] and cultural analytics [@manovich2020], enabling researchers to identify patterns and trends across large-scale art collections that would be impossible to observe through traditional close examination alone.

The library seamlessly integrates with the Hugging Face `datasets` ecosystem [@wolf2019;@lhoest2021], ensuring compatibility with modern machine learning workflows.

Key pedagogical advantages include:

1. **Artist-centric analysis**: Unlike dataset-wide tools, `renoir` focuses on individual artists, aligning with how art history is typically taught
2. **Minimal dependencies**: `renoir` requires only the `datasets` library, reducing installation friction in classroom settings
3. **Clear code structure**: The package is written to be read and understood by students learning Python
4. **Extensibility**: The tool is designed as a starting point for student projects and assignments

# Target Audience

The primary educational users of `renoir` include:

- **Art and design educators** teaching computational methods, creative coding, and data literacy in creative disciplines
- **Undergraduate students** in art, design, and digital humanities programs learning programming and data analysis
- **Graduate students** developing computational skills for creative research and practice
- **Workshop facilitators** conducting professional development in computational design and digital humanities
- **Curriculum developers** creating interdisciplinary programs that bridge creative practice with technology
- **Academic researchers** studying effective pedagogical approaches for teaching computational skills to creative practitioners

# Learning Objectives

`renoir` is designed to support specific educational learning outcomes in computational creativity:

**Technical Skills:**

- **Data manipulation**: Students learn to extract, filter, and organize cultural datasets using Python
- **API usage**: Understanding how to interact with external data sources and libraries
- **Statistical analysis**: Computing distributions, frequencies, and basic descriptive statistics
- **Data visualization**: Creating meaningful charts and graphs from cultural data

**Conceptual Understanding:**

- **Computational thinking**: Breaking down artistic analysis into algorithmic steps
- **Cultural data literacy**: Understanding how cultural artifacts can be studied quantitatively
- **Research methodology**: Combining traditional art historical inquiry with data-driven approaches
- **Critical evaluation**: Assessing the limitations and biases in computational cultural analysis

**Creative Applications:**

- **Project development**: Using data analysis as a foundation for creative projects
- **Interdisciplinary practice**: Bridging computational methods with traditional creative disciplines
- **Historical contextualization**: Understanding artistic movements through quantitative patterns

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

# Pedagogical Applications and Classroom Implementation

`renoir` has been successfully implemented in various educational contexts with measurable learning outcomes:

**Introductory Programming Courses:**

- **Motivation through relevance**: Students engage more readily with programming when analyzing artists they recognize
- **Scaffolded complexity**: Simple function calls (`quick_analysis()`) introduce programming concepts before advancing to object-oriented approaches
- **Immediate visual feedback**: Results connect abstract code to concrete cultural insights, reinforcing learning

**Data Literacy Curriculum:**

- **Accessible entry point**: Art metadata provides intuitive context for understanding datasets, distributions, and statistical concepts
- **Critical thinking development**: Students question what metrics can and cannot reveal about artistic practice
- **Real-world application**: Skills transfer to other domains requiring data analysis and interpretation

**Computational Design Workshops:**

- **Historical research integration**: Students learn to combine traditional art historical methods with quantitative analysis
- **Portfolio development**: Projects using `renoir` demonstrate technical skills to potential employers in creative industries
- **Interdisciplinary collaboration**: Tool facilitates partnerships between art historians, designers, and data scientists

**Assessment and Learning Outcomes:**
The package's educational effectiveness has been observed through:

- Increased student engagement in computational coursework (measured through attendance and assignment completion)
- Successful project outcomes demonstrating both technical proficiency and cultural understanding
- Positive student feedback regarding the relevance of cultural content to their creative practice
- Effective knowledge transfer to other data analysis contexts in subsequent courses

# Comparison to Existing Tools

While several tools work with art datasets, `renoir` is distinguished by its educational focus:

- **CAN (Creative Adversarial Networks)** [@elgammal2017]: Focuses on generative models, not exploratory analysis
- **ArtGAN** [@tan2019]: Emphasizes conditional image synthesis, not metadata analysis
- **HuggingFace Datasets** [@lhoest2021]: Provides raw dataset access but requires substantial code for artist-specific operations

`renoir` intentionally avoids machine learning complexity to maintain accessibility for introductory courses.

# Acknowledgements

The author developed this tool through teaching computational design courses and observing student needs when working with cultural datasets. Thanks to students whose feedback shaped the API design, and to the WikiArt and HuggingFace teams for making cultural datasets accessible.

# References
