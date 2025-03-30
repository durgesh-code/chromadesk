# Contributing to ChromaDesk

Thank you for your interest in contributing to ChromaDesk! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. Everyone is welcome regardless of their background or experience level.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine
3. **Create a virtual environment** and install the project in development mode:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```
4. **Create a new branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. **Make your changes**: Implement your feature or fix the bug
2. **Run tests**: Make sure your changes don't break existing functionality
   ```bash
   python -m unittest discover tests
   ```
3. **Commit your changes** with a descriptive commit message
4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** on GitHub from your fork to the main repository

## Code Style

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
* Use clear, descriptive variable and function names
* Write docstrings for all functions, classes, and modules
* Keep lines under 100 characters when possible

## Testing

* Add tests for new functionality
* Make sure all tests pass before submitting a pull request
* If you're fixing a bug, add a test that would have caught the bug

## Versioning

ChromaDesk follows [Semantic Versioning](https://semver.org/):

* **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
* Increment MAJOR for incompatible API changes
* Increment MINOR for new functionality in a backward compatible manner
* Increment PATCH for backward compatible bug fixes

To update the version number before building:

```bash
# Update version and build the executable
./build.sh --version-update 0.2.0

# Update version, build executable and create AppImage
./build.sh --version-update 0.2.0 --appimage

# Update version only, without building
./build.sh --version-update 0.2.0 --build-only
```

This will ensure version numbers are synchronized in both `chromadesk/__init__.py` and `pyproject.toml`.

## Building and Packaging

The build script supports multiple build options:

```bash
# Basic build using current version
./build.sh

# Create an AppImage (recommended for distribution)
./build.sh --appimage

# Get help on build options
./build.sh --help
```

### Building for Distribution

When preparing a release for distribution:

1. **Update the version** using `--version-update`
2. **Create an AppImage** using `--appimage`
3. **Test the AppImage** on a clean system if possible
4. **Create a GitHub release** with the AppImage attached

AppImages are the recommended distribution format for Linux users as they:
- Work on most Linux distributions without installation
- Integrate with the desktop environment
- Can be managed with AppImageLauncher
- Include all dependencies in a single file

The executable and related files will be placed in the `dist/` directory, and the AppImage will be created in the project root.

## Documentation

If you add new features, please update the documentation accordingly. This includes:

* Code comments and docstrings
* README.md updates if needed
* Any new command line options or configuration settings

## Submitting Pull Requests

When submitting a pull request:

1. Provide a clear description of the changes
2. Link any related issues
3. Include screenshots for UI changes if applicable
4. Ensure all tests pass
5. Make sure the code follows our style guidelines
6. Update version information if necessary

## Questions?

If you have any questions or need help, feel free to open an issue on GitHub.

Thank you for contributing to ChromaDesk! 