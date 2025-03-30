# chromadesk/chromadesk/core/wallpaper.py
import subprocess
import logging
from pathlib import Path
import shutil

logger = logging.getLogger()

# Define GNOME settings schemas and keys
SCHEMA_BACKGROUND = "org.gnome.desktop.background"
KEY_PICTURE_URI = "picture-uri"
KEY_PICTURE_URI_DARK = "picture-uri-dark" # Set both for light/dark theme consistency
KEY_PICTURE_OPTIONS = "picture-options" # Controls how image is scaled (e.g., 'zoom', 'scaled', 'centered')

def set_gnome_wallpaper(image_path: Path) -> bool:
    """
    Sets the GNOME desktop wallpaper using the gsettings command.

    Args:
        image_path (Path): The absolute path to the image file.

    Returns:
        bool: True if the wallpaper was set successfully, False otherwise.
    """
    if not image_path.is_file():
        logger.error(f"Wallpaper image file not found: {image_path}")
        return False

    # Check if gsettings command exists
    if not shutil.which("gsettings"):
         logger.error("'gsettings' command not found. Cannot set GNOME wallpaper.")
         # Consider notifying the user more explicitly in the UI later
         return False

    # Convert the Path object to a file URI (e.g., "file:///home/user/Pictures/image.jpg")
    # Ensure the path is absolute first
    try:
        abs_image_path = image_path.resolve(strict=True)
        file_uri = abs_image_path.as_uri()
    except FileNotFoundError:
         logger.error(f"Wallpaper image file not found (during resolve): {image_path}")
         return False
    except Exception as e:
         logger.error(f"Error resolving path or creating file URI for {image_path}: {e}")
         return False


    logger.info(f"Setting GNOME wallpaper to: {file_uri}")
    commands_to_run = [
        ['gsettings', 'set', SCHEMA_BACKGROUND, KEY_PICTURE_OPTIONS, 'zoom'], # or 'scaled', 'stretched'
        ['gsettings', 'set', SCHEMA_BACKGROUND, KEY_PICTURE_URI, file_uri],
    ]

    success = True
    for cmd in commands_to_run:
        try:
            # Run the command, capture output, check return code
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
            logger.debug(f"Command {' '.join(cmd)} successful. Output: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error(f"Command failed: '{cmd[0]}' not found.")
            success = False
            break # Stop if gsettings fails
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            success = False
            break
        except subprocess.CalledProcessError as e:
            # This catches non-zero exit codes
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"  Return Code: {e.returncode}")
            logger.error(f"  Stderr: {e.stderr.strip()}")
            logger.error(f"  Stdout: {e.stdout.strip()}")
            success = False
            break # Stop on first error
        except Exception as e:
             logger.error(f"An unexpected error occurred running command {' '.join(cmd)}: {e}")
             success = False
             break

    if success:
        logger.info("Successfully set GNOME wallpaper.")
    else:
        logger.error("Failed to set GNOME wallpaper.")

    return success

# Example Usage (can be tested independently)
if __name__ == "__main__":
    print("Testing GNOME Wallpaper Setter...")
    # WARNING: This will actually change your desktop wallpaper if it succeeds!

    # Option 1: Use one of the previously downloaded test images
    test_image_path = Path("./temp_downloads/test_bing.jpg").resolve()
    # Option 2: Specify a path to any other JPG/PNG on your system
    # test_image_path = Path.home() / "Pictures" / "my_other_wallpaper.jpg"

    if test_image_path.is_file():
        print(f"\nAttempting to set wallpaper to: {test_image_path}")
        set_success = set_gnome_wallpaper(test_image_path)
        print(f"Wallpaper set successfully: {set_success}")

        if set_success:
            print("\nCheck your desktop background!")
            print("(You might need to manually change it back later)")
        else:
            print("\nWallpaper setting failed. Check logs above for errors.")
    else:
        print(f"\nTest image not found: {test_image_path}")
        print("Please download an image first (e.g., run downloader.py) or specify a valid path.")
