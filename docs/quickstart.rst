Quick Start
===========

Extracting a Colour Palette
-----------------------------

.. code-block:: python

   from renoir.color import ColorExtractor, ColorAnalyzer, ColorVisualizer
   from PIL import Image

   extractor = ColorExtractor()
   image = Image.open("artwork.jpg")

   # Extract 6 dominant colours (reproducible with default random_state=42)
   palette = extractor.extract_dominant_colors(image, n_colors=6)
   print(palette)  # [(120, 89, 143), ...]

Naming Colours with Art-Historical Vocabularies
------------------------------------------------

.. code-block:: python

   from renoir.color import ColorAnalyzer

   analyzer = ColorAnalyzer()
   rgb = (120, 89, 143)

   # Name using four different vocabularies
   for vocab in ["artist", "resene", "natural", "xkcd"]:
       name = analyzer.get_color_name(rgb, vocabulary=vocab)
       print(f"{vocab}: {name}")

Advanced Metrics
----------------

.. code-block:: python

   # Colour Complexity Index
   cci = analyzer.calculate_colour_complexity_index(palette)
   print(f"CCI: {cci['overall_complexity']:.3f}")

   # Historical Pigment Probability (for a painting dated 1650)
   hpp = analyzer.calculate_historical_pigment_probability(rgb, year=1650)
   print(hpp)

   # Colour Provenance Score
   cps = analyzer.calculate_colour_provenance_score(palette, year=1650)
   print(f"Provenance score: {cps['provenance_score']:.3f}")

Visualisation
-------------

.. code-block:: python

   from renoir.color import ColorVisualizer

   visualizer = ColorVisualizer()
   visualizer.plot_palette(palette, title="Extracted Palette", show_names=True)
