Quick Start
===========

Extracting a Color Palette
-----------------------------

.. code-block:: python

   from renoir.color import ColorExtractor, ColorAnalyzer, ColorVisualizer
   from PIL import Image

   extractor = ColorExtractor()
   image = Image.open("artwork.jpg")

   # Extract 6 dominant colors (reproducible with default random_state=42)
   palette = extractor.extract_dominant_colors(image, n_colors=6)
   print(palette)  # [(120, 89, 143), ...]

Naming Colors with Art-Historical Vocabularies
------------------------------------------------

.. code-block:: python

   from renoir.color import ColorNamer

   namer = ColorNamer()
   rgb = (120, 89, 143)

   # Name using four different vocabularies
   for vocab in ["artist", "resene", "natural", "xkcd"]:
       namer.set_vocabulary(vocab)
       name = namer.name(rgb)
       print(f"{vocab}: {name}")

Advanced Metrics
----------------

.. code-block:: python

   from renoir.color import ColorAnalyzer, ColorNamer

   analyzer = ColorAnalyzer()

   # Color Complexity Index
   cci = analyzer.calculate_color_complexity(palette)
   print(f"CCI: {cci['cci']:.3f}")

   # Historical Pigment Probability (for a painting dated 1650)
   namer = ColorNamer(vocabulary="artist")
   hpp = namer.historical_pigment_probability(rgb, year=1650)
   print(hpp)

   # Color Provenance Score
   cps = analyzer.colour_provenance_score(palette, year=1650)
   print(f"Provenance score: {cps['score']:.3f}")

Visualization
-------------

.. code-block:: python

   from renoir.color import ColorVisualizer

   visualizer = ColorVisualizer()
   visualizer.plot_palette(palette, title="Extracted Palette", show_names=True)
