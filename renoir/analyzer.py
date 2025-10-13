"""
Core analysis functions for extracting and analyzing artist works from WikiArt.
"""

from datasets import load_dataset
from collections import Counter
from typing import List, Dict, Optional

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class ArtistAnalyzer:
    """
    A class for analyzing works by specific artists in the WikiArt dataset.
    
    This tool is designed for educational use in computational design and 
    digital humanities courses, providing students with hands-on experience
    in working with cultural datasets.
    
    Attributes:
        dataset: The loaded WikiArt dataset
        artist_names: List of all available artist names
    """
    
    def __init__(self):
        """Initialize the analyzer by loading the WikiArt dataset."""
        print("Loading WikiArt dataset...")
        self.dataset = load_dataset("huggan/wikiart")
        self.artist_names = self.dataset['train'].features['artist'].names
        self.genre_names = self.dataset['train'].features['genre'].names
        self.style_names = self.dataset['train'].features['style'].names
    
    def get_artist_index(self, artist_name: str) -> Optional[int]:
        """
        Get the index of an artist by name.
        
        Args:
            artist_name: The artist's name (e.g., 'pierre-auguste-renoir')
            
        Returns:
            The artist's index, or None if not found
        """
        try:
            return self.artist_names.index(artist_name)
        except ValueError:
            print(f"Artist '{artist_name}' not found in dataset.")
            print(f"Available artists: {len(self.artist_names)}")
            return None
    
    def extract_artist_works(self, artist_name: str) -> List[Dict]:
        """
        Extract all works by a specific artist.
        
        Args:
            artist_name: The artist's name (e.g., 'pierre-auguste-renoir')
            
        Returns:
            List of artwork dictionaries for the specified artist
        """
        artist_index = self.get_artist_index(artist_name)
        if artist_index is None:
            return []
        
        print(f"\nExtracting works by {artist_name} (index: {artist_index})...")
        works = [example for example in self.dataset['train'] 
                if example['artist'] == artist_index]
        
        print(f"Found {len(works)} works by {artist_name}")
        return works
    
    def analyze_genres(self, works: List[Dict]) -> Dict[str, int]:
        """
        Analyze the distribution of genres in a collection of works.
        
        Args:
            works: List of artwork dictionaries
            
        Returns:
            Dictionary mapping genre names to counts
        """
        genre_counts = Counter(work['genre'] for work in works)
        return {self.genre_names[genre_id]: count 
                for genre_id, count in genre_counts.items()}
    
    def analyze_styles(self, works: List[Dict]) -> Dict[str, int]:
        """
        Analyze the distribution of styles in a collection of works.
        
        Args:
            works: List of artwork dictionaries
            
        Returns:
            Dictionary mapping style names to counts
        """
        style_counts = Counter(work['style'] for work in works)
        return {self.style_names[style_id]: count 
                for style_id, count in style_counts.items()}
    
    def print_analysis(self, artist_name: str) -> None:
        """
        Print a complete analysis of an artist's works.
        
        This is a convenience method for educational demonstrations.
        
        Args:
            artist_name: The artist's name (e.g., 'pierre-auguste-renoir')
        """
        works = self.extract_artist_works(artist_name)
        if not works:
            return
        
        # Analyze genres
        genres = self.analyze_genres(works)
        print("\nGenre distribution:")
        for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
            print(f"  {genre}: {count}")
        
        # Analyze styles
        styles = self.analyze_styles(works)
        print("\nStyle distribution:")
        for style, count in sorted(styles.items(), key=lambda x: x[1], reverse=True):
            print(f"  {style}: {count}")
        
        # Show examples
        print("\nExample works:")
        for i, work in enumerate(works[:5]):
            print(f"\n  Work {i+1}:")
            print(f"    Genre: {self.genre_names[work['genre']]}")
            print(f"    Style: {self.style_names[work['style']]}")
    
    def list_artists(self, limit: Optional[int] = None) -> List[str]:
        """
        List all available artists in the dataset.
        
        Args:
            limit: Optional limit on number of artists to return
            
        Returns:
            List of artist names
        """
        artists = self.artist_names[:limit] if limit else self.artist_names
        return artists
    
    def _check_visualization_available(self) -> bool:
        """
        Check if visualization libraries are available.
        
        Returns:
            True if matplotlib and seaborn are available, False otherwise
        """
        if not VISUALIZATION_AVAILABLE:
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir[visualization]'")
            return False
        return True
    
    def plot_genre_distribution(self, artist_name: str, figsize: tuple = (12, 6), 
                               save_path: Optional[str] = None) -> None:
        """
        Create a bar plot of genre distribution for an artist.
        
        Args:
            artist_name: The artist's name
            figsize: Figure size as (width, height)
            save_path: Optional path to save the plot
        """
        if not self._check_visualization_available():
            return
            
        works = self.extract_artist_works(artist_name)
        if not works:
            return
            
        genres = self.analyze_genres(works)
        
        plt.figure(figsize=figsize)
        genre_names = list(genres.keys())
        counts = list(genres.values())
        
        bars = plt.bar(genre_names, counts, color='skyblue', alpha=0.8)
        plt.title(f"Genre Distribution: {artist_name.replace('-', ' ').title()}", 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Genre', fontsize=12)
        plt.ylabel('Number of Works', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def plot_style_distribution(self, artist_name: str, figsize: tuple = (10, 6),
                               save_path: Optional[str] = None) -> None:
        """
        Create a pie chart of style distribution for an artist.
        
        Args:
            artist_name: The artist's name
            figsize: Figure size as (width, height)
            save_path: Optional path to save the plot
        """
        if not self._check_visualization_available():
            return
            
        works = self.extract_artist_works(artist_name)
        if not works:
            return
            
        styles = self.analyze_styles(works)
        
        plt.figure(figsize=figsize)
        
        # Create pie chart
        wedges, texts, autotexts = plt.pie(styles.values(), labels=styles.keys(), 
                                          autopct='%1.1f%%', startangle=90,
                                          colors=plt.cm.Set3.colors)
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        plt.title(f"Style Distribution: {artist_name.replace('-', ' ').title()}", 
                 fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def compare_artists_genres(self, artist_names: List[str], figsize: tuple = (14, 8),
                              save_path: Optional[str] = None) -> None:
        """
        Create a grouped bar chart comparing genre distributions across artists.
        
        Args:
            artist_names: List of artist names to compare
            figsize: Figure size as (width, height)
            save_path: Optional path to save the plot
        """
        if not self._check_visualization_available():
            return
            
        # Collect data for all artists
        artist_data = {}
        all_genres = set()
        
        for artist in artist_names:
            works = self.extract_artist_works(artist)
            if works:
                genres = self.analyze_genres(works)
                artist_data[artist] = genres
                all_genres.update(genres.keys())
        
        if not artist_data:
            print("No data found for the specified artists.")
            return
        
        # Prepare data for plotting
        all_genres = sorted(list(all_genres))
        x_pos = range(len(all_genres))
        bar_width = 0.8 / len(artist_names)
        
        plt.figure(figsize=figsize)
        
        colors = plt.cm.Set1.colors
        for i, (artist, genres) in enumerate(artist_data.items()):
            counts = [genres.get(genre, 0) for genre in all_genres]
            offset = (i - len(artist_names)/2 + 0.5) * bar_width
            
            plt.bar([x + offset for x in x_pos], counts, bar_width, 
                   label=artist.replace('-', ' ').title(), 
                   color=colors[i % len(colors)], alpha=0.8)
        
        plt.title('Genre Distribution Comparison', fontsize=16, fontweight='bold')
        plt.xlabel('Genre', fontsize=12)
        plt.ylabel('Number of Works', fontsize=12)
        plt.xticks(x_pos, all_genres, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def create_artist_overview(self, artist_name: str, figsize: tuple = (16, 10),
                              save_path: Optional[str] = None) -> None:
        """
        Create a comprehensive overview with multiple visualizations for an artist.
        
        Args:
            artist_name: The artist's name
            figsize: Figure size as (width, height)
            save_path: Optional path to save the plot
        """
        if not self._check_visualization_available():
            return
            
        works = self.extract_artist_works(artist_name)
        if not works:
            return
            
        genres = self.analyze_genres(works)
        styles = self.analyze_styles(works)
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(f"Artistic Analysis: {artist_name.replace('-', ' ').title()}", 
                    fontsize=20, fontweight='bold')
        
        # Genre bar chart
        genre_names = list(genres.keys())
        genre_counts = list(genres.values())
        bars1 = ax1.bar(genre_names, genre_counts, color='lightcoral', alpha=0.8)
        ax1.set_title('Genre Distribution', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Number of Works')
        ax1.tick_params(axis='x', rotation=45)
        for bar, count in zip(bars1, genre_counts):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        # Style pie chart
        ax2.pie(styles.values(), labels=styles.keys(), autopct='%1.1f%%', 
               startangle=90, colors=plt.cm.Pastel1.colors)
        ax2.set_title('Style Distribution', fontsize=14, fontweight='bold')
        
        # Genre horizontal bar chart (sorted)
        sorted_genres = sorted(genres.items(), key=lambda x: x[1])
        genre_names_sorted = [item[0] for item in sorted_genres]
        genre_counts_sorted = [item[1] for item in sorted_genres]
        
        bars3 = ax3.barh(genre_names_sorted, genre_counts_sorted, color='lightblue', alpha=0.8)
        ax3.set_title('Genres (Sorted by Count)', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Number of Works')
        for bar, count in zip(bars3, genre_counts_sorted):
            ax3.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    str(count), ha='left', va='center', fontweight='bold')
        
        # Summary statistics
        ax4.axis('off')
        total_works = len(works)
        num_genres = len(genres)
        num_styles = len(styles)
        most_common_genre = max(genres.items(), key=lambda x: x[1])
        most_common_style = max(styles.items(), key=lambda x: x[1])
        
        summary_text = f"""
        SUMMARY STATISTICS
        
        Total Works: {total_works:,}
        Number of Genres: {num_genres}
        Number of Styles: {num_styles}
        
        Most Common Genre:
        {most_common_genre[0]} ({most_common_genre[1]} works)
        
        Most Common Style:
        {most_common_style[0]} ({most_common_style[1]} works)
        
        Genre Diversity:
        {(num_genres / total_works * 100):.1f}% of works span different genres
        """
        
        ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Overview saved to: {save_path}")
        
        plt.show()


def quick_analysis(artist_name: str, show_plots: bool = False) -> None:
    """
    Convenience function for quick artist analysis.
    
    This function is useful for classroom demonstrations and initial exploration.
    
    Args:
        artist_name: The artist's name (e.g., 'pierre-auguste-renoir')
        show_plots: If True, display visualizations (requires matplotlib)
    """
    analyzer = ArtistAnalyzer()
    analyzer.print_analysis(artist_name)
    
    if show_plots and VISUALIZATION_AVAILABLE:
        print("\nGenerating visualizations...")
        analyzer.plot_genre_distribution(artist_name, figsize=(10, 6))
        analyzer.plot_style_distribution(artist_name, figsize=(8, 6))
    elif show_plots and not VISUALIZATION_AVAILABLE:
        print("\nVisualization requested but libraries not available.")
        print("Install with: pip install 'renoir[visualization]'")
