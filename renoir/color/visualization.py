"""
Visualization functions for color analysis.

This module provides tools for creating educational visualizations
of color data, palettes, and distributions.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
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
        show: bool = True,
    ) -> Figure:
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
            show: If True, display the figure with plt.show()

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
            brightness = self._calculate_brightness(color)
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

        if show:
            plt.show()
        return fig

    def plot_named_palette(
        self,
        colors: List[Tuple[int, int, int]],
        vocabulary: str = "artist",
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 4),
        save_path: Optional[str] = None,
        show_metadata: bool = False,
        show: bool = True,
    ) -> Figure:
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
            show: If True, display the figure with plt.show()

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

        if show:
            plt.show()
        return fig

    def plot_color_wheel(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "Color Wheel Distribution",
        figsize: Tuple[int, int] = (8, 8),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Plot colors on a color wheel to show hue distribution.

        Educational visualization showing where colors fall on the spectrum.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()

        Example:
            >>> visualizer = ColorVisualizer()
            >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            >>> fig = visualizer.plot_color_wheel(colors)
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

        if show:
            plt.show()
        return fig

    def plot_rgb_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "RGB Distribution",
        figsize: Tuple[int, int] = (12, 4),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Plot RGB channel distributions as histograms.

        Educational visualization for understanding color composition.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
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

        if show:
            plt.show()
        return fig

    def plot_hsv_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "HSV Distribution",
        figsize: Tuple[int, int] = (14, 4),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Plot HSV (Hue, Saturation, Value) distributions.

        Educational visualization for understanding color in HSV space.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
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

        if show:
            plt.show()
        return fig

    def plot_3d_rgb_space(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "RGB Color Space (3D)",
        figsize: Tuple[int, int] = (10, 8),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Plot colors in 3D RGB space.

        Advanced educational visualization showing spatial relationships.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
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

        if show:
            plt.show()
        return fig

    def compare_palettes(
        self,
        palette1: List[Tuple[int, int, int]],
        palette2: List[Tuple[int, int, int]],
        labels: Tuple[str, str] = ("Palette 1", "Palette 2"),
        figsize: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Compare two color palettes side by side.

        Educational visualization for comparing artistic color choices.

        Args:
            palette1: First list of RGB tuples
            palette2: Second list of RGB tuples
            labels: Tuple of labels for the two palettes
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
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

        if show:
            plt.show()
        return fig

    def plot_temperature_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "Color Temperature Distribution",
        figsize: Tuple[int, int] = (10, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Visualize warm vs. cool color distribution.

        Educational visualization for color temperature analysis.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
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

        if show:
            plt.show()
        return fig

    def create_artist_color_report(
        self,
        colors: List[Tuple[int, int, int]],
        artist_name: str,
        figsize: Tuple[int, int] = (16, 12),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Create a comprehensive color analysis report for an artist.

        Combines multiple visualizations into a single figure.
        Educational method for comprehensive color analysis.

        Args:
            colors: List of RGB tuples from the artist's works
            artist_name: Name of the artist
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
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

        if show:
            plt.show()
        return fig

    # ------------------------------------------------------------------
    # Paper-figure methods (added v3.4.0)
    # ------------------------------------------------------------------

    def _calculate_brightness(self, rgb: Tuple[int, int, int]) -> float:
        """Return perceptual brightness (ITU-R BT.601 luma) for an RGB triplet."""
        return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

    def plot_historical_pigment_probability(
        self,
        color: Tuple[int, int, int],
        year: int,
        results: Optional[List[Dict]] = None,
        top_k: int = 5,
        figsize: Tuple[float, float] = (10.0, 4.5),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Visualize Historical Pigment Probability (HPP) output for one color.

        Shows the input color alongside the ranked candidate pigments returned
        by :meth:`~renoir.color.namer.ColorNamer.historical_pigment_probability`,
        with swatch, Color Index name, year of introduction, probability bar,
        and availability flag for each candidate.

        Args:
            color: Input RGB color tuple, e.g. ``(28, 62, 145)``.
            year: Historical year against which availability is assessed.
            results: Pre-computed HPP output (list of dicts).  If ``None`` the
                method calls :class:`~renoir.color.namer.ColorNamer` internally.
            top_k: Number of candidate pigments to display (default 5).
            figsize: Figure dimensions ``(width, height)`` in inches.
            save_path: File path for saving (PNG at 300 dpi or PDF).
            show: If True, display the figure with plt.show().
        """
        from .namer import ColorNamer

        if results is None:
            namer = ColorNamer()
            results = namer.historical_pigment_probability(color, year, top_k=top_k)

        k = len(results)
        r, g, b = color
        hex_str = f"#{r:02X}{g:02X}{b:02X}"
        brightness = self._calculate_brightness(color)
        input_fg = "white" if brightness < 140 else "#111111"

        fig, axes = plt.subplots(
            1,
            k + 1,
            figsize=figsize,
            gridspec_kw=dict(
                width_ratios=[1.5] + [1.0] * k,
                wspace=0.04,
                left=0.01,
                right=0.99,
                top=0.88,
                bottom=0.06,
            ),
        )
        fig.patch.set_facecolor("white")
        fig.suptitle(
            "Historical Pigment Probability",
            fontsize=10,
            fontweight="bold",
            y=0.96,
            color="#1A1A1A",
        )

        # ── Input panel ──────────────────────────────────────────────────
        ax_in = axes[0]
        ax_in.set_xlim(0, 1)
        ax_in.set_ylim(0, 1)
        ax_in.set_xticks([])
        ax_in.set_yticks([])
        for sp in ax_in.spines.values():
            sp.set_edgecolor("#CCCCCC")
            sp.set_linewidth(0.8)
        ax_in.set_facecolor(f"#{r:02X}{g:02X}{b:02X}")
        ax_in.text(
            0.5,
            0.60,
            hex_str,
            transform=ax_in.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=input_fg,
        )
        ax_in.text(
            0.5,
            0.40,
            str(year),
            transform=ax_in.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            color=input_fg,
            alpha=0.85,
        )
        ax_in.text(
            0.5,
            0.20,
            "Input color",
            transform=ax_in.transAxes,
            ha="center",
            va="center",
            fontsize=7.5,
            color=input_fg,
            fontstyle="italic",
            alpha=0.75,
        )

        # ── Candidate panels ─────────────────────────────────────────────
        max_prob = max(c["probability"] for c in results) if results else 1.0
        _ACTIVE_COL = "#2D6A9F"
        _INACTIVE_COL = "#AAAAAA"

        for idx, cand in enumerate(results):
            ax = axes[idx + 1]
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_edgecolor("#DDDDDD")
                sp.set_linewidth(0.7)
            ax.set_facecolor("white")

            cr, cg, cb = cand["rgb"]
            cand_hex = f"#{cr:02X}{cg:02X}{cb:02X}"
            cand_bright = self._calculate_brightness(cand["rgb"])
            cand_fg = "white" if cand_bright < 140 else "#111111"
            available = cand.get("available", True)
            yr_intro = cand.get("year_introduced")

            # Top 50 % → color swatch
            ax.add_patch(
                patches.Rectangle(
                    (0, 0.50),
                    1,
                    0.50,
                    facecolor=cand_hex,
                    linewidth=0,
                )
            )

            # Pigment name (centered in swatch)
            ax.text(
                0.5,
                0.66,
                cand["name"],
                ha="center",
                va="center",
                fontsize=7.0,
                fontweight="bold",
                color=cand_fg,
                multialignment="center",
            )

            # CI name
            ci = cand.get("ci_name") or ""
            ax.text(
                0.5,
                0.44,
                ci,
                ha="center",
                va="top",
                fontsize=6.5,
                color="#555555",
            )

            # Year introduced
            if yr_intro is not None:
                yr_label = "antiquity" if yr_intro <= 0 else f"est. {yr_intro}"
            else:
                yr_label = "date unknown"
            ax.text(
                0.5,
                0.34,
                yr_label,
                ha="center",
                va="top",
                fontsize=6.0,
                color="#888888",
            )

            # Probability bar
            bar_y, bar_h = 0.17, 0.07
            ax.add_patch(
                patches.Rectangle(
                    (0.05, bar_y),
                    0.90,
                    bar_h,
                    facecolor="#E0E0E0",
                    linewidth=0,
                )
            )
            fill_w = 0.90 * (cand["probability"] / max_prob)
            bar_col = _ACTIVE_COL if available else _INACTIVE_COL
            ax.add_patch(
                patches.Rectangle(
                    (0.05, bar_y),
                    fill_w,
                    bar_h,
                    facecolor=bar_col,
                    linewidth=0,
                )
            )

            # Probability value
            ax.text(
                0.5,
                bar_y - 0.03,
                f"p = {cand['probability']:.3f}",
                ha="center",
                va="top",
                fontsize=6.0,
                color="#555555",
            )

            # Availability badge
            badge_col = "#2E7D32" if available else "#B71C1C"
            badge_txt = "Available" if available else "Not yet available"
            ax.text(
                0.5,
                0.04,
                badge_txt,
                ha="center",
                va="bottom",
                fontsize=6.0,
                fontweight="bold",
                color=badge_col,
            )

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"HPP figure saved: {save_path}")
        if show:
            plt.show()
        return fig

    def plot_pemd_comparison(
        self,
        pairs: List[Tuple[List, List]],
        labels: Optional[List[Tuple[str, str]]] = None,
        pemd_values: Optional[List[float]] = None,
        figsize: Tuple[float, float] = (9.0, 4.0),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Visualize Palette Earth Mover's Distance (PEMD) for one or more palette pairs.

        Each pair is shown as two proportional color strips with the PEMD value
        annotated between them.  Accepts pre-computed PEMD values or computes
        them internally.

        Args:
            pairs: List of ``(palette1, palette2)`` tuples.  Each palette is a
                list of ``((R, G, B), proportion)`` tuples.
            labels: List of ``(label1, label2)`` strings for each pair.
            pemd_values: Pre-computed PEMD floats, one per pair.  If ``None``
                values are computed internally (requires scipy).
            figsize: Figure dimensions ``(width, height)`` in inches.
            save_path: File path for saving (PNG at 300 dpi or PDF).
            show: If True, display the figure with plt.show().
        """
        from .analysis import ColorAnalyzer

        n_pairs = len(pairs)
        if labels is None:
            labels = [
                (f"Palette A ({i + 1})", f"Palette B ({i + 1})") for i in range(n_pairs)
            ]

        # Validate and compute missing PEMD values
        if pemd_values is not None and len(pemd_values) != n_pairs:
            raise ValueError(
                f"pemd_values has {len(pemd_values)} entries but pairs has {n_pairs}."
            )
        analyzer = ColorAnalyzer()
        computed: List[Optional[float]] = (
            list(pemd_values) if pemd_values is not None else [None] * n_pairs
        )
        for i, (p1, p2) in enumerate(pairs):
            if computed[i] is None:
                computed[i] = analyzer.palette_earth_movers_distance(p1, p2)

        fig = plt.figure(figsize=figsize, facecolor="white")
        fig.suptitle(
            "Palette Earth Mover's Distance (PEMD)",
            fontsize=10,
            fontweight="bold",
            y=0.97,
            color="#1A1A1A",
        )

        # Each pair: 2 strip rows (strip1, strip2), gap between pairs
        gs = plt.GridSpec(
            n_pairs * 2,
            1,
            hspace=0.20,
            left=0.15,
            right=0.88,
            top=0.88,
            bottom=0.05,
        )

        def _draw_strip(ax: "plt.Axes", palette: List, label: str) -> None:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_edgecolor("#CCCCCC")
                sp.set_linewidth(0.6)
            ax.set_facecolor("white")
            total_w = sum(prop for _, prop in palette) or 1.0
            x = 0.0
            for rgb, prop in palette:
                seg_w = prop / total_w
                rr, gg, bb = rgb
                bright = self._calculate_brightness(rgb)
                seg_fg = "white" if bright < 140 else "#111111"
                ax.add_patch(
                    patches.Rectangle(
                        (x, 0),
                        seg_w,
                        1,
                        facecolor=f"#{rr:02X}{gg:02X}{bb:02X}",
                        linewidth=0,
                    )
                )
                if seg_w > 0.10:
                    ax.text(
                        x + seg_w / 2,
                        0.5,
                        f"#{rr:02X}{gg:02X}{bb:02X}",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color=seg_fg,
                    )
                x += seg_w
            ax.text(
                -0.02,
                0.5,
                label,
                transform=ax.transAxes,
                ha="right",
                va="center",
                fontsize=8,
                color="#333333",
            )

        for pair_idx, (p1, p2) in enumerate(pairs):
            lbl1, lbl2 = labels[pair_idx]
            pemd_val = computed[pair_idx]
            ax1 = fig.add_subplot(gs[pair_idx * 2, 0])
            ax2 = fig.add_subplot(gs[pair_idx * 2 + 1, 0])
            _draw_strip(ax1, p1, lbl1)
            _draw_strip(ax2, p2, lbl2)

            # PEMD annotation to the right of both strips
            ax1_pos = ax1.get_position()
            ax2_pos = ax2.get_position()
            mid_y = (ax1_pos.y0 + ax2_pos.y1) / 2
            fig.text(
                0.895,
                mid_y,
                f"PEMD\n{pemd_val:.2f}",
                ha="left",
                va="center",
                fontsize=8.5,
                fontweight="bold",
                color="white",
                bbox=dict(
                    boxstyle="round,pad=0.35",
                    facecolor="#1A1A1A",
                    edgecolor="none",
                ),
            )

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"PEMD figure saved: {save_path}")
        if show:
            plt.show()
        return fig

    def plot_cross_vocabulary_naming(
        self,
        colors: List[Tuple[int, int, int]],
        vocabulary_labels: Optional[Dict[str, str]] = None,
        figsize: Optional[Tuple[float, float]] = None,
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Visualize how a palette is named across all four color vocabularies.

        Creates a grid with vocabularies in rows and colors in columns.
        Each cell shows the matched color swatch and the name from that
        vocabulary (CIEDE2000 nearest-neighbor match).

        Args:
            colors: List of RGB tuples to name.
            vocabulary_labels: Optional mapping of vocabulary key to display
                label.  Defaults to standard vocabulary names.
            figsize: Figure dimensions ``(width, height)`` in inches.
                Auto-sized when ``None``.
            save_path: File path for saving (PNG at 300 dpi or PDF).
            show: If True, display the figure with plt.show().
        """
        from .namer import ColorNamer

        _VOCABS = ["artist", "resene", "natural", "xkcd"]
        if vocabulary_labels is None:
            vocabulary_labels = {
                "artist": "Artist pigments",
                "resene": "Resene",
                "natural": "Werner's Nomenclature",
                "xkcd": "xkcd",
            }

        # Gather names + matched RGB for each vocabulary
        vocab_data: Dict[str, List[Dict]] = {}
        for v in _VOCABS:
            namer = ColorNamer(vocabulary=v)
            vocab_data[v] = namer.name_palette(colors, return_metadata=True)

        n_colors = len(colors)
        n_vocabs = len(_VOCABS)

        if figsize is None:
            figsize = (9.5, max(3.0, 0.85 * n_vocabs + 1.0))

        fig, axes = plt.subplots(
            n_vocabs,
            n_colors,
            figsize=figsize,
            squeeze=False,
            gridspec_kw=dict(
                wspace=0.04,
                hspace=0.06,
                left=0.16,
                right=0.99,
                top=0.88,
                bottom=0.06,
            ),
        )
        fig.patch.set_facecolor("white")
        fig.suptitle(
            "Cross-vocabulary color naming",
            fontsize=10,
            fontweight="bold",
            y=0.96,
            color="#1A1A1A",
        )

        # Column headers: input color hex
        for col_idx, rgb in enumerate(colors):
            rr, gg, bb = rgb
            axes[0, col_idx].set_title(
                f"#{rr:02X}{gg:02X}{bb:02X}",
                fontsize=7.5,
                color="#444444",
                pad=3,
            )

        # Row labels: vocabulary names
        for row_idx, v in enumerate(_VOCABS):
            axes[row_idx, 0].set_ylabel(
                vocabulary_labels[v],
                fontsize=7.5,
                color="#333333",
                rotation=0,
                ha="right",
                va="center",
                labelpad=4,
            )

        # Cells
        for row_idx, v in enumerate(_VOCABS):
            for col_idx, rgb in enumerate(colors):
                ax = axes[row_idx, col_idx]
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_xticks([])
                ax.set_yticks([])
                for sp in ax.spines.values():
                    sp.set_edgecolor("#E0E0E0")
                    sp.set_linewidth(0.6)

                meta = vocab_data[v][col_idx]
                if isinstance(meta, dict):
                    name_str = meta.get("name", "—")
                    mr, mg, mb = meta.get("rgb", rgb)
                else:
                    name_str = str(meta)
                    mr, mg, mb = rgb

                # Left half: input color
                ax.add_patch(
                    patches.Rectangle(
                        (0, 0),
                        0.5,
                        1,
                        facecolor=f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}",
                        linewidth=0,
                    )
                )
                # Right half: matched color from vocabulary
                ax.add_patch(
                    patches.Rectangle(
                        (0.5, 0),
                        0.5,
                        1,
                        facecolor=f"#{mr:02X}{mg:02X}{mb:02X}",
                        linewidth=0,
                    )
                )
                # Vertical divider
                ax.axvline(0.5, color="white", linewidth=0.8)

                # Name label below cell
                bright_match = self._calculate_brightness((mr, mg, mb))
                txt_col = "white" if bright_match < 140 else "#1A1A1A"
                ax.text(
                    0.75,
                    0.5,
                    name_str,
                    ha="center",
                    va="center",
                    fontsize=5.5,
                    color=txt_col,
                    multialignment="center",
                )

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Cross-vocabulary figure saved: {save_path}")
        if show:
            plt.show()
        return fig


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
