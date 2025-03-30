# ChromaDesk

![ChromaDesk Logo](data/icons/io.github.anantdark.chromadesk.png)

A modern wallpaper management application for Linux/GNOME desktop environments. ChromaDesk automatically fetches and applies beautiful images from Bing's daily wallpapers or your own custom sources.

## Features

- **Daily Bing Wallpapers**: Automatically fetch and apply the Bing image of the day
- **Custom Image Sources**: Add your own URLs or local directories as image sources
- **Scheduling**: Configure automatic updates using systemd timers
- **History Management**: Browse and reapply previously downloaded wallpapers
- **Localization**: Set your preferred Bing region for region-specific images
- **Modern UI**: Clean, intuitive Qt-based interface
- **Minimal Resource Usage**: Efficient background operation with minimal system impact
- **Standalone Executable**: Run without installation (portable option)

## Installation

### Option 1: Using pip (Python Package)

```bash
# Install from PyPI
pip install chromadesk

# Or install in development mode from source
git clone https://github.com/anantdark/chromadesk.git
cd chromadesk
pip install -e .
```

### Option 2: Using Standalone Executable or AppImage (No Installation Required)

1. Download the latest `chromadesk` executable or AppImage from the [Releases](https://github.com/anantdark/chromadesk/releases) page
2. Make it executable:
   
   ```bash
   chmod +x chromadesk-x.y.z-x86_64.AppImage
   # or
   chmod +x chromadesk
   ```
3. Run it:
   
   ```bash
   ./chromadesk-x.y.z-x86_64.AppImage
   # or
   ./chromadesk
   ```

### Option 3: Build from Source

```bash
# Clone the repository
git clone https://github.com/anantdark/chromadesk.git
cd chromadesk

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run the application
python -m chromadesk
```

## Usage

### GUI Application

Launch ChromaDesk from your applications menu or by running:

```bash
chromadesk
```

From the main interface, you can:

- View and apply the current Bing wallpaper
- Browse your wallpaper history
- Configure automatic updates
- Set up custom image sources
- Manage application settings

### Command-line Usage

ChromaDesk also supports headless operation for automated updates:

```bash
# Update wallpaper using current settings
python -m chromadesk --update

# List all available options
python -m chromadesk --help
```

### Automatic Updates

To enable automatic daily updates:

1. Open ChromaDesk
2. Go to Settings
3. Check "Enable daily updates"
4. Select your preferred update time
5. Click "Save"

## System Integration

ChromaDesk integrates with systemd for scheduled operations:

- **Timer Service**: `chromadesk-daily.timer` - Controls when updates occur
- **Service Unit**: `chromadesk-daily.service` - Performs the actual update

The application will install and configure these units automatically when you enable scheduled updates.

## Building the Standalone Executable or AppImage

The project includes a build script that simplifies the process of creating a standalone executable or AppImage:

```bash
# Make the build script executable (if not already)
chmod +x build.sh

# Run the build script with default options (creates standalone executable)
./build.sh

# Build an AppImage
./build.sh --appimage

# Get help on available options
./build.sh --help
```

The script will:

1. Create/activate a virtual environment
2. Install required dependencies
3. Build a standalone executable using PyInstaller
4. Optionally create an AppImage with proper desktop integration
5. Place the built artifacts in the appropriate directories

After building, you can run the application with:

```bash
# For standalone executable
./dist/usr/bin/chromadesk

# For AppImage
./chromadesk-x.y.z-x86_64.AppImage
```

### Build Script Options

The build script (`build.sh`) automates the entire build process with a simple interface. It:

- Verifies your environment is properly set up
- Manages the Python virtual environment
- Installs the required build tools
- Creates a standalone executable with all dependencies included
- Generates proper desktop integration files
- Optionally creates an AppImage compatible with AppImageLauncher

Available options:

- `--help` or `-h`: Show help information
- `--version-update VER`: Update version numbers to specified version
- `--build-only`: Update version numbers without building
- `--appimage`: Create an AppImage after building the executable

### Updating the Version

To update the version of the application before building:

```bash
# Update version and build the executable
./build.sh --version-update 0.2.0

# Update version, build executable and create AppImage
./build.sh --version-update 0.2.0 --appimage

# Update version only, without building
./build.sh --version-update 0.2.0 --build-only
```

This will update the version number in both:

- `chromadesk/__init__.py`
- `pyproject.toml`

## Testing

ChromaDesk includes a test suite to ensure functionality works as expected:

```bash
# Run all tests
python -m unittest discover tests

# Run a specific test file
python -m unittest tests.test_basics
```

## Troubleshooting

### Mesa Intel Graphics Warning

If you see a message like:

```
MESA-INTEL: warning: Performance support disabled, consider sysctl dev.i915.perf_stream_paranoid=0
```

This is a warning from the Intel graphics driver and doesn't affect functionality. You can:

1. **Ignore it**: The warning doesn't affect the application's functionality
2. **Suppress it temporarily**: Run the application with the environment variable:
   
   ```bash
   MESA_DEBUG=silent python -m chromadesk
   ```
3. **Fix it permanently**: If you have administrator privileges, you can set:
   
   ```bash
   sudo sysctl dev.i915.perf_stream_paranoid=0
   ```
   
   To make the change permanent, add the following line to `/etc/sysctl.conf`:
   
   ```
   dev.i915.perf_stream_paranoid=0
   ```

## Requirements

- Python 3.8+
- PySide6 (Qt for Python)
- Requests
- Pillow
- GNOME desktop environment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to this project.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## Author

Anant Patel - [GitHub](https://github.com/anantdark)
