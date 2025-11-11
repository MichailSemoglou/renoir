#!/usr/bin/env python3
"""
Simple verification script to check that all renoir modules can be imported
and basic functionality works.
"""

import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from renoir import ArtistAnalyzer, quick_analysis, check_visualization_support
        from renoir.color import ColorExtractor, ColorAnalyzer, ColorVisualizer
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without requiring dataset download."""
    print("\nTesting basic functionality...")
    try:
        from renoir.color import ColorExtractor, ColorAnalyzer
        import numpy as np

        extractor = ColorExtractor()
        analyzer = ColorAnalyzer()

        # Test color conversions
        hsv = analyzer.rgb_to_hsv((255, 0, 0))
        assert hsv[0] >= 0 and hsv[0] <= 360
        assert hsv[1] >= 0 and hsv[1] <= 100
        assert hsv[2] >= 0 and hsv[2] <= 100

        # Test RGB to hex
        hex_color = extractor.rgb_to_hex((255, 0, 0))
        assert hex_color == '#ff0000'

        # Test hex to RGB
        rgb = extractor.hex_to_rgb('#ff0000')
        assert rgb == (255, 0, 0)

        # Test palette statistics
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        stats = analyzer.analyze_palette_statistics(colors)
        assert 'mean_saturation' in stats
        assert 'mean_value' in stats

        # Test color diversity
        diversity = analyzer.calculate_color_diversity(colors)
        assert 0 <= diversity <= 1

        print("✓ Basic functionality tests passed")
        return True

    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization_availability():
    """Test visualization library availability."""
    print("\nTesting visualization availability...")
    try:
        from renoir import check_visualization_support
        available = check_visualization_support()
        if available:
            print("✓ Visualization libraries available")
        else:
            print("⚠ Visualization libraries not available (optional)")
        return True
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        return False


def test_class_methods():
    """Test that all advertised methods exist."""
    print("\nTesting class methods...")
    try:
        from renoir import ArtistAnalyzer
        from renoir.color import ColorExtractor, ColorAnalyzer, ColorVisualizer

        analyzer = ArtistAnalyzer()

        # Check ArtistAnalyzer methods
        required_methods = [
            'extract_artist_works',
            'analyze_genres',
            'analyze_styles',
            'analyze_temporal_distribution',
            'get_work_summary',
            '_check_visualization_available',
            'plot_genre_distribution',
            'plot_style_distribution',
            'compare_artists_genres',
            'create_artist_overview'
        ]

        for method in required_methods:
            if not hasattr(analyzer, method):
                print(f"✗ Missing method: ArtistAnalyzer.{method}")
                return False

        # Check ColorExtractor methods
        extractor = ColorExtractor()
        extractor_methods = [
            'extract_dominant_colors',
            'extract_palette_from_artwork',
            'extract_average_color',
            'rgb_to_hex',
            'hex_to_rgb',
            'palette_to_dict',
            'export_palette_css',
            'export_palette_json'
        ]

        for method in extractor_methods:
            if not hasattr(extractor, method):
                print(f"✗ Missing method: ColorExtractor.{method}")
                return False

        # Check ColorAnalyzer methods
        color_analyzer = ColorAnalyzer()
        analyzer_methods = [
            'rgb_to_hsv',
            'hsv_to_rgb',
            'rgb_to_hsl',
            'hsl_to_rgb',
            'analyze_palette_statistics',
            'calculate_color_diversity',
            'calculate_saturation_score',
            'calculate_brightness_score',
            'compare_palettes',
            'classify_color_temperature',
            'analyze_color_temperature_distribution',
            'detect_complementary_colors',
            'calculate_contrast_ratio'
        ]

        for method in analyzer_methods:
            if not hasattr(color_analyzer, method):
                print(f"✗ Missing method: ColorAnalyzer.{method}")
                return False

        print("✓ All required methods exist")
        return True

    except Exception as e:
        print(f"✗ Method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Renoir Installation Verification")
    print("=" * 60)

    tests = [
        test_imports,
        test_basic_functionality,
        test_visualization_availability,
        test_class_methods,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if all(results):
        print("\n✓ All verification tests passed!")
        print("The package is ready for use.")
        return 0
    else:
        print("\n⚠ Some tests failed.")
        print("Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
