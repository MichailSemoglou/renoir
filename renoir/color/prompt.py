"""
Generative AI colour prompt module.

Converts renoir colour analysis results into structured prompts for
generative AI image and video models (DALL-E, Midjourney, Stable Diffusion,
Runway, Sora). Bridges the gap between computational colour analysis and
AI-assisted design workflows.
"""

from typing import List, Dict, Tuple, Optional, Union


class PromptGenerator:
    """
    Generate structured colour prompts for generative AI models.

    Composes outputs from renoir's colour analysis, naming, and harmony
    detection into descriptive prompt strings that can be used with
    image/video generation APIs.

    Example:
        >>> from renoir.color import ColorExtractor, PromptGenerator
        >>> from PIL import Image
        >>> extractor = ColorExtractor()
        >>> img = Image.open('artwork.jpg')
        >>> colors = extractor.extract_dominant_colors(img, n_colors=5)
        >>> gen = PromptGenerator()
        >>> prompt = gen.generate(colors)
        >>> print(prompt)
    """

    def __init__(self, vocabulary: str = "artist"):
        """
        Initialize PromptGenerator.

        Args:
            vocabulary: Colour naming vocabulary to use (default: 'artist').
        """
        self.vocabulary = vocabulary

    def generate(
        self,
        colors: List[Tuple[int, int, int]],
        proportions: Optional[List[float]] = None,
        style: Optional[str] = None,
        medium: Optional[str] = None,
        mood: Optional[str] = None,
        subject: Optional[str] = None,
        include_harmony: bool = True,
        include_temperature: bool = True,
        include_complexity: bool = True,
        target_model: str = "generic",
    ) -> str:
        """
        Generate a structured colour prompt from a palette.

        Args:
            colors: List of RGB tuples (typically from ColorExtractor).
            proportions: Optional colour proportions (should sum to 1.0).
                         If None, equal proportions are assumed.
            style: Optional art style descriptor (e.g. 'impressionist',
                   'minimalist', 'art deco').
            medium: Optional medium descriptor (e.g. 'oil painting',
                    'watercolour', 'digital illustration').
            mood: Optional mood descriptor (e.g. 'serene', 'dramatic').
            subject: Optional subject descriptor (e.g. 'landscape',
                     'portrait', 'abstract composition').
            include_harmony: Include harmony analysis in prompt (default: True).
            include_temperature: Include warm/cool distribution (default: True).
            include_complexity: Include CCI score description (default: True).
            target_model: Target model hint — 'generic', 'midjourney',
                          'dalle', 'stable_diffusion' (default: 'generic').

        Returns:
            Structured prompt string.

        Example:
            >>> gen = PromptGenerator()
            >>> colors = [(255, 87, 51), (0, 50, 200), (255, 255, 240)]
            >>> prompt = gen.generate(colors, style='impressionist',
            ...                       medium='oil painting')
            >>> print(prompt)
        """
        from .namer import ColorNamer
        from .analysis import ColorAnalyzer

        namer = ColorNamer(vocabulary=self.vocabulary)
        analyzer = ColorAnalyzer()

        if not colors:
            return ""

        if proportions is None:
            proportions = [1.0 / len(colors)] * len(colors)

        # Name each colour
        named = []
        for color, prop in zip(colors, proportions):
            name = namer.name(color)
            pct = round(prop * 100)
            named.append((name, pct, color))

        # Sort by proportion descending
        named.sort(key=lambda x: x[1], reverse=True)

        # Build palette description
        parts = []

        # Subject + medium + style opener
        opener_parts = []
        if subject:
            opener_parts.append(subject.capitalize())
        if medium:
            opener_parts.append(medium)
        if style:
            opener_parts.append(f"in {style} style")

        if opener_parts:
            parts.append(" ".join(opener_parts) + ".")

        # Colour palette
        palette_desc = "Colour palette: " + ", ".join(
            f"{name} ({pct}%)" if pct > 0 else name for name, pct, _ in named
        )
        parts.append(palette_desc + ".")

        # Dominant colour
        dominant_name, _, _ = named[0]
        parts.append(f"Dominant colour: {dominant_name}.")

        # Harmony analysis
        if include_harmony and len(colors) >= 2:
            harmony = analyzer.analyze_color_harmony(colors)
            dominant_harmony = harmony["dominant_harmony"]
            if dominant_harmony != "none":
                harmony_desc = dominant_harmony.replace("_", " ")
                parts.append(f"Colour harmony: {harmony_desc}.")

        # Temperature distribution
        if include_temperature:
            temp = analyzer.analyze_color_temperature_distribution(colors)
            warm_pct = temp["warm_percentage"]
            cool_pct = temp["cool_percentage"]
            dom_temp = temp["dominant_temperature"]
            parts.append(
                f"Colour temperature: {dom_temp}-dominant "
                f"({warm_pct:.0f}% warm, {cool_pct:.0f}% cool)."
            )

        # Complexity
        if include_complexity and len(colors) >= 2:
            complexity = analyzer.calculate_color_complexity(colors, proportions)
            cci = complexity["cci"]
            if cci < 0.3:
                complexity_word = "Low"
            elif cci < 0.6:
                complexity_word = "Moderate"
            else:
                complexity_word = "High"
            parts.append(f"{complexity_word} colour complexity (CCI: {cci:.2f}).")

        # Mood
        if mood:
            parts.append(f"Mood: {mood}.")

        # Model-specific formatting
        prompt = " ".join(parts)

        if target_model == "midjourney":
            prompt = prompt + " --v 6"
        elif target_model == "stable_diffusion":
            # SD prefers comma-separated keywords at the end
            prompt = prompt + ", highly detailed, professional colour grading"

        return prompt

    def generate_variation_prompts(
        self,
        colors: List[Tuple[int, int, int]],
        n_variations: int = 3,
        **kwargs,
    ) -> List[str]:
        """
        Generate multiple prompt variations from a single palette.

        Creates variations by rotating emphasis across palette colours
        and varying descriptors.

        Args:
            colors: List of RGB tuples.
            n_variations: Number of variations to generate (default: 3).
            **kwargs: Additional arguments passed to generate().

        Returns:
            List of prompt strings.

        Example:
            >>> gen = PromptGenerator()
            >>> colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0)]
            >>> prompts = gen.generate_variation_prompts(colors, n_variations=3)
            >>> for i, p in enumerate(prompts):
            ...     print(f"Variation {i+1}: {p[:80]}...")
        """
        from .namer import ColorNamer

        namer = ColorNamer(vocabulary=self.vocabulary)
        variations = []

        for i in range(min(n_variations, len(colors))):
            # Emphasise colour i; give every other colour a small uniform base
            base = 0.1
            proportions = [base] * len(colors)
            proportions[i % len(colors)] = 1.0 - base * (len(colors) - 1)
            # Renormalise to sum to 1.0
            total = sum(proportions)
            proportions = [p / total for p in proportions]

            prompt = self.generate(colors, proportions=proportions, **kwargs)
            variations.append(prompt)

        return variations

    def palette_to_prompt_keywords(
        self,
        colors: List[Tuple[int, int, int]],
    ) -> List[str]:
        """
        Extract concise keyword descriptors from a palette.

        Useful for tagging or short-form prompts.

        Args:
            colors: List of RGB tuples.

        Returns:
            List of keyword strings.

        Example:
            >>> gen = PromptGenerator()
            >>> keywords = gen.palette_to_prompt_keywords([(255, 0, 0), (0, 0, 255)])
            >>> print(keywords)
            ['Cadmium Red Light', 'Prussian Blue', 'complementary', 'warm-cool contrast']
        """
        from .namer import ColorNamer
        from .analysis import ColorAnalyzer

        namer = ColorNamer(vocabulary=self.vocabulary)
        analyzer = ColorAnalyzer()

        keywords = []

        # Colour names
        for color in colors:
            keywords.append(namer.name(color))

        # Harmony type
        if len(colors) >= 2:
            harmony = analyzer.analyze_color_harmony(colors)
            dom = harmony["dominant_harmony"]
            if dom != "none":
                keywords.append(dom.replace("_", " "))

        # Temperature
        temp = analyzer.analyze_color_temperature_distribution(colors)
        dom_temp = temp["dominant_temperature"]
        warm_pct = temp["warm_percentage"]
        cool_pct = temp["cool_percentage"]

        if warm_pct > 60:
            keywords.append("warm palette")
        elif cool_pct > 60:
            keywords.append("cool palette")
        elif abs(warm_pct - cool_pct) < 20:
            keywords.append("warm-cool contrast")

        # Saturation
        sat = analyzer.calculate_saturation_score(colors)
        if sat > 70:
            keywords.append("vibrant")
        elif sat < 30:
            keywords.append("muted")

        return keywords
