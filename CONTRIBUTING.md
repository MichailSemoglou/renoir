# Contributing to renoir

Thank you for your interest in contributing to `renoir`! This package is designed for educational purposes, and we welcome contributions that enhance its pedagogical value.

## Types of Contributions

We especially welcome:

1. **Pedagogical examples**: Classroom exercises, assignments, or demonstrations
2. **Documentation**: Improvements to explanations, examples, or tutorials
3. **Bug fixes**: Corrections to code issues
4. **Feature requests**: Ideas for new educational features

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/MichailSemoglou/renoir.git
   cd renoir
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```
4. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 conventions
- Use clear, descriptive variable names
- Write docstrings for all functions and classes
- Keep code simple and readable (remember: this is for students!)

### Testing

Run tests before submitting:

```bash
pytest tests/
```

### Documentation

- Update README.md if adding new features
- Include usage examples in docstrings
- Consider pedagogical context in documentation

### Building the Docs Locally

The `docs/_build/` directory is git-ignored and must be generated locally — never commit it.

```bash
# Install doc dependencies
pip install -e ".[dev]"

# Build HTML docs
cd docs
make html
# Output is in docs/_build/html/index.html

# Or, from the repo root:
sphinx-build -b html docs docs/_build/html
```

## Submitting Changes

1. Commit your changes:
   ```bash
   git commit -m "Add: brief description of changes"
   ```
2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Open a Pull Request with:
   - Clear description of changes
   - Pedagogical rationale (if applicable)
   - Any new dependencies or requirements

## Questions?

Open an issue for:

- Bug reports
- Feature suggestions
- Questions about contributing
- Ideas for classroom applications

## Code of Conduct

Be respectful, inclusive, and constructive. This is an educational project aimed at helping students learn.
