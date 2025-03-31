# chromadesk/core/wallpaper.py
"""
Handles setting the desktop wallpaper for GNOME environments,
adapting to different session types and available settings keys.
"""

import subprocess
import logging
from pathlib import Path
import shutil
import os

logger = logging.getLogger(__name__)

# Define GNOME settings schemas and keys
SCHEMA_BACKGROUND = "org.gnome.desktop.background"
KEY_PICTURE_URI = "picture-uri"
KEY_PICTURE_URI_DARK = "picture-uri-dark" # Existence is checked before use
KEY_PICTURE_OPTIONS = "picture-options"

# ==============================================================================
# Note: Requires notification sending functions to be defined above this point.
# These functions (_send_notification_notify2, _send_notification_dbus,
# send_notification) handle sending desktop notifications and are assumed
# to exist from previous versions or another part of the module.
# If they are not defined elsewhere, they need to be included here.
# Example placeholder (replace with actual functions if needed):
# def send_notification(title: str, message: str):
#     logger.warning("Notification sending not implemented in this snippet.")
# ==============================================================================


def _check_gsettings_key_exists(schema: str, key: str) -> bool:
    """
    Checks if a specific key exists within a gsettings schema using the CLI tool.

    Args:
        schema: The gsettings schema path (e.g., "org.gnome.desktop.background").
        key: The specific key name to check for (e.g., "picture-uri-dark").

    Returns:
        True if the key exists and can be listed, False otherwise.
    """
    # Ensure the command-line tool is available first
    if not shutil.which("gsettings"):
        logger.warning("Cannot check gsettings key: 'gsettings' command not found.")
        return False # Assume key doesn't exist if we can't check

    cmd = ['gsettings', 'list-keys', schema]
    try:
        # Execute 'gsettings list-keys <schema>'
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
        key_list = result.stdout.splitlines() # Get list of keys in the schema
        exists = key in key_list # Check if our target key is in the list
        logger.debug(f"Schema '{schema}' keys checked. Key '{key}' exists: {exists}")
        return exists
    except FileNotFoundError:
        # Defensive check, though shutil.which should catch it.
        logger.error(f"Command failed: '{cmd[0]}' not found during key check.")
        return False
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out while listing keys for schema '{schema}'.")
        return False
    except subprocess.CalledProcessError as e:
        # gsettings might fail if the schema itself doesn't exist
        logger.warning(f"Command failed while listing keys for schema '{schema}'. "
                       f"Maybe schema not installed? Stderr: {e.stderr.strip()}")
        return False # Failed to list keys, assume the specific key doesn't exist
    except Exception as e:
         logger.error(f"An unexpected error occurred checking gsettings keys: {e}")
         return False


def set_gnome_wallpaper(image_path: Path) -> bool:
    """
    Sets the GNOME desktop wallpaper using the gsettings command-line tool.

    This function adapts its behavior based on the desktop session type
    (X11 vs. Wayland/other) and the availability of the 'picture-uri-dark'
    gsettings key to maximize compatibility across different GNOME versions.

    Args:
        image_path: The absolute Path object pointing to the desired wallpaper image.

    Returns:
        True if the necessary gsettings commands were executed successfully,
        False otherwise. Note: Success indicates the commands ran without error,
        but doesn't guarantee the desktop visually updated if there are other
        desktop environment issues.
    """
    if not image_path.is_file():
        logger.error(f"Wallpaper image file not found: {image_path}")
        return False

    # Check if gsettings command exists early on
    if not shutil.which("gsettings"):
         logger.error("'gsettings' command not found. Cannot set GNOME wallpaper.")
         return False

    # Convert the Path object to an absolute file URI (e.g., "file:///...")
    try:
        abs_image_path = image_path.resolve(strict=True) # Ensures path exists
        file_uri = abs_image_path.as_uri()
    except FileNotFoundError:
         logger.error(f"Wallpaper image file not found (during resolve): {image_path}")
         return False
    except Exception as e:
         logger.error(f"Error resolving path or creating file URI for {image_path}: {e}")
         return False

    # --- Determine which keys need to be set based on environment ---
    session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown').lower()
    is_x11 = (session_type == 'x11')
    should_set_dark_uri = False # Default to not setting the dark URI

    if is_x11:
        # On X11, GNOME traditionally uses only picture-uri for both light/dark
        logger.info("X11 session detected. Will only set 'picture-uri'.")
    else:
        # On Wayland (or unknown sessions), check if the modern 'picture-uri-dark' exists
        logger.info(f"Session type '{session_type}' detected (or unknown). Checking for '{KEY_PICTURE_URI_DARK}'.")
        if _check_gsettings_key_exists(SCHEMA_BACKGROUND, KEY_PICTURE_URI_DARK):
            logger.info(f"Key '{KEY_PICTURE_URI_DARK}' found. Will set both light and dark URIs.")
            should_set_dark_uri = True
        else:
            logger.info(f"Key '{KEY_PICTURE_URI_DARK}' not found. Will only set 'picture-uri'.")

    # --- Build the list of commands to execute ---
    commands_to_run = [
        # 1. Set picture options (e.g., how the image is scaled)
        ['gsettings', 'set', SCHEMA_BACKGROUND, KEY_PICTURE_OPTIONS, 'zoom'], # 'zoom' is usually a good default
        # 2. Always set the primary picture URI
        ['gsettings', 'set', SCHEMA_BACKGROUND, KEY_PICTURE_URI, file_uri],
    ]

    # 3. Conditionally add the command for the dark URI if needed
    if should_set_dark_uri:
        commands_to_run.append(['gsettings', 'set', SCHEMA_BACKGROUND, KEY_PICTURE_URI_DARK, file_uri])

    logger.info(f"Attempting to set wallpaper using {len(commands_to_run)} gsettings command(s). Target URI: {file_uri}")

    # --- Execute the gsettings commands ---
    success = True
    for cmd in commands_to_run:
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            # Run the command, check for non-zero exit code, capture output
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            logger.debug(f"Command successful.") # Keep success log concise
        except FileNotFoundError:
            logger.error(f"Command failed: '{cmd[0]}' not found. Check PATH.")
            success = False
            break # Cannot continue if gsettings is missing
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            success = False
            break # Stop if a command hangs
        except subprocess.CalledProcessError as e:
            # This catches gsettings commands that exit with an error
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"  Return Code: {e.returncode}")
            logger.error(f"  Stderr: {e.stderr.strip()}")
            # If setting the main URI fails, no point setting dark. If options fail, maybe continue?
            # For simplicity, we break on the first error.
            success = False
            break
        except Exception as e:
             # Catch any other unexpected exceptions during subprocess execution
             logger.error(f"An unexpected error occurred running command {' '.join(cmd)}: {e}", exc_info=True)
             success = False
             break

    # Final status log
    if success:
        logger.info("Successfully executed necessary gsettings commands for wallpaper.")
    else:
        logger.error("Failed to execute all necessary gsettings commands for wallpaper.")

    return success