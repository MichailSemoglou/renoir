from setuptools import setup, find_packages

setup(
    name="renoir-wikiart",
    version="3.3.0",
    packages=find_packages(exclude=['tests*', 'examples*', 'Research*', 'test_env*', 'Pierre-Auguste Renoir*', 'jose*']),
    package_data={
        'renoir': ['data/colors/*.json'],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "datasets>=2.0.0",
        "Pillow>=8.0.0",
        "numpy>=1.20.0",
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "jupyter>=1.0.0",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],
    },
)
