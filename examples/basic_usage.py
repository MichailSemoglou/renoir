"""
Basic usage examples for the renoir package.

This script demonstrates the main functionality and can be used
for classroom demonstrations.
"""

from renoir import ArtistAnalyzer, quick_analysis

def example_1_quick_analysis():
    """Simplest way to analyze an artist."""
    print("=" * 50)
    print("Example 1: Quick Analysis")
    print("=" * 50)
    quick_analysis('pierre-auguste-renoir')

def example_2_programmatic_access():
    """Using the analyzer class for more control."""
    print("\n" + "=" * 50)
    print("Example 2: Programmatic Access")
    print("=" * 50)
    
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('claude-monet')
    genres = analyzer.analyze_genres(works)
    
    print(f"\nClaude Monet created works in {len(genres)} different genres:")
    for genre, count in genres.items():
        print(f"  {genre}: {count} works")

def example_3_compare_artists():
    """Compare genre distributions across artists."""
    print("\n" + "=" * 50)
    print("Example 3: Compare Multiple Artists")
    print("=" * 50)
    
    analyzer = ArtistAnalyzer()
    artists = ['pierre-auguste-renoir', 'claude-monet', 'edgar-degas']
    
    for artist in artists:
        works = analyzer.extract_artist_works(artist)
        print(f"\n{artist}: {len(works)} works")

def example_4_list_artists():
    """List available artists."""
    print("\n" + "=" * 50)
    print("Example 4: List Available Artists")
    print("=" * 50)
    
    analyzer = ArtistAnalyzer()
    artists = analyzer.list_artists(limit=20)
    
    print(f"\nFirst 20 artists in the dataset:")
    for i, artist in enumerate(artists, 1):
        print(f"  {i}. {artist}")

def example_5_visualization_demo():
    """Demonstrate visualization capabilities."""
    print("\n" + "=" * 50)
    print("Example 5: Visualization Demo")
    print("=" * 50)
    
    from renoir import check_visualization_support
    
    # Check if visualization is available
    if check_visualization_support():
        print("\nCreating sample visualizations...")
        print("(Plots will appear in separate windows)")
        
        analyzer = ArtistAnalyzer()
        
        # Demo quick analysis with plots
        print("\nQuick analysis with visualizations:")
        quick_analysis('pierre-auguste-renoir', show_plots=True)
        
    else:
        print("\n❌ Visualization libraries not installed.")
        print("Install with: pip install 'renoir[visualization]'")
        print("\nAvailable visualization methods:")
        analyzer = ArtistAnalyzer()
        viz_methods = [
            'plot_genre_distribution',
            'plot_style_distribution', 
            'compare_artists_genres',
            'create_artist_overview'
        ]
        for method in viz_methods:
            available = "✅" if hasattr(analyzer, method) else "❌"
            print(f"  {available} {method}")

if __name__ == "__main__":
    # Run all examples
    example_1_quick_analysis()
    example_2_programmatic_access()
    example_3_compare_artists()
    example_4_list_artists()
    example_5_visualization_demo()
    
    print("\n" + "=" * 50)
    print("🎉 All examples complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  - Try the visualization_examples.py for more advanced plotting")
    print("  - Explore different artists and create your own analyses")
    print("  - Use renoir in your computational design or digital humanities projects!")
