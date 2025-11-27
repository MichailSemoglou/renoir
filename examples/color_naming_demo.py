#!/usr/bin/env python3
"""
ColorNamer Demo Script

Demonstrates the color naming capabilities of the Renoir package.
Run this script to see evocative color names in action!
"""

from renoir.color import ColorNamer


def main():
    print("\n" + "=" * 70)
    print("  🎨 Renoir ColorNamer Demo - Evocative Color Naming")
    print("=" * 70 + "\n")

    # Initialize with artist vocabulary
    namer = ColorNamer(vocabulary="artist")

    # Demo 1: Single color naming
    print("1. BASIC COLOR NAMING")
    print("-" * 70)
    test_colors = [
        ((255, 87, 51), "Orange-red"),
        ((0, 49, 83), "Deep blue"),
        ((204, 119, 34), "Yellow-brown"),
        ((64, 130, 109), "Blue-green"),
    ]

    for rgb, description in test_colors:
        result = namer.name(rgb, return_metadata=True)
        print(f"\nRGB {rgb} ({description})")
        print(f"  → {result['name']}")
        if result.get("ci_name"):
            print(f"     Color Index: {result['ci_name']}")
        print(f"     Family: {result['family']}")

    # Demo 2: Compare vocabularies
    print("\n\n2. COMPARING VOCABULARIES")
    print("-" * 70)
    test_color = (214, 138, 89)
    print(f"RGB {test_color} named across vocabularies:\n")

    for vocab in ColorNamer.available_vocabularies():
        namer.set_vocabulary(vocab)
        name = namer.name(test_color)
        print(f"  {vocab.upper():10} → {name}")

    # Demo 3: Palette naming
    print("\n\n3. NAMING A COLOR PALETTE")
    print("-" * 70)
    namer.set_vocabulary("artist")
    palette = [
        (255, 227, 3),  # Bright yellow
        (233, 116, 81),  # Orange-red
        (65, 102, 245),  # Blue
        (80, 125, 42),  # Green
        (138, 51, 36),  # Dark red
    ]

    print("Impressionist-inspired palette:\n")
    names = namer.name_palette(palette, return_metadata=True)
    for i, (rgb, meta) in enumerate(zip(palette, names), 1):
        print(f"{i}. {meta['name']}")
        print(f"   RGB: {rgb} | Hex: {meta['hex']}")
        if meta.get("ci_name"):
            print(f"   Pigment: {meta['ci_name']}")
        print()

    # Demo 4: Finding physical pigments
    print("\n4. DIGITAL-TO-PHYSICAL PIGMENT MATCHING")
    print("-" * 70)
    digital_color = (100, 150, 220)
    pigment = namer.closest_pigment(digital_color)

    print(f"Digital color: RGB {digital_color}")
    print(f"\nClosest physical pigment:")
    print(f"  Name: {pigment['name']}")
    print(f"  Color Index: {pigment['ci_name']}")
    print(f"  Hex: {pigment['hex']}")
    print(f"  Distance: {pigment['distance']:.3f} (perceptual)")
    if pigment.get("description"):
        print(f"  Description: {pigment['description']}")

    # Demo 5: Vocabulary statistics
    print("\n\n5. VOCABULARY INFORMATION")
    print("-" * 70)
    info = namer.get_vocabulary_info()
    print(f"Artist Vocabulary Statistics:")
    print(f"  Total colors: {info['count']}")
    print(f"  Colors with CI names: {info['ci_names']}")
    print(f"\n  Color families:")
    for family, count in sorted(
        info["families"].items(), key=lambda x: x[1], reverse=True
    ):
        print(f"    {family}: {count}")

    print("\n" + "=" * 70)
    print("✓ Demo complete! Try the Jupyter notebook for visualizations.")
    print("  → examples/color_analysis/11_color_naming.ipynb")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
