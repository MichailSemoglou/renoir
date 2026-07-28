"""
Generative AI color prompt module.

Converts renoir color analysis results into structured prompts for
generative AI image and video models (DALL-E, Midjourney, Stable Diffusion,
Runway, Sora). Bridges the gap between computational color analysis and
AI-assisted design workflows.
"""

from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

_CCI_LOW_THRESHOLD = 0.3
_CCI_MODERATE_THRESHOLD = 0.6
_WARM_PALETTE_THRESHOLD = 60
_COOL_PALETTE_THRESHOLD = 60
_WARM_COOL_CONTRAST_THRESHOLD = 20
_VIBRANT_SATURATION_THRESHOLD = 70
_MUTED_SATURATION_THRESHOLD = 30
_VARIATION_BASE_PROPORTION = 0.1
_MIDJOURNEY_SUFFIX = " --v 6"
_STABLE_DIFFUSION_SUFFIX = ", highly detailed, professional color grading"


class PromptGenerator:
    """
    Generate structured color prompts for generative AI models.

    Composes outputs from renoir's color analysis, naming, and harmony
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

    def __init__(self, vocabulary: str = "artist", namer=None, analyzer=None):
        """
        Initialize PromptGenerator.

        Args:
            vocabulary: Color naming vocabulary to use (default: 'artist').
            namer: Optional pre-configured ``ColorNamer`` instance.
                When ``None``, one is created lazily on first use.
            analyzer: Optional pre-configured ``ColorAnalyzer`` instance.
                When ``None``, one is created lazily on first use.
        """
        self.vocabulary = vocabulary
        self._namer = namer
        self._analyzer = analyzer

    def _get_namer(self):
        if self._namer is None:
            from .namer import ColorNamer

            self._namer = ColorNamer(vocabulary=self.vocabulary)
        return self._namer

    def _get_analyzer(self):
        if self._analyzer is None:
            from .analysis import ColorAnalyzer

            self._analyzer = ColorAnalyzer()
        return self._analyzer

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
        Generate a structured color prompt from a palette.

        Args:
            colors: List of RGB tuples (typically from ColorExtractor).
            proportions: Optional color proportions (should sum to 1.0).
                         If None, equal proportions are assumed.
            style: Optional art style descriptor (e.g. 'impressionist',
                   'minimalist', 'art deco').
            medium: Optional medium descriptor (e.g. 'oil painting',
                    'watercolor', 'digital illustration').
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
        if not colors:
            logger.warning(
                "generate() called with empty colors list; returning empty prompt"
            )
            return ""

        namer = self._get_namer()
        analyzer = self._get_analyzer()

        if proportions is None:
            proportions = [1.0 / len(colors)] * len(colors)

        named = []
        for color, prop in zip(colors, proportions):
            name = namer.name(color)
            pct = round(prop * 100)
            named.append((name, pct, color))

        named.sort(key=lambda x: x[1], reverse=True)

        parts = []

        opener = self._build_opener(subject, medium, style)
        if opener:
            parts.append(opener)

        palette_desc = "Color palette: " + ", ".join(
            f"{name} ({pct}%)" if pct > 0 else name for name, pct, _ in named
        )
        parts.append(palette_desc + ".")

        dominant_name, _, _ = named[0]
        parts.append(f"Dominant color: {dominant_name}.")

        if include_harmony and len(colors) >= 2:
            harmony = analyzer.analyze_color_harmony(colors)
            dominant_harmony = harmony["dominant_harmony"]
            if dominant_harmony != "none":
                harmony_desc = dominant_harmony.replace("_", " ")
                parts.append(f"Color harmony: {harmony_desc}.")

        if include_temperature:
            temp = analyzer.analyze_color_temperature_distribution(colors)
            parts.append(
                f"Color temperature: {temp['dominant_temperature']}-dominant "
                f"({temp['warm_percentage']:.0f}% warm, "
                f"{temp['cool_percentage']:.0f}% cool)."
            )

        if include_complexity and len(colors) >= 2:
            complexity_desc = self._describe_complexity(analyzer, colors, proportions)
            if complexity_desc:
                parts.append(complexity_desc)

        if mood:
            parts.append(f"Mood: {mood}.")

        prompt = " ".join(parts)
        return self._apply_model_suffixes(prompt, target_model)

    @staticmethod
    def _build_opener(
        subject: Optional[str],
        medium: Optional[str],
        style: Optional[str],
    ) -> Optional[str]:
        opener_parts = []
        if subject:
            opener_parts.append(subject.capitalize())
        if medium:
            opener_parts.append(medium)
        if style:
            opener_parts.append(f"in {style} style")
        return " ".join(opener_parts) + "." if opener_parts else None

    @staticmethod
    def _describe_complexity(analyzer, colors, proportions) -> Optional[str]:
        complexity = analyzer.calculate_color_complexity(colors, proportions)
        cci = complexity["cci"]
        if cci < _CCI_LOW_THRESHOLD:
            word = "Low"
        elif cci < _CCI_MODERATE_THRESHOLD:
            word = "Moderate"
        else:
            word = "High"
        return f"{word} color complexity (CCI: {cci:.2f})."

    @staticmethod
    def _apply_model_suffixes(prompt: str, target_model: str) -> str:
        if target_model == "midjourney":
            return prompt + _MIDJOURNEY_SUFFIX
        if target_model == "stable_diffusion":
            return prompt + _STABLE_DIFFUSION_SUFFIX
        return prompt

    def generate_variation_prompts(
        self,
        colors: List[Tuple[int, int, int]],
        n_variations: int = 3,
        **kwargs,
    ) -> List[str]:
        """
        Generate multiple prompt variations from a single palette.

        Creates variations by rotating emphasis across palette colors
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
        variations = []

        for i in range(min(n_variations, len(colors))):
            base = _VARIATION_BASE_PROPORTION
            proportions = [base] * len(colors)
            proportions[i % len(colors)] = 1.0 - base * (len(colors) - 1)
            # Renormalize to sum to 1.0
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
        if not colors:
            logger.warning("palette_to_prompt_keywords() called with empty colors list")
            return []

        namer = self._get_namer()
        analyzer = self._get_analyzer()

        keywords = []

        # Color names
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

        if warm_pct > _WARM_PALETTE_THRESHOLD:
            keywords.append("warm palette")
        elif cool_pct > _COOL_PALETTE_THRESHOLD:
            keywords.append("cool palette")
        elif abs(warm_pct - cool_pct) < _WARM_COOL_CONTRAST_THRESHOLD:
            keywords.append("warm-cool contrast")

        # Saturation
        sat = analyzer.calculate_saturation_score(colors)
        if sat > _VIBRANT_SATURATION_THRESHOLD:
            keywords.append("vibrant")
        elif sat < _MUTED_SATURATION_THRESHOLD:
            keywords.append("muted")

        return keywords
