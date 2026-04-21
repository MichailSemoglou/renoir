"""
Color analysis functions for statistical and color space analysis.

This module provides tools for analyzing color distributions, converting
between color spaces, and computing color statistics from artworks.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from collections import Counter
import colorsys

try:
    from scipy.optimize import linear_sum_assignment

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class ColorAnalyzer:
    """
    Analyze color distributions and relationships in artworks.

    This class provides methods for statistical analysis of colors,
    color space conversions, and comparative analysis across artworks.
    Designed for teaching color theory and computational analysis to
    art and design students.
    """

    def __init__(self):
        """Initialize the ColorAnalyzer."""
        pass

    def rgb_to_hsv(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Convert RGB color to HSV (Hue, Saturation, Value) color space.

        HSV is often more intuitive for artists and designers as it
        separates color into hue (color type), saturation (intensity),
        and value (brightness).

        Args:
            rgb: Tuple of (R, G, B) values (0-255)

        Returns:
            Tuple of (H, S, V) where:
                H: Hue in degrees (0-360)
                S: Saturation as percentage (0-100)
                V: Value as percentage (0-100)

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> hsv = analyzer.rgb_to_hsv((255, 87, 51))
            >>> print(f"Hue: {hsv[0]}°, Saturation: {hsv[1]}%, Value: {hsv[2]}%")
        """
        # Normalize RGB to 0-1
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0

        # Convert using colorsys
        h, s, v = colorsys.rgb_to_hsv(r, g, b)

        # Convert to standard ranges
        return (h * 360, s * 100, v * 100)

    def hsv_to_rgb(self, hsv: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """
        Convert HSV color to RGB color space.

        Args:
            hsv: Tuple of (H, S, V) where:
                H: Hue in degrees (0-360)
                S: Saturation as percentage (0-100)
                V: Value as percentage (0-100)

        Returns:
            Tuple of (R, G, B) values (0-255)

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> rgb = analyzer.hsv_to_rgb((10, 80, 100))
            >>> print(f"RGB: {rgb}")
        """
        # Normalize to 0-1
        h, s, v = hsv[0] / 360.0, hsv[1] / 100.0, hsv[2] / 100.0

        # Convert using colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        # Convert to 0-255 range
        return (int(r * 255), int(g * 255), int(b * 255))

    def rgb_to_hsl(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Convert RGB color to HSL (Hue, Saturation, Lightness) color space.

        Args:
            rgb: Tuple of (R, G, B) values (0-255)

        Returns:
            Tuple of (H, S, L) where:
                H: Hue in degrees (0-360)
                S: Saturation as percentage (0-100)
                L: Lightness as percentage (0-100)
        """
        # Normalize RGB to 0-1
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0

        # Convert using colorsys
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        # Convert to standard ranges
        return (h * 360, s * 100, l * 100)

    def hsl_to_rgb(self, hsl: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """
        Convert HSL color to RGB.

        Args:
            hsl: Tuple of (H, S, L) where:
                H: Hue in degrees (0-360)
                S: Saturation as percentage (0-100)
                L: Lightness as percentage (0-100)

        Returns:
            Tuple of (R, G, B) values (0-255)
        """
        # Validate input
        if not isinstance(hsl, (tuple, list)) or len(hsl) != 3:
            raise ValueError("HSL must be a tuple of 3 values")

        h, s, l = hsl
        if not (0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100):
            raise ValueError("H must be 0-360, S and L must be 0-100")

        # Normalize to 0-1 range
        h = h / 360.0
        s = s / 100.0
        l = l / 100.0

        # Convert using colorsys
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Scale to 0-255
        return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))

    def analyze_palette_statistics(self, colors: List[Tuple[int, int, int]]) -> Dict:
        """
        Compute statistical measures for a color palette.

        Educational method for teaching students about color data analysis.

        Args:
            colors: List of RGB tuples

        Returns:
            Dictionary containing:
                - mean_rgb: Average RGB values
                - std_rgb: Standard deviation of RGB values
                - hsv_values: HSV representation of each color
                - mean_hue: Average hue
                - mean_saturation: Average saturation
                - mean_value: Average brightness/value

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> colors = [(255, 87, 51), (100, 200, 150), (50, 100, 200)]
            >>> stats = analyzer.analyze_palette_statistics(colors)
            >>> print(f"Average hue: {stats['mean_hue']:.1f}°")
        """
        if not colors:
            return {}

        # Convert to numpy array for easy calculation
        rgb_array = np.array(colors)

        # RGB statistics
        mean_rgb = tuple(np.mean(rgb_array, axis=0).astype(int))
        std_rgb = tuple(np.std(rgb_array, axis=0).astype(int))

        # Convert to HSV for color-space statistics
        hsv_values = [self.rgb_to_hsv(color) for color in colors]
        hsv_array = np.array(hsv_values)

        # Handle circular mean for hue (0-360 degrees)
        hues_rad = np.radians(hsv_array[:, 0])
        mean_hue_rad = np.arctan2(np.mean(np.sin(hues_rad)), np.mean(np.cos(hues_rad)))
        mean_hue = np.degrees(mean_hue_rad) % 360

        stats = {
            "n_colors": len(colors),
            "mean_rgb": mean_rgb,
            "std_rgb": std_rgb,
            "hsv_values": hsv_values,
            "mean_hue": float(mean_hue),
            "mean_saturation": float(np.mean(hsv_array[:, 1])),
            "mean_value": float(np.mean(hsv_array[:, 2])),
            "std_hue": float(np.std(hsv_array[:, 0])),
            "std_saturation": float(np.std(hsv_array[:, 1])),
            "std_value": float(np.std(hsv_array[:, 2])),
        }

        return stats

    def calculate_color_diversity(self, colors: List[Tuple[int, int, int]]) -> float:
        """
        Calculate color diversity using hue distribution entropy.

        Higher values indicate more diverse color usage.
        Useful for comparing artistic styles quantitatively.

        Args:
            colors: List of RGB tuples

        Returns:
            Diversity score (0-1, higher = more diverse)

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> monochrome = [(100, 100, 100), (110, 110, 110), (120, 120, 120)]
            >>> diverse = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            >>> print(analyzer.calculate_color_diversity(monochrome))  # Low score
            >>> print(analyzer.calculate_color_diversity(diverse))     # High score
        """
        if len(colors) < 2:
            return 0.0

        # Convert to HSV
        hsv_values = [self.rgb_to_hsv(color) for color in colors]

        # Get hue values (0-360)
        hues = [hsv[0] for hsv in hsv_values]

        # Bin hues into 12 categories (like a color wheel)
        bins = np.linspace(0, 360, 13)
        hist, _ = np.histogram(hues, bins=bins)

        # Calculate Shannon entropy
        hist = hist / hist.sum()
        hist = hist[hist > 0]  # Remove zero bins
        entropy = -np.sum(hist * np.log2(hist))

        # Normalize to 0-1 (max entropy for 12 bins is log2(12))
        max_entropy = np.log2(12)
        diversity = entropy / max_entropy

        return float(diversity)

    def calculate_saturation_score(self, colors: List[Tuple[int, int, int]]) -> float:
        """
        Calculate average saturation score for a palette.

        Useful for characterizing artistic styles:
        - High saturation: Bold, vibrant (Fauvism, Pop Art)
        - Low saturation: Muted, subtle (Impressionism, Realism)

        Args:
            colors: List of RGB tuples

        Returns:
            Average saturation (0-100)

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> vibrant = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            >>> muted = [(200, 180, 170), (150, 140, 130)]
            >>> print(analyzer.calculate_saturation_score(vibrant))  # ~100
            >>> print(analyzer.calculate_saturation_score(muted))    # ~20
        """
        if not colors:
            return 0.0

        hsv_values = [self.rgb_to_hsv(color) for color in colors]
        saturations = [hsv[1] for hsv in hsv_values]

        return float(np.mean(saturations))

    def calculate_brightness_score(self, colors: List[Tuple[int, int, int]]) -> float:
        """
        Calculate average brightness/value score for a palette.

        Args:
            colors: List of RGB tuples

        Returns:
            Average brightness (0-100)
        """
        if not colors:
            return 0.0

        hsv_values = [self.rgb_to_hsv(color) for color in colors]
        values = [hsv[2] for hsv in hsv_values]

        return float(np.mean(values))

    def compare_palettes(
        self, palette1: List[Tuple[int, int, int]], palette2: List[Tuple[int, int, int]]
    ) -> Dict:
        """
        Compare two color palettes statistically.

        Educational method for teaching comparative color analysis.

        Args:
            palette1: First list of RGB tuples
            palette2: Second list of RGB tuples

        Returns:
            Dictionary with comparative statistics

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> monet_colors = [(120, 150, 180), (200, 220, 230)]
            >>> picasso_colors = [(255, 50, 50), (50, 50, 200)]
            >>> comparison = analyzer.compare_palettes(monet_colors, picasso_colors)
            >>> print(f"Saturation difference: {comparison['saturation_diff']:.1f}%")
        """
        stats1 = self.analyze_palette_statistics(palette1)
        stats2 = self.analyze_palette_statistics(palette2)

        comparison = {
            "palette1_stats": stats1,
            "palette2_stats": stats2,
            "hue_diff": abs(stats1["mean_hue"] - stats2["mean_hue"]),
            "saturation_diff": abs(
                stats1["mean_saturation"] - stats2["mean_saturation"]
            ),
            "brightness_diff": abs(stats1["mean_value"] - stats2["mean_value"]),
            "diversity_diff": abs(
                self.calculate_color_diversity(palette1)
                - self.calculate_color_diversity(palette2)
            ),
        }

        return comparison

    def classify_color_temperature(self, rgb: Tuple[int, int, int]) -> str:
        """
        Classify a color as warm or cool based on hue.

        Educational method for teaching color theory concepts.

        Args:
            rgb: RGB tuple

        Returns:
            'warm', 'cool', or 'neutral'

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> print(analyzer.classify_color_temperature((255, 0, 0)))    # 'warm'
            >>> print(analyzer.classify_color_temperature((0, 0, 255)))    # 'cool'
            >>> print(analyzer.classify_color_temperature((128, 128, 128))) # 'neutral'
        """
        hsv = self.rgb_to_hsv(rgb)
        hue = hsv[0]
        saturation = hsv[1]

        # Low saturation colors are neutral
        if saturation < 10:
            return "neutral"

        # Warm: red-orange-yellow (0-60 and 300-360)
        # Cool: green-blue-purple (120-300)
        if (hue >= 0 and hue <= 60) or (hue >= 300 and hue <= 360):
            return "warm"
        elif hue >= 120 and hue <= 300:
            return "cool"
        else:
            return "neutral"

    def analyze_color_temperature_distribution(
        self, colors: List[Tuple[int, int, int]]
    ) -> Dict:
        """
        Analyze the distribution of warm vs. cool colors in a palette.

        Args:
            colors: List of RGB tuples

        Returns:
            Dictionary with temperature distribution statistics

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)]
            >>> temp_dist = analyzer.analyze_color_temperature_distribution(colors)
            >>> print(temp_dist)
        """
        temperatures = [self.classify_color_temperature(color) for color in colors]
        temp_counts = Counter(temperatures)

        total = len(colors)

        return {
            "warm_count": temp_counts["warm"],
            "cool_count": temp_counts["cool"],
            "neutral_count": temp_counts["neutral"],
            "warm_percentage": (temp_counts["warm"] / total) * 100,
            "cool_percentage": (temp_counts["cool"] / total) * 100,
            "neutral_percentage": (temp_counts["neutral"] / total) * 100,
            "dominant_temperature": (
                temp_counts.most_common(1)[0][0] if temp_counts else "none"
            ),
        }

    def detect_complementary_colors(
        self, colors: List[Tuple[int, int, int]], tolerance: float = 30
    ) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]]:
        """
        Detect complementary color pairs in a palette.

        Complementary colors are opposite on the color wheel (180° apart).
        Educational method for teaching color harmony.

        Args:
            colors: List of RGB tuples
            tolerance: Hue difference tolerance in degrees (default: 30)

        Returns:
            List of complementary color pairs

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> colors = [(255, 0, 0), (0, 255, 255), (128, 0, 128)]
            >>> pairs = analyzer.detect_complementary_colors(colors)
        """
        complementary_pairs = []

        # Convert all to HSV
        hsv_colors = [(color, self.rgb_to_hsv(color)) for color in colors]

        # Check each pair
        for i, (color1, hsv1) in enumerate(hsv_colors):
            for color2, hsv2 in hsv_colors[i + 1 :]:
                hue_diff = abs(hsv1[0] - hsv2[0])

                # Account for circular nature of hue
                if hue_diff > 180:
                    hue_diff = 360 - hue_diff

                # Check if approximately 180° apart
                if abs(hue_diff - 180) <= tolerance:
                    complementary_pairs.append((color1, color2))

        return complementary_pairs

    def calculate_contrast_ratio(
        self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]
    ) -> float:
        """
        Calculate WCAG contrast ratio between two colors.

        Useful for teaching accessibility in design.
        Ratio of 4.5:1 is minimum for normal text (WCAG AA).

        Args:
            color1: First RGB tuple
            color2: Second RGB tuple

        Returns:
            Contrast ratio (1-21)

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> ratio = analyzer.calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
            >>> print(f"Contrast ratio: {ratio:.2f}:1")  # 21.00:1
        """

        def relative_luminance(rgb):
            """Calculate relative luminance for contrast."""
            r, g, b = [x / 255.0 for x in rgb]

            # Apply gamma correction
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = relative_luminance(color1)
        l2 = relative_luminance(color2)

        # Ensure l1 is the lighter color
        if l2 > l1:
            l1, l2 = l2, l1

        ratio = (l1 + 0.05) / (l2 + 0.05)

        return float(ratio)

    def detect_triadic_harmony(
        self, colors: List[Tuple[int, int, int]], tolerance: float = 30
    ) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]]:
        """
        Detect triadic color harmonies in a palette.

        Triadic harmonies are three colors equally spaced on the color wheel
        (120° apart). Used by masters like Mondrian and in vibrant designs.

        Args:
            colors: List of RGB tuples
            tolerance: Hue difference tolerance in degrees (default: 30)

        Returns:
            List of triadic color triplets

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # R, G, B
            >>> triads = analyzer.detect_triadic_harmony(colors)
            >>> print(f"Found {len(triads)} triadic harmonies")
        """
        triadic_sets = []

        # Convert all to HSV
        hsv_colors = [(color, self.rgb_to_hsv(color)) for color in colors]

        # Check each triplet
        for i, (color1, hsv1) in enumerate(hsv_colors):
            for j, (color2, hsv2) in enumerate(hsv_colors[i + 1 :], i + 1):
                for color3, hsv3 in hsv_colors[j + 1 :]:
                    # Calculate hue differences
                    diff1 = abs(hsv1[0] - hsv2[0])
                    diff2 = abs(hsv2[0] - hsv3[0])
                    diff3 = abs(hsv3[0] - hsv1[0])

                    # Normalize to 0-180 range (account for circular nature)
                    diffs = []
                    for diff in [diff1, diff2, diff3]:
                        if diff > 180:
                            diff = 360 - diff
                        diffs.append(diff)

                    # Check if all approximately 120° apart
                    if all(abs(d - 120) <= tolerance for d in diffs):
                        triadic_sets.append((color1, color2, color3))

        return triadic_sets

    def detect_analogous_harmony(
        self, colors: List[Tuple[int, int, int]], max_hue_range: float = 60
    ) -> List[List[Tuple[int, int, int]]]:
        """
        Detect analogous color schemes in a palette.

        Analogous colors are adjacent on the color wheel (within 60° typically).
        Creates harmonious, serene color schemes. Common in nature and landscapes.

        Args:
            colors: List of RGB tuples
            max_hue_range: Maximum hue range in degrees (default: 60)

        Returns:
            List of analogous color groups (groups of 2+ colors)

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> # Blues and greens (analogous)
            >>> colors = [(0, 100, 255), (0, 200, 200), (0, 255, 100)]
            >>> groups = analyzer.detect_analogous_harmony(colors)
        """
        if len(colors) < 2:
            return []

        # Convert to HSV and sort by hue
        hsv_colors = [(color, self.rgb_to_hsv(color)) for color in colors]
        hsv_colors.sort(key=lambda x: x[1][0])  # Sort by hue

        analogous_groups = []
        current_group = [hsv_colors[0][0]]
        base_hue = hsv_colors[0][1][0]

        for color, hsv in hsv_colors[1:]:
            hue = hsv[0]
            hue_diff = abs(hue - base_hue)

            # Account for circular nature (e.g., 350° and 10° are close)
            if hue_diff > 180:
                hue_diff = 360 - hue_diff

            if hue_diff <= max_hue_range:
                current_group.append(color)
            else:
                if len(current_group) >= 2:
                    analogous_groups.append(current_group)
                current_group = [color]
                base_hue = hue

        # Add last group if valid
        if len(current_group) >= 2:
            analogous_groups.append(current_group)

        return analogous_groups

    def detect_split_complementary(
        self, colors: List[Tuple[int, int, int]], tolerance: float = 30
    ) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]]:
        """
        Detect split-complementary color schemes.

        Split-complementary uses a base color and two colors adjacent to its
        complement (instead of the direct complement). Provides high contrast
        while being more subtle than complementary. Popular in Renaissance art.

        Args:
            colors: List of RGB tuples
            tolerance: Hue difference tolerance in degrees (default: 30)

        Returns:
            List of split-complementary triplets (base, complement1, complement2)

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> # Red with blue-green and yellow-green (instead of pure green)
            >>> colors = [(255, 0, 0), (0, 200, 100), (100, 200, 0)]
            >>> splits = analyzer.detect_split_complementary(colors)
        """
        split_comp_sets = []

        # Convert all to HSV
        hsv_colors = [(color, self.rgb_to_hsv(color)) for color in colors]

        # For each color, look for two colors ~150° and ~210° away (or ±150°)
        for i, (base_color, base_hsv) in enumerate(hsv_colors):
            base_hue = base_hsv[0]
            complement_hue = (base_hue + 180) % 360

            # Look for colors 30° on either side of complement
            target_hue1 = (complement_hue - 30) % 360
            target_hue2 = (complement_hue + 30) % 360

            candidates1 = []
            candidates2 = []

            for j, (color, hsv) in enumerate(hsv_colors):
                if i == j:
                    continue

                hue = hsv[0]

                # Check against target_hue1
                diff1 = abs(hue - target_hue1)
                if diff1 > 180:
                    diff1 = 360 - diff1
                if diff1 <= tolerance:
                    candidates1.append((color, hsv))

                # Check against target_hue2
                diff2 = abs(hue - target_hue2)
                if diff2 > 180:
                    diff2 = 360 - diff2
                if diff2 <= tolerance:
                    candidates2.append((color, hsv))

            # Create triplets
            for color1, _ in candidates1:
                for color2, _ in candidates2:
                    if color1 != color2:
                        split_comp_sets.append((base_color, color1, color2))

        return split_comp_sets

    def detect_tetradic_harmony(
        self, colors: List[Tuple[int, int, int]], tolerance: float = 30
    ) -> List[
        Tuple[
            Tuple[int, int, int],
            Tuple[int, int, int],
            Tuple[int, int, int],
            Tuple[int, int, int],
        ]
    ]:
        """
        Detect tetradic (double complementary) color harmonies.

        Tetradic uses two complementary pairs, forming a rectangle on the
        color wheel. Creates rich, diverse palettes. Used in complex
        compositions and modern art.

        Args:
            colors: List of RGB tuples
            tolerance: Hue difference tolerance in degrees (default: 30)

        Returns:
            List of tetradic color quartets

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> # Two complementary pairs
            >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            >>> tetrads = analyzer.detect_tetradic_harmony(colors)
        """
        tetradic_sets = []

        if len(colors) < 4:
            return []

        # Convert all to HSV
        hsv_colors = [(color, self.rgb_to_hsv(color)) for color in colors]

        # Check each quartet
        for i, (c1, hsv1) in enumerate(hsv_colors):
            for j, (c2, hsv2) in enumerate(hsv_colors[i + 1 :], i + 1):
                for k, (c3, hsv3) in enumerate(hsv_colors[j + 1 :], j + 1):
                    for c4, hsv4 in hsv_colors[k + 1 :]:
                        # Get all hues
                        hues = sorted([hsv1[0], hsv2[0], hsv3[0], hsv4[0]])

                        # Calculate differences between consecutive hues
                        diffs = []
                        for idx in range(4):
                            diff = hues[(idx + 1) % 4] - hues[idx]
                            if idx == 3:  # Last to first
                                diff = (hues[0] + 360) - hues[3]
                            diffs.append(diff)

                        # For tetradic: should have two pairs of equal angles
                        # (rectangle on color wheel)
                        diffs_sorted = sorted(diffs)
                        if (
                            abs(diffs_sorted[0] - diffs_sorted[1]) <= tolerance
                            and abs(diffs_sorted[2] - diffs_sorted[3]) <= tolerance
                        ):
                            tetradic_sets.append((c1, c2, c3, c4))

        return tetradic_sets

    def analyze_color_harmony(
        self, colors: List[Tuple[int, int, int]]
    ) -> Dict[str, any]:
        """
        Comprehensive analysis of color harmonies present in a palette.

        Analyzes all major harmony types and provides statistics.
        Educational method for teaching color theory in practice.

        Args:
            colors: List of RGB tuples

        Returns:
            Dictionary containing:
                - complementary_pairs: List of complementary color pairs
                - triadic_sets: List of triadic harmonies
                - analogous_groups: List of analogous color groups
                - split_complementary_sets: List of split-complementary schemes
                - tetradic_sets: List of tetradic harmonies
                - harmony_score: Overall harmony score (0-1)
                - dominant_harmony: Most prevalent harmony type

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            >>> analysis = analyzer.analyze_color_harmony(colors)
            >>> print(f"Dominant harmony: {analysis['dominant_harmony']}")
        """
        # Detect all harmony types
        complementary = self.detect_complementary_colors(colors)
        triadic = self.detect_triadic_harmony(colors)
        analogous = self.detect_analogous_harmony(colors)
        split_comp = self.detect_split_complementary(colors)
        tetradic = self.detect_tetradic_harmony(colors)

        # Count harmonies
        harmony_counts = {
            "complementary": len(complementary),
            "triadic": len(triadic),
            "analogous": len(analogous),
            "split_complementary": len(split_comp),
            "tetradic": len(tetradic),
        }

        # Determine dominant harmony
        dominant = max(harmony_counts, key=harmony_counts.get)
        if harmony_counts[dominant] == 0:
            dominant = "none"

        # Calculate harmony score (normalized by palette size)
        total_harmonies = sum(harmony_counts.values())
        max_possible = len(colors) * (len(colors) - 1) // 2  # Combinations
        harmony_score = min(
            1.0, total_harmonies / max_possible if max_possible > 0 else 0
        )

        return {
            "complementary_pairs": complementary,
            "triadic_sets": triadic,
            "analogous_groups": analogous,
            "split_complementary_sets": split_comp,
            "tetradic_sets": tetradic,
            "harmony_counts": harmony_counts,
            "total_harmonies": total_harmonies,
            "harmony_score": harmony_score,
            "dominant_harmony": dominant,
        }

    def _get_namer(self):
        """Lazy-load a ColorNamer instance for CIEDE2000 calculations."""
        if not hasattr(self, "_namer"):
            from .namer import ColorNamer

            self._namer = ColorNamer()
        return self._namer

    def palette_earth_movers_distance(
        self,
        palette1: List[Tuple[Tuple[int, int, int], float]],
        palette2: List[Tuple[Tuple[int, int, int], float]],
    ) -> float:
        """
        Calculate Palette Earth Mover's Distance (PEMD) between two palettes.

        Uses CIEDE2000 as the perceptual ground distance and colour proportions
        as weights, solved via optimal transport. This provides a structurally
        aware comparison that accounts for both colour similarity and proportion
        differences.

        Args:
            palette1: List of (RGB tuple, proportion) pairs.
                      Proportions should sum to 1.0.
            palette2: List of (RGB tuple, proportion) pairs.
                      Proportions should sum to 1.0.

        Returns:
            PEMD distance (lower = more similar). Scale depends on CIEDE2000
            units (typically 0–100+, where <2 is imperceptible).

        Raises:
            ImportError: If scipy is not installed.
            ValueError: If palettes are empty.

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> p1 = [((255, 0, 0), 0.6), ((0, 0, 255), 0.4)]
            >>> p2 = [((250, 10, 5), 0.5), ((10, 0, 250), 0.5)]
            >>> dist = analyzer.palette_earth_movers_distance(p1, p2)
            >>> print(f"PEMD: {dist:.2f}")
        """
        if not SCIPY_AVAILABLE:
            raise ImportError(
                "scipy is required for PEMD. Install with: pip install scipy"
            )

        if not palette1 or not palette2:
            raise ValueError("Both palettes must be non-empty")

        namer = self._get_namer()
        n = len(palette1)
        m = len(palette2)

        # Build cost matrix using CIEDE2000
        cost_matrix = np.zeros((n, m))
        for i, (c1, _) in enumerate(palette1):
            lab1 = namer._rgb_to_lab(c1)
            for j, (c2, _) in enumerate(palette2):
                lab2 = namer._rgb_to_lab(c2)
                cost_matrix[i, j] = namer._ciede2000(lab1, lab2)

        # Extract weights
        w1 = np.array([w for _, w in palette1], dtype=float)
        w2 = np.array([w for _, w in palette2], dtype=float)

        # Normalise weights
        w1 = w1 / w1.sum()
        w2 = w2 / w2.sum()

        # Expand to balanced assignment problem:
        # Discretise weights into N units using largest-remainder method so
        # totals are guaranteed equal and no positive weight is zeroed out.
        resolution = max(n, m) * 10  # granularity

        def _largest_remainder(weights: np.ndarray, total: int) -> np.ndarray:
            raw = weights * total
            floors = np.floor(raw).astype(int)
            # Guarantee at least 1 unit for every positive weight
            floors = np.where((weights > 0) & (floors == 0), 1, floors)
            remainder = total - floors.sum()
            if remainder > 0:
                fracs = raw - np.floor(raw)
                # Indices sorted by descending fractional part
                order = np.argsort(-fracs)
                for idx in order[:remainder]:
                    floors[idx] += 1
            elif remainder < 0:
                # Over-allocated (can happen when forced minimums push sum above total)
                fracs = raw - np.floor(raw)
                order = np.argsort(fracs)  # smallest fracs donated first
                for idx in order[:-remainder]:
                    if floors[idx] > 1:
                        floors[idx] -= 1
            return floors

        counts1 = _largest_remainder(w1, resolution)
        counts2 = _largest_remainder(w2, resolution)

        # Ensure the two totals agree (off-by-one possible when forced minimums kick in)
        diff = int(counts1.sum()) - int(counts2.sum())
        if diff > 0:
            counts2[np.argmax(w2)] += diff
        elif diff < 0:
            counts1[np.argmax(w1)] += -diff

        total = int(counts1.sum())
        if total == 0:
            return 0.0

        # Build expanded cost matrix
        expanded_cost = np.zeros((total, total))
        row_idx = 0
        for i, c1_count in enumerate(counts1):
            col_idx = 0
            for j, c2_count in enumerate(counts2):
                expanded_cost[
                    row_idx : row_idx + c1_count, col_idx : col_idx + c2_count
                ] = cost_matrix[i, j]
                col_idx += c2_count
            row_idx += c1_count

        row_ind, col_ind = linear_sum_assignment(expanded_cost)
        return float(expanded_cost[row_ind, col_ind].sum() / total)

    def calculate_color_complexity(
        self,
        colors: List[Tuple[int, int, int]],
        proportions: Optional[List[float]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict:
        """
        Calculate the Colour Complexity Index (CCI) for a palette.

        A multi-dimensional information-theoretic measure combining:
        - Hue entropy (spread across the colour wheel)
        - Perceptual spread (mean pairwise CIEDE2000 distance)
        - Proportion evenness (1 - Gini coefficient)
        - Harmony penalty (lower complexity if colours follow harmony rules)

        Args:
            colors: List of RGB tuples
            proportions: Optional list of colour proportions (should sum to 1).
                         If None, equal proportions are assumed.
            weights: Optional dict of component weights with keys:
                     'hue_entropy', 'perceptual_spread', 'proportion_evenness',
                     'harmony_penalty'. Defaults to equal weighting.

        Returns:
            Dictionary containing:
                - cci: Composite Colour Complexity Index (0-1)
                - hue_entropy: Normalised hue entropy (0-1)
                - perceptual_spread: Normalised mean pairwise CIEDE2000 (0-1)
                - proportion_evenness: 1 - Gini coefficient (0-1)
                - harmony_penalty: Harmony score (0-1, subtracted)
                - components: Dict of weighted sub-scores

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> mondrian = [(255, 0, 0), (0, 0, 255), (255, 255, 0),
            ...             (255, 255, 255), (0, 0, 0)]
            >>> result = analyzer.calculate_color_complexity(mondrian)
            >>> print(f"CCI: {result['cci']:.3f}")
        """
        if len(colors) < 2:
            return {
                "cci": 0.0,
                "hue_entropy": 0.0,
                "perceptual_spread": 0.0,
                "proportion_evenness": 0.0,
                "harmony_penalty": 0.0,
                "components": {},
            }

        default_weights = {
            "hue_entropy": 0.3,
            "perceptual_spread": 0.3,
            "proportion_evenness": 0.2,
            "harmony_penalty": 0.2,
        }
        w = weights if weights else default_weights

        # 1. Hue entropy (reuse existing method, already normalised 0–1)
        hue_entropy = self.calculate_color_diversity(colors)

        # 2. Perceptual spread: mean pairwise CIEDE2000, normalised
        namer = self._get_namer()
        labs = [namer._rgb_to_lab(c) for c in colors]
        distances = []
        for i in range(len(labs)):
            for j in range(i + 1, len(labs)):
                distances.append(namer._ciede2000(labs[i], labs[j]))

        mean_distance = float(np.mean(distances)) if distances else 0.0
        # Normalise: CIEDE2000 of 100 is extreme; cap at 100
        perceptual_spread = min(1.0, mean_distance / 100.0)

        # 3. Proportion evenness (1 - Gini coefficient)
        if proportions is None:
            proportions = [1.0 / len(colors)] * len(colors)
        props = np.array(sorted(proportions), dtype=float)
        n = len(props)
        if props.sum() == 0:
            gini = 0.0
        else:
            index = np.arange(1, n + 1)
            gini = (2 * np.sum(index * props) - (n + 1) * np.sum(props)) / (
                n * np.sum(props)
            )
        proportion_evenness = 1.0 - gini

        # 4. Harmony penalty
        harmony = self.analyze_color_harmony(colors)
        harmony_score = harmony["harmony_score"]

        # Composite CCI
        cci = (
            w.get("hue_entropy", 0.3) * hue_entropy
            + w.get("perceptual_spread", 0.3) * perceptual_spread
            + w.get("proportion_evenness", 0.2) * proportion_evenness
            - w.get("harmony_penalty", 0.2) * harmony_score
        )
        cci = max(0.0, min(1.0, cci))

        return {
            "cci": float(cci),
            "hue_entropy": float(hue_entropy),
            "perceptual_spread": float(perceptual_spread),
            "proportion_evenness": float(proportion_evenness),
            "harmony_penalty": float(harmony_score),
            "components": {
                "hue_entropy_weighted": float(w.get("hue_entropy", 0.3) * hue_entropy),
                "perceptual_spread_weighted": float(
                    w.get("perceptual_spread", 0.3) * perceptual_spread
                ),
                "proportion_evenness_weighted": float(
                    w.get("proportion_evenness", 0.2) * proportion_evenness
                ),
                "harmony_penalty_weighted": float(
                    w.get("harmony_penalty", 0.2) * harmony_score
                ),
            },
        }

    def colour_provenance_score(
        self,
        colors: List[Tuple[int, int, int]],
        year: int,
        proportions: Optional[List[float]] = None,
    ) -> Dict:
        """
        Calculate Colour Provenance Score (CPS) for a palette and attributed date.

        Estimates how consistent a palette is with historically available pigments
        at the given date. Low scores may indicate anachronistic colour usage.

        Requires the artist_pigments vocabulary with historical date fields.

        Args:
            colors: List of RGB tuples from the artwork
            year: Attributed year of the artwork
            proportions: Optional colour proportions. If None, equal weights used.

        Returns:
            Dictionary containing:
                - score: Overall provenance score (0–1, higher = more consistent)
                - per_color: List of per-colour assessments
                - flagged: Colours flagged as potentially anachronistic

        Example:
            >>> analyzer = ColorAnalyzer()
            >>> colors = [(0, 50, 200), (255, 0, 0), (255, 255, 0)]
            >>> result = analyzer.colour_provenance_score(colors, year=1780)
            >>> print(f"Provenance: {result['score']:.2f}")
            >>> for flag in result['flagged']:
            ...     print(f"  ⚠ {flag['color']}: {flag['reason']}")
        """
        from .namer import ColorNamer

        namer = ColorNamer(vocabulary="artist")

        if not colors:
            raise ValueError("colors must not be empty")

        if proportions is None:
            proportions = [1.0 / len(colors)] * len(colors)

        if len(proportions) != len(colors):
            raise ValueError(
                f"proportions length ({len(proportions)}) must match "
                f"colors length ({len(colors)})"
            )

        per_color = []
        flagged = []

        for i, (color, weight) in enumerate(zip(colors, proportions)):
            result = namer.historical_pigment_probability(color, year)

            # Best match probability
            best = result[0] if result else None
            prob = best["probability"] if best else 0.0

            entry = {
                "color": color,
                "weight": weight,
                "probability": prob,
                "best_pigment": best["name"] if best else "Unknown",
                "available_pigments": len(result),
            }
            per_color.append(entry)

            # Flag if no pigments available or very low probability
            if prob < 0.1:
                flagged.append(
                    {
                        "color": color,
                        "reason": (
                            f"No historically plausible pigment match for year {year}. "
                            f"Best match: {best['name']} (prob: {prob:.3f})"
                            if best
                            else f"No pigments available for year {year}"
                        ),
                    }
                )

        # Weighted overall score
        total_weight = sum(proportions)
        if total_weight > 0:
            score = (
                sum(e["probability"] * e["weight"] for e in per_color) / total_weight
            )
        else:
            score = 0.0

        return {
            "score": float(score),
            "year": year,
            "per_color": per_color,
            "flagged": flagged,
        }
