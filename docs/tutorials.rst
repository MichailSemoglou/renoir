Tutorials
=========

renoir ships with a 17-notebook progressive curriculum. The notebooks are
located in the ``examples/color_analysis/`` directory and can be opened with
Jupyter Lab or Jupyter Notebook.

.. list-table::
   :header-rows: 1
   :widths: 10 60 30

   * - #
     - Title
     - Key Concepts
   * - 01
     - Colour Palette Extraction
     - k-means, pixel sampling
   * - 02
     - Colour Space Analysis
     - RGB, HSV, HSL
   * - 03
     - Comparative Artist Analysis
     - palette comparison, PEMD
   * - 04
     - Artist Colour Signature
     - statistical profiling
   * - 05
     - Colour Harmony Principles
     - triadic, analogous, tetradic
   * - 06
     - Thematic Colour Analysis
     - CCI, hue entropy
   * - 07
     - Colour Analysis Pipeline
     - end-to-end workflow
   * - 08
     - Movement Colour Evolution
     - temporal analysis
   * - 09
     - Colour Psychology
     - valence, arousal
   * - 10
     - Style Classifier
     - scikit-learn, feature engineering
   * - 11
     - Colour Naming
     - CIEDE2000, four vocabularies
   * - 12
     - Art Movement Classification
     - HPP, CPS
   * - 13
     - Palette Generation (VAE)
     - PyTorch, generative models
   * - 14
     - Artist Colour DNA
     - cross-vocabulary translation
   * - 15
     - Clustering & Anomaly Detection
     - DBSCAN, isolation forest
   * - 16
     - Temporal Artist Evolution
     - longitudinal analysis
   * - 17
     - Capstone Project
     - SHAP, explainable AI

Running the Notebooks
---------------------

.. code-block:: bash

   pip install 'renoir-wikiart[visualization]' jupyter
   jupyter lab examples/color_analysis/
