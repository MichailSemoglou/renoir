"""
Color extraction functions for artwork analysis.

This module provides tools for extracting dominant colors from artworks
using k-means clustering and other computational methods.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from PIL import Image
from collections import Counter

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class ColorExtractor:
    """
    Extract dominant colors and palettes from artwork images.
    
    This class provides methods for extracting color information from
    digital images, designed for educational use in teaching computational
    color analysis to art and design students.
    
    Attributes:
        use_sklearn: Whether scikit-learn is available for k-means clustering
    """
    
    def __init__(self):
        """Initialize the ColorExtractor."""
        self.use_sklearn = SKLEARN_AVAILABLE
        if not SKLEARN_AVAILABLE:
            print("Warning: scikit-learn not available. Some features may be limited.")
            print("Install with: pip install scikit-learn")
    
    def extract_dominant_colors(
        self,
        image: Union[Image.Image, np.ndarray],
        n_colors: int = 5,
        method: str = 'kmeans',
        sample_size: Optional[int] = 10000
    ) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from an image using k-means clustering.

        This method identifies the most prominent colors in an artwork by
        clustering pixel colors and finding cluster centers. Ideal for
        teaching students about color quantization and computational analysis.

        Args:
            image: PIL Image or numpy array of the artwork
            n_colors: Number of dominant colors to extract (default: 5)
            method: Extraction method - 'kmeans' or 'frequency' (default: 'kmeans')
            sample_size: Number of pixels to sample for faster processing
                        None = use all pixels (default: 10000)

        Returns:
            List of RGB tuples representing dominant colors, ordered by prominence

        Raises:
            ValueError: If n_colors is invalid
            ValueError: If sample_size is invalid
            ValueError: If method is not recognized
            TypeError: If image is not PIL Image or numpy array
            ValueError: If image dimensions are invalid

        Example:
            >>> extractor = ColorExtractor()
            >>> from PIL import Image
            >>> img = Image.open('artwork.jpg')
            >>> colors = extractor.extract_dominant_colors(img, n_colors=5)
            >>> print(colors)
            [(120, 89, 143), (201, 178, 156), ...]
        """
        # Input validation
        if not isinstance(n_colors, int):
            raise ValueError("n_colors must be an integer")
        if n_colors < 1:
            raise ValueError("n_colors must be at least 1")
        if n_colors > 256:
            raise ValueError("n_colors cannot exceed 256")

        if sample_size is not None:
            if not isinstance(sample_size, int):
                raise ValueError("sample_size must be an integer or None")
            if sample_size < 1:
                raise ValueError("sample_size must be positive")

        if method not in ['kmeans', 'frequency']:
            raise ValueError("method must be 'kmeans' or 'frequency'")

        # Validate and convert image
        try:
            if isinstance(image, Image.Image):
                img_array = np.array(image)
            elif isinstance(image, np.ndarray):
                img_array = image
            else:
                raise TypeError(
                    "image must be a PIL Image or numpy array, "
                    f"got {type(image).__name__}"
                )
        except Exception as e:
            raise TypeError(f"Failed to convert image to array: {str(e)}")

        # Validate image dimensions
        if img_array.ndim not in [2, 3]:
            raise ValueError(
                f"Image must be 2D or 3D array, got {img_array.ndim}D"
            )

        if img_array.ndim == 3:
            if img_array.shape[-1] not in [3, 4]:
                raise ValueError(
                    f"Image must have 3 (RGB) or 4 (RGBA) channels, "
                    f"got {img_array.shape[-1]}"
                )
            # Handle RGBA images by removing alpha channel
            if img_array.shape[-1] == 4:
                img_array = img_array[:, :, :3]
        else:
            # Grayscale - convert to RGB
            img_array = np.stack([img_array] * 3, axis=-1)

        # Check image is not empty
        if img_array.size == 0:
            raise ValueError("Image is empty")

        # Reshape to 2D array of pixels
        try:
            pixels = img_array.reshape(-1, 3)
        except Exception as e:
            raise ValueError(f"Failed to reshape image: {str(e)}")

        # Remove any invalid pixels (e.g., all zeros, all 255s)
        valid_pixels = pixels[~np.all(pixels == 0, axis=1)]
        valid_pixels = valid_pixels[~np.all(valid_pixels == 255, axis=1)]

        if len(valid_pixels) == 0:
            print("Warning: No valid pixels found in image")
            return [(0, 0, 0)] * n_colors

        if len(valid_pixels) < n_colors:
            print(f"Warning: Only {len(valid_pixels)} unique pixels, fewer than requested {n_colors} colors")
            n_colors = len(valid_pixels)

        # Sample pixels for faster processing
        if sample_size and len(valid_pixels) > sample_size:
            indices = np.random.choice(len(valid_pixels), sample_size, replace=False)
            sampled_pixels = valid_pixels[indices]
        else:
            sampled_pixels = valid_pixels

        try:
            if method == 'kmeans' and self.use_sklearn:
                return self._extract_kmeans(sampled_pixels, n_colors)
            else:
                return self._extract_frequency(sampled_pixels, n_colors)
        except Exception as e:
            raise RuntimeError(f"Color extraction failed: {str(e)}")
    
    def _extract_kmeans(
        self, 
        pixels: np.ndarray, 
        n_colors: int
    ) -> List[Tuple[int, int, int]]:
        """
        Extract colors using k-means clustering.
        
        Args:
            pixels: Array of pixel RGB values
            n_colors: Number of clusters/colors to extract
            
        Returns:
            List of RGB tuples ordered by cluster size
        """
        # Perform k-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get cluster centers (dominant colors)
        colors = kmeans.cluster_centers_.astype(int)
        
        # Count pixels in each cluster to order by prominence
        labels = kmeans.labels_
        label_counts = Counter(labels)
        
        # Sort colors by cluster size (most prominent first)
        sorted_indices = sorted(
            range(n_colors), 
            key=lambda i: label_counts[i], 
            reverse=True
        )
        
        sorted_colors = [tuple(colors[i]) for i in sorted_indices]
        
        return sorted_colors
    
    def _extract_frequency(
        self, 
        pixels: np.ndarray, 
        n_colors: int
    ) -> List[Tuple[int, int, int]]:
        """
        Extract colors by frequency (fallback method without sklearn).
        
        Args:
            pixels: Array of pixel RGB values
            n_colors: Number of most frequent colors to return
            
        Returns:
            List of RGB tuples ordered by frequency
        """
        # Convert to tuples for counting
        pixel_tuples = [tuple(pixel) for pixel in pixels]
        
        # Count frequencies
        color_counts = Counter(pixel_tuples)
        
        # Get n most common
        most_common = color_counts.most_common(n_colors)
        
        return [color for color, count in most_common]
    
    def extract_palette_from_artwork(
        self, 
        artwork_dict: Dict,
        n_colors: int = 5
    ) -> Dict:
        """
        Extract color palette from a WikiArt artwork dictionary.
        
        Convenience method that works directly with renoir artwork data.
        
        Args:
            artwork_dict: Artwork dictionary from WikiArt dataset
            n_colors: Number of colors to extract
            
        Returns:
            Dictionary with 'colors' (RGB tuples) and 'metadata' (artwork info)
            
        Example:
            >>> from renoir import ArtistAnalyzer
            >>> analyzer = ArtistAnalyzer()
            >>> works = analyzer.extract_artist_works('claude-monet')
            >>> extractor = ColorExtractor()
            >>> palette = extractor.extract_palette_from_artwork(works[0])
        """
        image = artwork_dict['image']
        colors = self.extract_dominant_colors(image, n_colors=n_colors)
        
        return {
            'colors': colors,
            'artwork': artwork_dict.get('title', 'Unknown'),
            'artist': artwork_dict.get('artist', 'Unknown'),
            'n_colors': n_colors
        }
    
    def extract_average_color(
        self, 
        image: Union[Image.Image, np.ndarray]
    ) -> Tuple[int, int, int]:
        """
        Calculate the average color of an image.
        
        Simple method useful for teaching color concepts to beginners.
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            RGB tuple representing the average color
            
        Example:
            >>> extractor = ColorExtractor()
            >>> avg_color = extractor.extract_average_color(img)
            >>> print(f"Average color: RGB{avg_color}")
        """
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Handle RGBA
        if img_array.shape[-1] == 4:
            img_array = img_array[:, :, :3]
        
        # Calculate mean for each channel
        avg_color = np.mean(img_array, axis=(0, 1)).astype(int)
        
        return tuple(avg_color)
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hexadecimal color code.
        
        Args:
            rgb: Tuple of (R, G, B) values (0-255)
            
        Returns:
            Hexadecimal color string (e.g., '#FF5733')
            
        Example:
            >>> extractor = ColorExtractor()
            >>> hex_color = extractor.rgb_to_hex((255, 87, 51))
            >>> print(hex_color)  # '#FF5733'
        """
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hexadecimal color code to RGB tuple.
        
        Args:
            hex_color: Hexadecimal color string (e.g., '#FF5733' or 'FF5733')
            
        Returns:
            Tuple of (R, G, B) values (0-255)
            
        Example:
            >>> extractor = ColorExtractor()
            >>> rgb = extractor.hex_to_rgb('#FF5733')
            >>> print(rgb)  # (255, 87, 51)
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def palette_to_dict(
        self,
        colors: List[Tuple[int, int, int]],
        include_hex: bool = True
    ) -> Dict:
        """
        Convert color palette to a dictionary format.

        Useful for exporting palettes or educational demonstrations.

        Args:
            colors: List of RGB tuples
            include_hex: Whether to include hex codes (default: True)

        Returns:
            Dictionary with palette information

        Example:
            >>> colors = [(255, 87, 51), (100, 200, 150)]
            >>> palette_dict = extractor.palette_to_dict(colors)
        """
        # Convert numpy types to native Python types for JSON compatibility
        colors_native = [
            (int(r), int(g), int(b)) for r, g, b in colors
        ]

        palette = {
            'rgb_values': colors_native,
            'n_colors': len(colors_native)
        }

        if include_hex:
            palette['hex_values'] = [self.rgb_to_hex(color) for color in colors_native]

        return palette
    
    def export_palette_css(
        self, 
        colors: List[Tuple[int, int, int]], 
        filename: str,
        prefix: str = 'color'
    ) -> None:
        """
        Export color palette as CSS variables.
        
        Useful for design students to use extracted palettes in web projects.
        
        Args:
            colors: List of RGB tuples
            filename: Output CSS filename
            prefix: Variable name prefix (default: 'color')
            
        Example:
            >>> colors = [(255, 87, 51), (100, 200, 150)]
            >>> extractor.export_palette_css(colors, 'palette.css')
        """
        with open(filename, 'w') as f:
            f.write(":root {\n")
            for i, color in enumerate(colors, 1):
                hex_color = self.rgb_to_hex(color)
                f.write(f"  --{prefix}-{i}: {hex_color};\n")
            f.write("}\n")
        
        print(f"Palette exported to {filename}")
    
    def export_palette_json(
        self, 
        colors: List[Tuple[int, int, int]], 
        filename: str
    ) -> None:
        """
        Export color palette as JSON.
        
        Args:
            colors: List of RGB tuples
            filename: Output JSON filename
            
        Example:
            >>> colors = [(255, 87, 51), (100, 200, 150)]
            >>> extractor.export_palette_json(colors, 'palette.json')
        """
        import json
        
        palette_dict = self.palette_to_dict(colors)
        
        with open(filename, 'w') as f:
            json.dump(palette_dict, f, indent=2)
        
        print(f"Palette exported to {filename}")


def check_color_extraction_support() -> bool:
    """
    Check if color extraction dependencies are available.
    
    Returns:
        True if scikit-learn is available, False otherwise
    """
    if SKLEARN_AVAILABLE:
        print("✅ Color extraction fully supported (scikit-learn available)")
        print("   You can use k-means clustering for optimal color extraction")
    else:
        print("⚠️  Limited color extraction support")
        print("   Install scikit-learn for k-means clustering:")
        print("   pip install scikit-learn")
        print("   Fallback frequency-based extraction will be used")
    
    return SKLEARN_AVAILABLE
