"""
Visualization examples for the renoir package.

This script demonstrates how to create various visualizations
using the built-in plotting methods of the ArtistAnalyzer class.

To run these examples, you need to install the visualization dependencies:
pip install 'renoir[visualization]'
"""

from renoir import ArtistAnalyzer

def example_1_genre_bar_chart():
    """Create a bar chart of genre distribution for Renoir."""
    print("=" * 60)
    print("Example 1: Genre Distribution Bar Chart")
    print("=" * 60)
    
    analyzer = ArtistAnalyzer()
    analyzer.plot_genre_distribution('pierre-auguste-renoir')

def example_2_style_pie_chart():
    """Create a pie chart of style distribution for Picasso."""
    print("\n" + "=" * 60)
    print("Example 2: Style Distribution Pie Chart")
    print("=" * 60)
    
    analyzer = ArtistAnalyzer()
    analyzer.plot_style_distribution('pablo-picasso')

def example_3_compare_artists():
    """Compare genre distributions across multiple artists."""
    print("\n" + "=" * 60)
    print("Example 3: Compare Artists' Genre Distributions")
    print("=" * 60)
    
    analyzer = ArtistAnalyzer()
    artists = ['pierre-auguste-renoir', 'claude-monet', 'pablo-picasso']
    analyzer.compare_artists_genres(artists)

def example_4_comprehensive_overview():
    """Create a comprehensive overview for an artist."""
    print("\n" + "=" * 60)
    print("Example 4: Comprehensive Artist Overview")
    print("=" * 60)
    
    analyzer = ArtistAnalyzer()
    analyzer.create_artist_overview('vincent-van-gogh')

def example_5_save_visualizations():
    """Demonstrate saving visualizations to files."""
    print("\n" + "=" * 60)
    print("Example 5: Saving Visualizations")
    print("=" * 60)
    
    analyzer = ArtistAnalyzer()
    
    print("Creating and saving genre distribution...")
    analyzer.plot_genre_distribution('pierre-auguste-renoir', 
                                   save_path='renoir_genres.png')
    
    print("Creating and saving comprehensive overview...")
    analyzer.create_artist_overview('claude-monet', 
                                  save_path='monet_overview.png')

def example_6_classroom_exercise():
    """A typical classroom exercise comparing Impressionist artists."""
    print("\n" + "=" * 60)
    print("Example 6: Classroom Exercise - Impressionist Comparison")
    print("=" * 60)
    
    analyzer = ArtistAnalyzer()
    
    # Impressionist artists to compare
    impressionists = [
        'pierre-auguste-renoir',
        'claude-monet', 
        'edgar-degas',
        'camille-pissarro'
    ]
    
    print("Comparing genre distributions among Impressionist artists...")
    analyzer.compare_artists_genres(impressionists, figsize=(16, 10))
    
    print("\nCreating individual overviews...")
    for artist in impressionists[:2]:  # Just show first two to avoid too many plots
        analyzer.create_artist_overview(artist, figsize=(14, 8))

if __name__ == "__main__":
    print("Renoir Package - Visualization Examples")
    print("These examples demonstrate the visualization capabilities.")
    print("Each plot will open in a new window.\n")
    
    try:
        # Run all examples
        example_1_genre_bar_chart()
        input("\nPress Enter to continue to the next example...")
        
        example_2_style_pie_chart()
        input("\nPress Enter to continue to the next example...")
        
        example_3_compare_artists()
        input("\nPress Enter to continue to the next example...")
        
        example_4_comprehensive_overview()
        input("\nPress Enter to continue to the next example...")
        
        example_5_save_visualizations()
        input("\nPress Enter to continue to the final example...")
        
        example_6_classroom_exercise()
        
        print("\n" + "=" * 60)
        print("🎉 All visualization examples completed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have installed the visualization dependencies:")
        print("pip install 'renoir[visualization]'")