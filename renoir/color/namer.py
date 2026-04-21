"""
Color naming module for evocative, artist-friendly color identification.

This module provides tools for converting RGB/hex colors to memorable,
evocative names like "Burnt Sienna" or "Prussian Blue" rather than
technical codes. Uses perceptually accurate color matching (CIEDE2000).
"""

import json
import os
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import numpy as np


class ColorNamer:
    """
    Convert colors to evocative, artist-friendly names.

    This class provides paint manufacturer-style color naming using
    perceptually accurate color matching. Supports multiple naming
    vocabularies from traditional artist pigments to modern design colors.

    Attributes:
        vocabulary: Currently active color vocabulary
        _colors: Cached color data for current vocabulary
        _lab_cache: Cache of Lab color space conversions

    Example:
        >>> from renoir.color import ColorNamer
        >>> namer = ColorNamer(vocabulary="artist")
        >>> result = namer.name((255, 87, 51))
        >>> print(result['name'])
        'Cadmium Orange'
    """

    # Class-level vocabulary registry
    _VOCABULARIES = {
        "artist": "artist_pigments.json",
        "resene": "resene.json",
        "natural": "werner.json",
        "werner": "werner.json",  # Alias
        "xkcd": "xkcd.json",
    }

    def __init__(self, vocabulary: str = "artist"):
        """
        Initialize the ColorNamer with a specific vocabulary.

        Args:
            vocabulary: Name of the color vocabulary to use.
                       Options: 'artist', 'resene', 'natural'/'werner', 'xkcd'
                       (default: 'artist')

        Raises:
            ValueError: If vocabulary is not recognized

        Example:
            >>> namer = ColorNamer(vocabulary="artist")
            >>> # or
            >>> namer = ColorNamer(vocabulary="xkcd")
        """
        if vocabulary not in self._VOCABULARIES:
            available = ", ".join(self._VOCABULARIES.keys())
            raise ValueError(
                f"Unknown vocabulary '{vocabulary}'. "
                f"Available vocabularies: {available}"
            )

        self.vocabulary = vocabulary
        self._colors: Optional[List[Dict]] = None
        self._lab_cache: Dict[Tuple[int, int, int], Tuple[float, float, float]] = {}
        self._data_dir = Path(__file__).parent.parent / "data" / "colors"

    @classmethod
    def available_vocabularies(cls) -> List[str]:
        """
        Get list of available color vocabularies.

        Returns:
            List of vocabulary names that can be used

        Example:
            >>> vocabs = ColorNamer.available_vocabularies()
            >>> print(vocabs)
            ['artist', 'resene', 'natural', 'werner', 'xkcd']
        """
        # Return unique vocabulary names (excluding aliases)
        return ["artist", "resene", "natural", "xkcd"]

    def _load_colors(self) -> List[Dict]:
        """
        Lazy-load color data from JSON file.

        Returns:
            List of color dictionaries with name, hex, rgb, etc.
        """
        if self._colors is not None:
            return self._colors

        filename = self._VOCABULARIES[self.vocabulary]
        filepath = self._data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(
                f"Color data file not found: {filepath}. "
                f"Please ensure the data files are properly installed."
            )

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self._colors = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in color data file {filepath}: {e}")

        return self._colors

    def _rgb_to_lab(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Convert RGB color to CIE Lab color space for perceptual matching.

        Uses D65 illuminant and 2° standard observer.

        Args:
            rgb: Tuple of (R, G, B) values (0-255)

        Returns:
            Tuple of (L, a, b) values in CIE Lab space
        """
        # Check cache first
        if rgb in self._lab_cache:
            return self._lab_cache[rgb]

        # Normalize RGB to 0-1
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0

        # Apply gamma correction (sRGB to linear RGB)
        def gamma_correct(channel):
            if channel <= 0.04045:
                return channel / 12.92
            else:
                return ((channel + 0.055) / 1.055) ** 2.4

        r_linear = gamma_correct(r)
        g_linear = gamma_correct(g)
        b_linear = gamma_correct(b)

        # Convert to XYZ using D65 illuminant matrix
        x = r_linear * 0.4124564 + g_linear * 0.3575761 + b_linear * 0.1804375
        y = r_linear * 0.2126729 + g_linear * 0.7151522 + b_linear * 0.0721750
        z = r_linear * 0.0193339 + g_linear * 0.1191920 + b_linear * 0.9503041

        # Normalize by D65 white point
        x = x / 0.95047
        y = y / 1.00000
        z = z / 1.08883

        # Convert to Lab
        def f(t):
            delta = 6.0 / 29.0
            if t > delta**3:
                return t ** (1.0 / 3.0)
            else:
                return t / (3 * delta**2) + 4.0 / 29.0

        fx = f(x)
        fy = f(y)
        fz = f(z)

        L = 116.0 * fy - 16.0
        a = 500.0 * (fx - fy)
        b_lab = 200.0 * (fy - fz)

        lab = (L, a, b_lab)
        self._lab_cache[rgb] = lab
        return lab

    def _ciede2000(
        self,
        lab1: Tuple[float, float, float],
        lab2: Tuple[float, float, float],
    ) -> float:
        """
        Calculate CIEDE2000 color difference between two Lab colors.

        CIEDE2000 is a perceptually uniform color difference metric that
        better matches human color perception than simple Euclidean distance.

        Args:
            lab1: First color in Lab space (L, a, b)
            lab2: Second color in Lab space (L, a, b)

        Returns:
            Color difference value (lower = more similar)
        """
        # Unpack Lab values
        L1, a1, b1 = lab1
        L2, a2, b2 = lab2

        # Calculate Chroma
        C1 = np.sqrt(a1**2 + b1**2)
        C2 = np.sqrt(a2**2 + b2**2)

        # Calculate average Chroma
        C_bar = (C1 + C2) / 2.0

        # Calculate G factor
        G = 0.5 * (1 - np.sqrt(C_bar**7 / (C_bar**7 + 25**7)))

        # Calculate adjusted a values
        a1_prime = a1 * (1 + G)
        a2_prime = a2 * (1 + G)

        # Calculate adjusted Chroma
        C1_prime = np.sqrt(a1_prime**2 + b1**2)
        C2_prime = np.sqrt(a2_prime**2 + b2**2)

        # Calculate adjusted Hue
        def calc_h_prime(a_prime, b_val):
            if a_prime == 0 and b_val == 0:
                return 0
            h = np.degrees(np.arctan2(b_val, a_prime))
            if h < 0:
                h += 360
            return h

        h1_prime = calc_h_prime(a1_prime, b1)
        h2_prime = calc_h_prime(a2_prime, b2)

        # Calculate delta values
        delta_L_prime = L2 - L1
        delta_C_prime = C2_prime - C1_prime

        # Calculate delta H prime
        if C1_prime * C2_prime == 0:
            delta_h_prime = 0
        elif abs(h2_prime - h1_prime) <= 180:
            delta_h_prime = h2_prime - h1_prime
        elif h2_prime - h1_prime > 180:
            delta_h_prime = h2_prime - h1_prime - 360
        else:
            delta_h_prime = h2_prime - h1_prime + 360

        delta_H_prime = (
            2 * np.sqrt(C1_prime * C2_prime) * np.sin(np.radians(delta_h_prime / 2))
        )

        # Calculate average L', C', H'
        L_bar_prime = (L1 + L2) / 2
        C_bar_prime = (C1_prime + C2_prime) / 2

        if C1_prime * C2_prime == 0:
            H_bar_prime = h1_prime + h2_prime
        elif abs(h1_prime - h2_prime) <= 180:
            H_bar_prime = (h1_prime + h2_prime) / 2
        elif h1_prime + h2_prime < 360:
            H_bar_prime = (h1_prime + h2_prime + 360) / 2
        else:
            H_bar_prime = (h1_prime + h2_prime - 360) / 2

        # Calculate weighting functions
        T = (
            1
            - 0.17 * np.cos(np.radians(H_bar_prime - 30))
            + 0.24 * np.cos(np.radians(2 * H_bar_prime))
            + 0.32 * np.cos(np.radians(3 * H_bar_prime + 6))
            - 0.20 * np.cos(np.radians(4 * H_bar_prime - 63))
        )

        delta_theta = 30 * np.exp(-(((H_bar_prime - 275) / 25) ** 2))

        R_C = 2 * np.sqrt(C_bar_prime**7 / (C_bar_prime**7 + 25**7))

        S_L = 1 + (0.015 * (L_bar_prime - 50) ** 2) / np.sqrt(
            20 + (L_bar_prime - 50) ** 2
        )
        S_C = 1 + 0.045 * C_bar_prime
        S_H = 1 + 0.015 * C_bar_prime * T

        R_T = -np.sin(np.radians(2 * delta_theta)) * R_C

        # Calculate final CIEDE2000 difference
        delta_E = np.sqrt(
            (delta_L_prime / S_L) ** 2
            + (delta_C_prime / S_C) ** 2
            + (delta_H_prime / S_H) ** 2
            + R_T * (delta_C_prime / S_C) * (delta_H_prime / S_H)
        )

        return delta_E

    def name(
        self,
        color: Union[Tuple[int, int, int], str],
        return_metadata: bool = False,
    ) -> Union[Dict[str, any], str]:
        """
        Find the closest color name for an RGB or hex color.

        Uses CIEDE2000 perceptual color difference for accurate matching.

        Args:
            color: RGB tuple (R, G, B) or hex string ('#RRGGBB')
            return_metadata: If True, return full metadata dictionary,
                           otherwise just the color name (default: False)

        Returns:
            If return_metadata=False: Color name string
            If return_metadata=True: Dictionary with keys:
                - name: Color name
                - hex: Hex color code
                - rgb: RGB tuple
                - distance: CIEDE2000 distance from input
                - vocabulary: Active vocabulary name
                - family: Color family (if available)
                - ci_name: Color Index name (if available)
                - description: Color description (if available)

        Raises:
            ValueError: If color format is invalid

        Example:
            >>> namer = ColorNamer(vocabulary="artist")
            >>> namer.name((255, 87, 51))
            'Cadmium Orange'
            >>> namer.name("#FF5733", return_metadata=True)
            {'name': 'Cadmium Orange', 'hex': '#FF6103', ...}
        """
        # Convert hex to RGB if needed
        if isinstance(color, str):
            rgb = self._hex_to_rgb(color)
        else:
            rgb = color

        # Validate RGB
        if (
            not isinstance(rgb, (tuple, list))
            or len(rgb) != 3
            or not all(isinstance(c, int) and 0 <= c <= 255 for c in rgb)
        ):
            raise ValueError(
                "Color must be RGB tuple (0-255) or hex string. " f"Got: {color}"
            )

        # Convert input to Lab
        input_lab = self._rgb_to_lab(rgb)

        # Find closest match
        colors = self._load_colors()
        best_match = None
        best_distance = float("inf")

        for color_data in colors:
            color_rgb = tuple(color_data["rgb"])
            color_lab = self._rgb_to_lab(color_rgb)
            distance = self._ciede2000(input_lab, color_lab)

            if distance < best_distance:
                best_distance = distance
                best_match = color_data

        if best_match is None:
            raise RuntimeError("No colors found in vocabulary")

        # Build result
        if return_metadata:
            result = {
                "name": best_match["name"],
                "hex": best_match["hex"],
                "rgb": tuple(best_match["rgb"]),
                "distance": round(best_distance, 3),
                "vocabulary": self.vocabulary,
                "family": best_match.get("family"),
            }

            # Add optional fields if present
            if "ci_name" in best_match:
                result["ci_name"] = best_match["ci_name"]
            if "description" in best_match:
                result["description"] = best_match["description"]

            return result
        else:
            return best_match["name"]

    def name_palette(
        self,
        colors: List[Tuple[int, int, int]],
        return_metadata: bool = False,
    ) -> List[Union[str, Dict]]:
        """
        Name multiple colors in a palette.

        Args:
            colors: List of RGB tuples
            return_metadata: If True, return metadata dictionaries

        Returns:
            List of color names or metadata dictionaries

        Example:
            >>> namer = ColorNamer()
            >>> palette = [(255, 87, 51), (100, 200, 150), (50, 100, 200)]
            >>> names = namer.name_palette(palette)
            >>> print(names)
            ['Cadmium Orange', 'Mountain Meadow', 'Denim']
        """
        return [self.name(color, return_metadata) for color in colors]

    def closest_pigment(
        self, color: Union[Tuple[int, int, int], str]
    ) -> Dict[str, any]:
        """
        Find the closest actual artist pigment (with Color Index name).

        Useful for digital-to-physical color matching. Only searches colors
        that have Color Index names in the artist vocabulary.

        Args:
            color: RGB tuple or hex string

        Returns:
            Dictionary with pigment name, CI name, and color info

        Example:
            >>> namer = ColorNamer()
            >>> result = namer.closest_pigment((45, 82, 128))
            >>> print(f"{result['name']} ({result['ci_name']})")
            'Prussian Blue (PB27)'
        """
        # Temporarily switch to artist vocabulary if needed
        original_vocab = self.vocabulary
        if self.vocabulary != "artist":
            self.vocabulary = "artist"
            self._colors = None  # Force reload

        try:
            # Convert hex to RGB if needed
            if isinstance(color, str):
                rgb = self._hex_to_rgb(color)
            else:
                rgb = color

            # Get full metadata
            result = self.name(rgb, return_metadata=True)

            # Filter for colors with CI names only
            input_lab = self._rgb_to_lab(rgb)
            colors = self._load_colors()
            pigments = [c for c in colors if c.get("ci_name")]

            if not pigments:
                raise ValueError("No pigments with Color Index names found")

            best_match = None
            best_distance = float("inf")

            for pigment in pigments:
                pigment_rgb = tuple(pigment["rgb"])
                pigment_lab = self._rgb_to_lab(pigment_rgb)
                distance = self._ciede2000(input_lab, pigment_lab)

                if distance < best_distance:
                    best_distance = distance
                    best_match = pigment

            return {
                "name": best_match["name"],
                "ci_name": best_match["ci_name"],
                "hex": best_match["hex"],
                "rgb": tuple(best_match["rgb"]),
                "distance": round(best_distance, 3),
                "family": best_match.get("family"),
                "description": best_match.get("description"),
            }

        finally:
            # Restore original vocabulary
            self.vocabulary = original_vocab
            self._colors = None  # Force reload on next use

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color string to RGB tuple.

        Args:
            hex_color: Hex string like '#FF5733' or 'FF5733'

        Returns:
            RGB tuple (R, G, B)

        Raises:
            ValueError: If hex format is invalid
        """
        hex_color = hex_color.lstrip("#")

        if len(hex_color) != 6:
            raise ValueError(
                f"Hex color must be 6 characters (got {len(hex_color)}): {hex_color}"
            )

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except ValueError:
            raise ValueError(f"Invalid hex color format: {hex_color}")

    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex string.

        Args:
            rgb: RGB tuple (R, G, B)

        Returns:
            Hex string like '#FF5733'
        """
        return "#{:02X}{:02X}{:02X}".format(*rgb)

    def set_vocabulary(self, vocabulary: str) -> None:
        """
        Switch to a different color vocabulary.

        Args:
            vocabulary: Name of vocabulary to switch to

        Raises:
            ValueError: If vocabulary is not recognized

        Example:
            >>> namer = ColorNamer(vocabulary="artist")
            >>> namer.set_vocabulary("xkcd")
            >>> namer.name((255, 87, 51))
            'orange pink'
        """
        if vocabulary not in self._VOCABULARIES:
            available = ", ".join(self._VOCABULARIES.keys())
            raise ValueError(
                f"Unknown vocabulary '{vocabulary}'. "
                f"Available vocabularies: {available}"
            )

        self.vocabulary = vocabulary
        self._colors = None  # Clear cache to force reload

    def get_vocabulary_info(self) -> Dict[str, any]:
        """
        Get information about the current vocabulary.

        Returns:
            Dictionary with vocabulary metadata

        Example:
            >>> namer = ColorNamer(vocabulary="artist")
            >>> info = namer.get_vocabulary_info()
            >>> print(f"{info['name']}: {info['count']} colors")
            'artist: 48 colors'
        """
        colors = self._load_colors()

        # Count colors by family
        families = {}
        for color in colors:
            family = color.get("family", "Unknown")
            families[family] = families.get(family, 0) + 1

        # Count colors with CI names
        ci_count = sum(1 for c in colors if c.get("ci_name"))

        return {
            "name": self.vocabulary,
            "count": len(colors),
            "families": families,
            "ci_names": ci_count,
            "file": self._VOCABULARIES[self.vocabulary],
        }

    def translate(
        self,
        color_name: str,
        from_vocabulary: Optional[str] = None,
        to_vocabulary: str = "xkcd",
        k: int = 3,
    ) -> Dict:
        """
        Translate a colour name from one vocabulary to another.

        Creates a "colour Rosetta Stone" by finding the perceptually closest
        names in the target vocabulary via CIEDE2000 matching in Lab space.

        Args:
            color_name: Name of the colour to translate (case-insensitive)
            from_vocabulary: Source vocabulary. If None, uses current vocabulary.
            to_vocabulary: Target vocabulary name.
            k: Number of closest matches to return (default: 3).

        Returns:
            Dictionary containing:
                - source_name: Original colour name
                - source_vocabulary: Source vocabulary
                - source_rgb: RGB of the source colour
                - translations: List of dicts with name, rgb, hex, distance
                - target_vocabulary: Target vocabulary name

        Raises:
            ValueError: If colour name not found or vocabulary is invalid.

        Example:
            >>> namer = ColorNamer(vocabulary="werner")
            >>> result = namer.translate("Gamboge Yellow", to_vocabulary="xkcd")
            >>> for t in result['translations']:
            ...     print(f"  {t['name']} (ΔE={t['distance']:.1f})")
        """
        src_vocab = from_vocabulary or self.vocabulary

        # Validate vocabularies
        if src_vocab not in self._VOCABULARIES:
            raise ValueError(f"Unknown source vocabulary '{src_vocab}'")
        if to_vocabulary not in self._VOCABULARIES:
            raise ValueError(f"Unknown target vocabulary '{to_vocabulary}'")

        # Save state
        original_vocab = self.vocabulary
        original_colors = self._colors

        try:
            # Load source vocabulary and find the colour
            self.vocabulary = src_vocab
            self._colors = None
            src_colors = self._load_colors()

            source = None
            for c in src_colors:
                if c["name"].lower() == color_name.lower():
                    source = c
                    break

            if source is None:
                available = [c["name"] for c in src_colors]
                raise ValueError(
                    f"Colour '{color_name}' not found in {src_vocab} vocabulary. "
                    f"Available: {', '.join(available[:10])}..."
                )

            source_rgb = tuple(source["rgb"])
            source_lab = self._rgb_to_lab(source_rgb)

            # Load target vocabulary and find k closest
            self.vocabulary = to_vocabulary
            self._colors = None
            tgt_colors = self._load_colors()

            scored = []
            for c in tgt_colors:
                tgt_rgb = tuple(c["rgb"])
                tgt_lab = self._rgb_to_lab(tgt_rgb)
                dist = self._ciede2000(source_lab, tgt_lab)
                scored.append(
                    {
                        "name": c["name"],
                        "rgb": tgt_rgb,
                        "hex": c.get("hex", self._rgb_to_hex(tgt_rgb)),
                        "distance": round(dist, 3),
                    }
                )

            scored.sort(key=lambda x: x["distance"])

            return {
                "source_name": source["name"],
                "source_vocabulary": src_vocab,
                "source_rgb": source_rgb,
                "translations": scored[:k],
                "target_vocabulary": to_vocabulary,
            }

        finally:
            self.vocabulary = original_vocab
            self._colors = original_colors

    def translate_all_vocabularies(
        self,
        color_name: str,
        from_vocabulary: Optional[str] = None,
        k: int = 1,
    ) -> Dict:
        """
        Translate a colour name to all other vocabularies at once.

        Args:
            color_name: Name of the colour to translate
            from_vocabulary: Source vocabulary. If None, uses current.
            k: Number of matches per vocabulary (default: 1)

        Returns:
            Dictionary mapping vocabulary names to translation results.

        Example:
            >>> namer = ColorNamer(vocabulary="artist")
            >>> result = namer.translate_all_vocabularies("Prussian Blue")
            >>> for vocab, trans in result.items():
            ...     print(f"  {vocab}: {trans['translations'][0]['name']}")
        """
        src_vocab = from_vocabulary or self.vocabulary
        all_vocabs = [v for v in self.available_vocabularies() if v != src_vocab]

        results = {}
        for vocab in all_vocabs:
            results[vocab] = self.translate(
                color_name, from_vocabulary=src_vocab, to_vocabulary=vocab, k=k
            )

        return results

    def historical_pigment_probability(
        self,
        color: Union[Tuple[int, int, int], str],
        year: int,
        temperature: float = 15.0,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Estimate probability of historical pigments for a colour at a given date.

        Uses Bayesian reasoning: P(pigment|colour,date) is proportional to
        perceptual match (CIEDE2000) multiplied by historical availability.

        Pigments with year_introduced/year_discontinued fields in the artist
        vocabulary are used. Pigments without date fields are assumed always
        available.

        Args:
            color: RGB tuple or hex string
            year: Year to evaluate pigment availability
            temperature: Softmax temperature for perceptual match (lower = stricter).
                         Default 15.0 gives reasonable discrimination.
            top_k: Number of top pigments to return (default: 5)

        Returns:
            List of dicts sorted by probability, each containing:
                - name: Pigment name
                - ci_name: Color Index name (if available)
                - rgb: RGB tuple
                - probability: Normalised probability (0–1)
                - ciede2000: Raw CIEDE2000 distance
                - available: Whether pigment was available at given year

        Example:
            >>> namer = ColorNamer()
            >>> results = namer.historical_pigment_probability((0, 50, 200), year=1780)
            >>> for r in results:
            ...     print(f"  {r['name']}: prob={r['probability']:.3f}, available={r['available']}")
        """
        # Convert hex to RGB if needed
        if isinstance(color, str):
            rgb = self._hex_to_rgb(color)
        else:
            rgb = color

        input_lab = self._rgb_to_lab(rgb)

        # Save state and switch to artist vocabulary
        original_vocab = self.vocabulary
        original_colors = self._colors

        try:
            self.vocabulary = "artist"
            self._colors = None
            pigments = self._load_colors()

            scored = []
            for p in pigments:
                p_rgb = tuple(p["rgb"])
                p_lab = self._rgb_to_lab(p_rgb)
                distance = self._ciede2000(input_lab, p_lab)

                # Historical availability
                introduced = p.get("year_introduced")
                discontinued = p.get("year_discontinued")

                available = True
                if introduced is not None and year < introduced:
                    available = False
                if discontinued is not None and year > discontinued:
                    available = False

                # Perceptual match score (softmax-style)
                match_score = np.exp(-distance / temperature)

                # Historical prior: 1.0 if available, 0.01 if not (small epsilon)
                historical_prior = 1.0 if available else 0.01

                raw_score = match_score * historical_prior

                scored.append(
                    {
                        "name": p["name"],
                        "ci_name": p.get("ci_name"),
                        "rgb": p_rgb,
                        "raw_score": raw_score,
                        "ciede2000": round(distance, 3),
                        "available": available,
                    }
                )

            # Normalise to probabilities
            total = sum(s["raw_score"] for s in scored)
            if total > 0:
                for s in scored:
                    s["probability"] = round(s["raw_score"] / total, 6)
            else:
                for s in scored:
                    s["probability"] = 0.0

            # Sort by probability descending
            scored.sort(key=lambda x: x["probability"], reverse=True)

            # Clean up and return top_k
            for s in scored:
                del s["raw_score"]

            return scored[:top_k]

        finally:
            self.vocabulary = original_vocab
            self._colors = original_colors
