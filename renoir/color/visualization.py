"""
Visualization functions for color analysis.

This module provides tools for creating educational visualizations
of color data, palettes, and distributions.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D

try:
    import seaborn as sns

    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False


class ColorVisualizer:
    """
    Create visualizations for color analysis and education.

    This class provides methods for visualizing color palettes,
    distributions, and relationships. Designed for teaching color
    theory and computational analysis to art and design students.
    """

    def __init__(self):
        """Initialize the ColorVisualizer."""
        if SEABORN_AVAILABLE:
            sns.set_style("whitegrid")

    def plot_palette(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "Color Palette",
        figsize: Tuple[int, int] = (12, 2),
        save_path: Optional[str] = None,
        show_hex: bool = True,
        show_names: bool = False,
        vocabulary: str = "artist",
    ) -> None:
        """
        Visualize a color palette as horizontal color swatches.

        Educational method for displaying extracted colors clearly.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size (width, height)
            save_path: Optional path to save the figure
            show_hex: Whether to show hex codes below colors
            show_names: Whether to show evocative color names (default: False)
            vocabulary: Color naming vocabulary to use when show_names=True
                       Options: 'artist', 'resene', 'natural', 'xkcd'

        Example:
            >>> from renoir.color import ColorExtractor, ColorVisualizer
            >>> extractor = ColorExtractor()
            >>> visualizer = ColorVisualizer()
            >>> colors = [(255, 87, 51), (100, 200, 150), (50, 100, 200)]
            >>> visualizer.plot_palette(colors, title="My Palette")
            >>> # With color names
            >>> visualizer.plot_palette(colors, show_names=True, vocabulary="artist")
        """
        n_colors = len(colors)

        # Adjust figure height if showing names
        if show_names:
            figsize = (figsize[0], figsize[1] + 1)

        fig, ax = plt.subplots(figsize=figsize)

        # Load color names if requested
        color_names = None
        if show_names:
            try:
                from .namer import ColorNamer

                namer = ColorNamer(vocabulary=vocabulary)
                color_names = namer.name_palette(colors)
            except ImportError:
                print("Warning: ColorNamer not available. Showing hex codes only.")
                color_names = None

        # Create color swatches
        for i, color in enumerate(colors):
            # Normalize to 0-1 for matplotlib
            normalized_color = tuple(c / 255 for c in color)

            # Draw rectangle
            rect = patches.Rectangle(
                (i, 0), 1, 1, facecolor=normalized_color, edgecolor="black", linewidth=2
            )
            ax.add_patch(rect)

            # Determine text color (black or white) based on brightness
            brightness = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
            text_color = "white" if brightness < 128 else "black"

            # Add hex code if requested
            if show_hex and not show_names:
                hex_code = "#{:02x}{:02x}{:02x}".format(*color)
                ax.text(
                    i + 0.5,
                    0.5,
                    hex_code,
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold",
                    color=text_color,
                )

            # Add color names if requested
            if show_names and color_names:
                name = color_names[i]
                # Wrap long names
                if len(name) > 15:
                    words = name.split()
                    mid = len(words) // 2
                    name = "\n".join([" ".join(words[:mid]), " ".join(words[mid:])])

                ax.text(
                    i + 0.5,
                    0.5,
                    name,
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold",
                    color=text_color,
                )

        ax.set_xlim(0, n_colors)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Palette saved to: {save_path}")

        plt.show()

    def plot_named_palette(
        self,
        colors: List[Tuple[int, int, int]],
        vocabulary: str = "artist",
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 4),
        save_path: Optional[str] = None,
        show_metadata: bool = False,
    ) -> None:
        """
        Visualize a color palette with evocative color names.

        Creates a rich visualization showing color swatches with their
        evocative names and optional metadata like Color Index names.

        Args:
            colors: List of RGB tuples
            vocabulary: Color naming vocabulary ('artist', 'resene', 'natural', 'xkcd')
            title: Plot title (auto-generated if None)
            figsize: Figure size (width, height)
            save_path: Optional path to save the figure
            show_metadata: Whether to show additional metadata like CI names

        Example:
            >>> from renoir.color import ColorExtractor, ColorVisualizer
            >>> visualizer = ColorVisualizer()
            >>> colors = [(255, 87, 51), (100, 200, 150), (50, 100, 200)]
            >>> visualizer.plot_named_palette(colors, vocabulary="artist")
        """
        try:
            from .namer import ColorNamer
        except ImportError:
            print("Error: ColorNamer not available")
            return

        namer = ColorNamer(vocabulary=vocabulary)
        named_colors = namer.name_palette(colors, return_metadata=True)

        n_colors = len(colors)

        # Auto-generate title if not provided
        if title is None:
            title = f"Color Palette ({vocabulary.title()} Names)"

        # Adjust figure height for metadata
        if show_metadata:
            figsize = (figsize[0], figsize[1] + 0.5)

        fig, ax = plt.subplots(figsize=figsize)

        # Create color swatches with names
        for i, (color, metadata) in enumerate(zip(colors, named_colors)):
            # Normalize to 0-1 for matplotlib
            normalized_color = tuple(c / 255 for c in color)

            # Draw rectangle
            rect = patches.Rectangle(
                (i, 0), 1, 1, facecolor=normalized_color, edgecolor="black", linewidth=2
            )
            ax.add_patch(rect)

            # Determine text color based on brightness
            brightness = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
            text_color = "white" if brightness < 128 else "black"

            # Add color name
            name = metadata["name"]
            # Wrap long names
            if len(name) > 15:
                words = name.split()
                if len(words) > 1:
                    mid = len(words) // 2
                    name = "\n".join([" ".join(words[:mid]), " ".join(words[mid:])])

            y_pos = 0.6 if show_metadata else 0.5
            ax.text(
                i + 0.5,
                y_pos,
                name,
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=text_color,
            )

            # Add metadata if requested
            if show_metadata:
                meta_lines = []
                if metadata.get("ci_name"):
                    meta_lines.append(f"CI: {metadata['ci_name']}")
                if metadata.get("family"):
                    meta_lines.append(metadata["family"])

                if meta_lines:
                    meta_text = "\n".join(meta_lines)
                    ax.text(
                        i + 0.5,
                        0.3,
                        meta_text,
                        ha="center",
                        va="center",
                        fontsize=7,
                        color=text_color,
                        style="italic",
                    )

        ax.set_xlim(0, n_colors)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Named palette saved to: {save_path}")

        plt.show()

    def plot_color_wheel(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "Color Wheel Distribution",
        figsize: Tuple[int, int] = (8, 8),
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot colors on a color wheel to show hue distribution.

        Educational visualization showing where colors fall on the spectrum.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure

        Example:
            >>> visualizer = ColorVisualizer()
            >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            >>> visualizer.plot_color_wheel(colors)
        """
        from .analysis import ColorAnalyzer

        analyzer = ColorAnalyzer()

        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection="polar"))

        # Convert colors to HSV and extract hues
        hsv_values = [analyzer.rgb_to_hsv(color) for color in colors]

        for color, hsv in zip(colors, hsv_values):
            hue_rad = np.radians(hsv[0])  # Convert hue to radians
            saturation = hsv[1] / 100  # Normalize saturation

            # Plot point
            normalized_color = tuple(c / 255 for c in color)
            ax.plot(
                hue_rad,
                saturation,
                "o",
                color=normalized_color,
                markersize=15,
                markeredgecolor="black",
                markeredgewidth=2,
            )

        ax.set_ylim(0, 1)
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
        ax.set_ylabel("Saturation", fontsize=10)

        # Add color wheel background
        theta = np.linspace(0, 2 * np.pi, 360)
        for t in theta:
            hue_deg = np.degrees(t) % 360
            rgb = analyzer.hsv_to_rgb((hue_deg, 100, 100))
            normalized = tuple(c / 255 for c in rgb)
            ax.plot([t, t], [0, 1], color=normalized, linewidth=2, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Color wheel saved to: {save_path}")

        plt.show()

    def plot_rgb_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "RGB Distribution",
        figsize: Tuple[int, int] = (12, 4),
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot RGB channel distributions as histograms.

        Educational visualization for understanding color composition.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
        """
        rgb_array = np.array(colors)

        fig, axes = plt.subplots(1, 3, figsize=figsize)
        channel_names = ["Red", "Green", "Blue"]
        channel_colors = ["red", "green", "blue"]

        for i, (ax, name, color) in enumerate(zip(axes, channel_names, channel_colors)):
            ax.hist(rgb_array[:, i], bins=20, color=color, alpha=0.7, edgecolor="black")
            ax.set_title(f"{name} Channel", fontweight="bold")
            ax.set_xlabel("Value (0-255)")
            ax.set_ylabel("Frequency")
            ax.set_xlim(0, 255)
            ax.grid(alpha=0.3)

        fig.suptitle(title, fontsize=14, fontweight="bold")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"RGB distribution saved to: {save_path}")

        plt.show()

    def plot_hsv_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "HSV Distribution",
        figsize: Tuple[int, int] = (14, 4),
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot HSV (Hue, Saturation, Value) distributions.

        Educational visualization for understanding color in HSV space.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
        """
        from .analysis import ColorAnalyzer

        analyzer = ColorAnalyzer()
        hsv_values = [analyzer.rgb_to_hsv(color) for color in colors]
        hsv_array = np.array(hsv_values)

        fig, axes = plt.subplots(1, 3, figsize=figsize)

        # Hue (circular, 0-360)
        axes[0].hist(
            hsv_array[:, 0], bins=24, color="purple", alpha=0.7, edgecolor="black"
        )
        axes[0].set_title("Hue Distribution", fontweight="bold")
        axes[0].set_xlabel("Hue (degrees)")
        axes[0].set_ylabel("Frequency")
        axes[0].set_xlim(0, 360)
        axes[0].grid(alpha=0.3)

        # Saturation (0-100%)
        axes[1].hist(
            hsv_array[:, 1], bins=20, color="orange", alpha=0.7, edgecolor="black"
        )
        axes[1].set_title("Saturation Distribution", fontweight="bold")
        axes[1].set_xlabel("Saturation (%)")
        axes[1].set_ylabel("Frequency")
        axes[1].set_xlim(0, 100)
        axes[1].grid(alpha=0.3)

        # Value/Brightness (0-100%)
        axes[2].hist(
            hsv_array[:, 2], bins=20, color="gray", alpha=0.7, edgecolor="black"
        )
        axes[2].set_title("Value/Brightness Distribution", fontweight="bold")
        axes[2].set_xlabel("Value (%)")
        axes[2].set_ylabel("Frequency")
        axes[2].set_xlim(0, 100)
        axes[2].grid(alpha=0.3)

        fig.suptitle(title, fontsize=14, fontweight="bold")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"HSV distribution saved to: {save_path}")

        plt.show()

    def plot_3d_rgb_space(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "RGB Color Space (3D)",
        figsize: Tuple[int, int] = (10, 8),
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot colors in 3D RGB space.

        Advanced educational visualization showing spatial relationships.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")

        rgb_array = np.array(colors)

        # Normalize colors for display
        normalized_colors = rgb_array / 255

        # Plot points
        ax.scatter(
            rgb_array[:, 0],
            rgb_array[:, 1],
            rgb_array[:, 2],
            c=normalized_colors,
            s=200,
            alpha=0.8,
            edgecolors="black",
            linewidths=2,
        )

        ax.set_xlabel("Red", fontsize=12, fontweight="bold")
        ax.set_ylabel("Green", fontsize=12, fontweight="bold")
        ax.set_zlabel("Blue", fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        # Set limits
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 255)
        ax.set_zlim(0, 255)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"3D RGB space saved to: {save_path}")

        plt.show()

    def compare_palettes(
        self,
        palette1: List[Tuple[int, int, int]],
        palette2: List[Tuple[int, int, int]],
        labels: Tuple[str, str] = ("Palette 1", "Palette 2"),
        figsize: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
    ) -> None:
        """
        Compare two color palettes side by side.

        Educational visualization for comparing artistic color choices.

        Args:
            palette1: First list of RGB tuples
            palette2: Second list of RGB tuples
            labels: Tuple of labels for the two palettes
            figsize: Figure size
            save_path: Optional path to save the figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

        # Plot first palette
        for i, color in enumerate(palette1):
            normalized_color = tuple(c / 255 for c in color)
            rect = patches.Rectangle(
                (i, 0), 1, 1, facecolor=normalized_color, edgecolor="black", linewidth=2
            )
            ax1.add_patch(rect)

        ax1.set_xlim(0, len(palette1))
        ax1.set_ylim(0, 1)
        ax1.set_aspect("equal")
        ax1.axis("off")
        ax1.set_title(labels[0], fontsize=12, fontweight="bold")

        # Plot second palette
        for i, color in enumerate(palette2):
            normalized_color = tuple(c / 255 for c in color)
            rect = patches.Rectangle(
                (i, 0), 1, 1, facecolor=normalized_color, edgecolor="black", linewidth=2
            )
            ax2.add_patch(rect)

        ax2.set_xlim(0, len(palette2))
        ax2.set_ylim(0, 1)
        ax2.set_aspect("equal")
        ax2.axis("off")
        ax2.set_title(labels[1], fontsize=12, fontweight="bold")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Palette comparison saved to: {save_path}")

        plt.show()

    def plot_temperature_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "Color Temperature Distribution",
        figsize: Tuple[int, int] = (10, 6),
        save_path: Optional[str] = None,
    ) -> None:
        """
        Visualize warm vs. cool color distribution.

        Educational visualization for color temperature analysis.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
        """
        from .analysis import ColorAnalyzer

        analyzer = ColorAnalyzer()
        temp_dist = analyzer.analyze_color_temperature_distribution(colors)

        # Create bar chart
        fig, ax = plt.subplots(figsize=figsize)

        categories = ["Warm", "Cool", "Neutral"]
        counts = [
            temp_dist["warm_count"],
            temp_dist["cool_count"],
            temp_dist["neutral_count"],
        ]
        bar_colors = ["#FF6B35", "#4ECDC4", "#95A5A6"]

        bars = ax.bar(
            categories,
            counts,
            color=bar_colors,
            alpha=0.8,
            edgecolor="black",
            linewidth=2,
        )

        # Add percentages on bars
        for bar, count in zip(bars, counts):
            percentage = (count / sum(counts)) * 100
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{percentage:.1f}%",
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold",
            )

        ax.set_ylabel("Number of Colors", fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Temperature distribution saved to: {save_path}")

        plt.show()

    def create_artist_color_report(
        self,
        colors: List[Tuple[int, int, int]],
        artist_name: str,
        figsize: Tuple[int, int] = (16, 12),
        save_path: Optional[str] = None,
    ) -> None:
        """
        Create a comprehensive color analysis report for an artist.

        Combines multiple visualizations into a single figure.
        Educational method for comprehensive color analysis.

        Args:
            colors: List of RGB tuples from the artist's works
            artist_name: Name of the artist
            figsize: Figure size
            save_path: Optional path to save the figure
        """
        from .analysis import ColorAnalyzer

        analyzer = ColorAnalyzer()

        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Title
        fig.suptitle(f"Color Analysis: {artist_name}", fontsize=18, fontweight="bold")

        # 1. Palette (top, spanning all columns)
        ax_palette = fig.add_subplot(gs[0, :])
        for i, color in enumerate(colors[:10]):  # Show up to 10 colors
            normalized_color = tuple(c / 255 for c in color)
            rect = patches.Rectangle(
                (i, 0), 1, 1, facecolor=normalized_color, edgecolor="black", linewidth=2
            )
            ax_palette.add_patch(rect)
        ax_palette.set_xlim(0, min(10, len(colors)))
        ax_palette.set_ylim(0, 1)
        ax_palette.set_aspect("equal")
        ax_palette.axis("off")
        ax_palette.set_title("Dominant Color Palette", fontsize=12, fontweight="bold")

        # 2. RGB distributions
        rgb_array = np.array(colors)
        channel_names = ["Red", "Green", "Blue"]
        channel_colors = ["red", "green", "blue"]

        for i, (name, color) in enumerate(zip(channel_names, channel_colors)):
            ax = fig.add_subplot(gs[1, i])
            ax.hist(rgb_array[:, i], bins=15, color=color, alpha=0.7, edgecolor="black")
            ax.set_title(f"{name}", fontsize=10, fontweight="bold")
            ax.set_xlim(0, 255)
            ax.grid(alpha=0.3)

        # 3. HSV analysis
        hsv_values = [analyzer.rgb_to_hsv(color) for color in colors]
        hsv_array = np.array(hsv_values)

        # Hue circular plot
        ax_hue = fig.add_subplot(gs[2, 0], projection="polar")
        theta = np.radians(hsv_array[:, 0])
        ax_hue.hist(theta, bins=24, color="purple", alpha=0.7)
        ax_hue.set_title("Hue", fontsize=10, fontweight="bold")

        # Saturation
        ax_sat = fig.add_subplot(gs[2, 1])
        ax_sat.hist(
            hsv_array[:, 1], bins=15, color="orange", alpha=0.7, edgecolor="black"
        )
        ax_sat.set_title("Saturation", fontsize=10, fontweight="bold")
        ax_sat.set_xlim(0, 100)
        ax_sat.grid(alpha=0.3)

        # Value
        ax_val = fig.add_subplot(gs[2, 2])
        ax_val.hist(
            hsv_array[:, 2], bins=15, color="gray", alpha=0.7, edgecolor="black"
        )
        ax_val.set_title("Brightness", fontsize=10, fontweight="bold")
        ax_val.set_xlim(0, 100)
        ax_val.grid(alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Color report saved to: {save_path}")

        plt.show()


def check_visualization_support() -> bool:
    """
    Check if visualization dependencies are available.

    Returns:
        True if matplotlib is available, False otherwise
    """
    try:
        import matplotlib.pyplot as plt

        print("✅ Color visualization fully supported (matplotlib available)")
        if SEABORN_AVAILABLE:
            print("✅ Enhanced styling available (seaborn available)")
        else:
            print("ℹ️  Basic styling (seaborn not installed, but not required)")
        return True
    except ImportError:
        print("❌ Visualization not available")
        print("   Install with: pip install matplotlib")
        return False
