"""
Tests for PromptGenerator class.

Test suite for GenAI colour prompt generation functionality.
"""

import pytest
from renoir.color import PromptGenerator


class TestPromptGeneratorInitialization:
    """Test PromptGenerator initialization."""

    def test_default_initialization(self):
        gen = PromptGenerator()
        assert gen.vocabulary == "artist"

    def test_custom_vocabulary(self):
        gen = PromptGenerator(vocabulary="xkcd")
        assert gen.vocabulary == "xkcd"


class TestPromptGeneration:
    """Test prompt generation."""

    @pytest.fixture
    def gen(self):
        return PromptGenerator()

    def test_generate_basic(self, gen):
        colors = [(255, 0, 0), (0, 0, 255)]
        prompt = gen.generate(colors)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_generate_with_style(self, gen):
        colors = [(255, 87, 51), (0, 50, 200)]
        prompt = gen.generate(colors, style="impressionist", medium="oil painting")
        assert "impressionist" in prompt.lower()
        assert "oil painting" in prompt.lower()

    def test_generate_with_mood(self, gen):
        colors = [(255, 0, 0)]
        prompt = gen.generate(colors, mood="dramatic")
        assert "dramatic" in prompt.lower()

    def test_generate_with_subject(self, gen):
        colors = [(255, 0, 0)]
        prompt = gen.generate(colors, subject="landscape")
        assert "Landscape" in prompt

    def test_generate_empty_palette(self, gen):
        prompt = gen.generate([])
        assert prompt == ""

    def test_generate_midjourney_target(self, gen):
        colors = [(255, 0, 0), (0, 255, 0)]
        prompt = gen.generate(colors, target_model="midjourney")
        assert "--v 6" in prompt

    def test_generate_stable_diffusion_target(self, gen):
        colors = [(255, 0, 0)]
        prompt = gen.generate(colors, target_model="stable_diffusion")
        assert "colour grading" in prompt.lower()

    def test_generate_with_proportions(self, gen):
        colors = [(255, 0, 0), (0, 0, 255)]
        prompt = gen.generate(colors, proportions=[0.8, 0.2])
        assert "80%" in prompt
        assert "20%" in prompt

    def test_generate_no_harmony(self, gen):
        colors = [(255, 0, 0), (0, 0, 255)]
        prompt = gen.generate(colors, include_harmony=False)
        assert isinstance(prompt, str)

    def test_generate_no_temperature(self, gen):
        colors = [(255, 0, 0)]
        prompt = gen.generate(colors, include_temperature=False)
        assert "temperature" not in prompt.lower()

    def test_generate_no_complexity(self, gen):
        colors = [(255, 0, 0), (0, 0, 255)]
        prompt = gen.generate(colors, include_complexity=False)
        assert "CCI" not in prompt


class TestVariationPrompts:
    """Test variation prompt generation."""

    def test_generate_variations(self):
        gen = PromptGenerator()
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        variations = gen.generate_variation_prompts(colors, n_variations=3)
        assert len(variations) == 3
        assert all(isinstance(v, str) for v in variations)
        # Variations should differ
        assert len(set(variations)) > 1

    def test_generate_variations_with_kwargs(self):
        gen = PromptGenerator()
        colors = [(255, 0, 0), (0, 0, 255)]
        variations = gen.generate_variation_prompts(
            colors, n_variations=2, style="abstract"
        )
        assert all("abstract" in v.lower() for v in variations)


class TestPaletteKeywords:
    """Test keyword extraction."""

    def test_keywords_basic(self):
        gen = PromptGenerator()
        keywords = gen.palette_to_prompt_keywords([(255, 0, 0), (0, 0, 255)])
        assert isinstance(keywords, list)
        assert len(keywords) >= 2  # At least the colour names

    def test_keywords_vibrant(self):
        gen = PromptGenerator()
        keywords = gen.palette_to_prompt_keywords(
            [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        )
        assert "vibrant" in keywords

    def test_keywords_muted(self):
        gen = PromptGenerator()
        keywords = gen.palette_to_prompt_keywords([(180, 170, 165), (160, 155, 150)])
        assert "muted" in keywords
