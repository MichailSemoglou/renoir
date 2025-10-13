# Setup Guide for JOSS Submission

This guide will help you prepare and submit the `renoir` package to JOSS (Journal of Open Source Software).

## ✅ Files Created

Your package now has the proper structure for JOSS submission with comprehensive visualization capabilities:

```
renoir/
├── renoir/                     # Main package directory
│   ├── __init__.py            # Package initialization with visualization support
│   └── analyzer.py            # Core functionality + 4 visualization methods
├── examples/                  # Example scripts
│   ├── basic_usage.py         # Updated with visualization demo
│   └── visualization_examples.py # Comprehensive visualization examples
├── tests/                     # Unit tests
│   └── test_analyzer.py       # Updated tests including visualization tests
├── README.md                  # Updated main documentation
├── FEATURE_GUIDE.md           # Comprehensive feature documentation
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Contribution guidelines
├── paper.md                   # JOSS paper (main submission file)
├── paper.bib                  # Bibliography for JOSS paper
├── pyproject.toml             # Updated package configuration with viz dependencies
├── requirements.txt           # Updated with visualization dependencies
└── .gitignore                 # Git ignore file

New Visualization Features:
✨ plot_genre_distribution()    # Bar charts
✨ plot_style_distribution()    # Pie charts
✨ compare_artists_genres()     # Multi-artist comparisons
✨ create_artist_overview()     # 4-panel comprehensive analysis
✨ Enhanced quick_analysis()    # Now with optional visualizations
```

## 📝 Before You Push to GitHub

### 1. Update Your Information

Edit these files with your actual information:

**pyproject.toml** (line 10):

```toml
{name = "Michail Semoglou", email = "your.email@university.edu"}
```

**pyproject.toml** (lines 33-36):

```toml
Homepage = "https://github.com/YOURUSERNAME/renoir"
Documentation = "https://github.com/YOURUSERNAME/renoir#readme"
Repository = "https://github.com/YOURUSERNAME/renoir"
"Bug Tracker" = "https://github.com/YOURUSERNAME/renoir/issues"
```

**paper.md** (lines 13-16):

```yaml
- name: Michail Semoglou
  orcid: 0000-0000-0000-0000 # Get yours at https://orcid.org
  affiliation: 1
# Update affiliation with your university/department
```

**README.md** (multiple locations):

- Update GitHub URLs from `yourusername` to your actual username
- Update contact email

### 2. Test the Package Locally

#### Basic Testing

```bash
# Navigate to your package directory
cd "/Users/michailsemoglou/Documents/Python_M3/renoir"

# Install in development mode
pip install -e .

# Run the basic example
python examples/basic_usage.py

# Run tests (optional - requires pytest)
pip install pytest
pytest tests/
```

#### Visualization Testing

```bash
# Install with visualization support
pip install -e .[visualization]

# Test visualization capabilities
python -c "from renoir import check_visualization_support; check_visualization_support()"

# Run visualization examples (will create plot windows)
python examples/visualization_examples.py

# Test quick analysis with plots
python -c "from renoir import quick_analysis; quick_analysis('pablo-picasso', show_plots=True)"
```

#### Complete Feature Test

```bash
# This will test all 9 test cases including new visualization tests
pytest tests/ -v

# Expected output: 9 passed tests including:
# ✅ Basic analysis tests (6)
# ✅ Visualization support tests (3)
```

### 3. Initialize Git Repository (if not already done)

```bash
cd "/Users/michailsemoglou/Library/Mobile Documents/com~apple~CloudDocs/Documents/Research/renoir"
git init
git add .
git commit -m "Initial commit: JOSS-ready package structure"
```

### 4. Create GitHub Repository

1. Go to https://github.com/new
2. Name it: `renoir`
3. Description: "A pedagogical tool for analyzing artist-specific works from WikiArt"
4. **Keep it public** (required for JOSS)
5. Don't initialize with README (you already have one)
6. Click "Create repository"

### 5. Push to GitHub

```bash
# Add your GitHub repository as remote (replace YOURUSERNAME)
git remote add origin https://github.com/YOURUSERNAME/renoir.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🚀 Submit to JOSS

### Before Submission

1. **Create a release** on GitHub:

   - Go to your repo → Releases → Create a new release
   - Tag: `v0.1.0`
   - Title: `Initial Release v0.1.0`
   - Description: "Educational tool for analyzing WikiArt dataset"

2. **Get your ORCID** (if you don't have one):
   - Visit https://orcid.org
   - Create a free account
   - Update `paper.md` with your ORCID

### Submission Process

1. Go to https://joss.theoj.org/papers/new
2. Enter your repository URL: `https://github.com/YOURUSERNAME/renoir`
3. JOSS will automatically find your `paper.md`
4. Fill in the submission form
5. Submit!

### What JOSS Reviewers Will Check

- ✅ Software functionality (does it work?)
- ✅ Documentation quality (README, examples)
- ✅ Software paper (`paper.md`)
- ✅ Tests (basic tests are sufficient)
- ✅ License (MIT ✓)
- ✅ Statement of need (educational focus ✓)

## 📚 Optional Improvements

Before or after submission, you might want to add:

1. **Jupyter notebook example** in `examples/`:

   - More interactive for students
   - Show visualizations with matplotlib

2. **More tests** in `tests/`:

   - Edge cases
   - Performance tests

3. **Documentation site** (e.g., with Sphinx or MkDocs)

4. **CI/CD** with GitHub Actions:
   - Automated testing
   - Code quality checks

## 🎯 JOSS Review Timeline

- Submission → Editor assignment: ~1 week
- Review process: 2-3 months
- Acceptance → Publication: ~1 week

## 📧 Need Help?

- JOSS documentation: https://joss.readthedocs.io
- JOSS example papers: https://joss.theoj.org/papers
- Questions: Open an issue on GitHub

## 🎓 Using in Your Teaching

Once published:

- Add DOI badge to README
- Share with computational design community
- Create classroom assignments based on it
- Collect student feedback for future versions

Good luck with your submission! 🚀
