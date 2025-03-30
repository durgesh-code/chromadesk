# chromadesk/chromadesk/services/manager.py
import sys
import os
import logging
import subprocess
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Constants ---
SERVICE_NAME = "chromadesk-daily"
SERVICE_FILE = f"{SERVICE_NAME}.service"
TIMER_FILE = f"{SERVICE_NAME}.timer"
SYSTEMD_USER_DIR = Path.home() / ".config" / "systemd" / "user"
TEMPLATE_DIR = Path(__file__).parent / "templates" # Path relative to this file

# --- Helper Functions ---

def _run_systemctl(command: list, check: bool = False, capture: bool = False) -> subprocess.CompletedProcess | None:
    """Runs a systemctl --user command."""
    base_cmd = ['systemctl', '--user']
    full_cmd = base_cmd + command
    logger.debug(f"Running systemctl command: {' '.join(full_cmd)}")
    try:
        result = subprocess.run(
            full_cmd,
            check=check,            # Raise exception on non-zero exit code if True
            capture_output=capture, # Capture stdout/stderr if True
            text=True,              # Work with text streams
            timeout=10              # Prevent hanging
        )
        if capture:
            logger.debug(f"systemctl stdout: {result.stdout.strip()}")
            logger.debug(f"systemctl stderr: {result.stderr.strip()}")
        logger.debug(f"systemctl finished with code: {result.returncode}")
        return result
    except FileNotFoundError:
        logger.error("'systemctl' command not found. Cannot manage systemd units.")
        return None
    except subprocess.TimeoutExpired:
        logger.error(f"systemctl command timed out: {' '.join(full_cmd)}")
        return None
    except subprocess.CalledProcessError as e:
        # Error is logged automatically if check=True caused it
        if not check: # Log error if check was False but it still failed somehow
             logger.error(f"systemctl command failed: {' '.join(full_cmd)} (Code: {e.returncode})")
             if capture:
                 logger.error(f"  Stderr: {e.stderr.strip()}")
        return None # Indicate failure
    except Exception as e:
         logger.error(f"Unexpected error running systemctl: {e}", exc_info=True)
         return None

def _get_python_executable() -> str:
    """Gets the path to the currently running Python executable."""
    # sys.executable is usually reliable, especially in venvs
    path = sys.executable
    if not path:
         logger.warning("Could not determine Python executable path from sys.executable. Falling back to 'python3'.")
         path = "python3" # Less reliable fallback
    logger.debug(f"Using Python executable: {path}")
    return str(Path(path).resolve()) # Return absolute path

def _get_script_path() -> str:
    """Gets the absolute path to the headless.py script."""
    # Assumes headless.py is in the parent directory of this 'services' dir
    try:
        script_path = Path(__file__).parent.parent / "headless.py"
        abs_path = str(script_path.resolve(strict=True))
        logger.debug(f"Found headless script path: {abs_path}")
        return abs_path
    except FileNotFoundError:
         logger.error("headless.py not found relative to manager.py!")
         return "" # Should cause failure later

def _get_project_root() -> str:
     """Gets the absolute path to the project root directory."""
     # Assumes project root is the parent of the 'chromadesk' package directory
     # where headless.py resides (i.e., parent of parent of this file's dir)
     try:
        root_path = Path(__file__).parent.parent.parent
        abs_path = str(root_path.resolve(strict=True))
        logger.debug(f"Using project root (working directory): {abs_path}")
        return abs_path
     except Exception as e:
          logger.error(f"Could not determine project root directory: {e}")
          return "." # Fallback, might cause issues


def _get_dbus_address() -> str:
    """Gets the DBUS_SESSION_BUS_ADDRESS from the environment."""
    dbus_addr = os.environ.get("DBUS_SESSION_BUS_ADDRESS", "")
    if not dbus_addr:
        logger.warning("DBUS_SESSION_BUS_ADDRESS environment variable not found. Notifications from timer might fail.")
    else:
        logger.debug(f"Found DBUS_SESSION_BUS_ADDRESS: {dbus_addr}")
    return dbus_addr

# --- Public API ---

def _get_venv_path() -> str:
    """Gets the path to the active venv directory using sys.prefix."""
    try:
        # sys.prefix usually points to the venv directory when running inside one
        venv_path = Path(sys.prefix).resolve()

        # Basic sanity checks to see if it looks like a venv
        # Check for pyvenv.cfg or a common lib/pythonX.Y/site-packages structure
        is_likely_venv = (venv_path / "pyvenv.cfg").is_file() or \
                         list(venv_path.glob("lib/python*/site-packages"))

        # If it doesn't look like a venv or points to system paths, something is wrong
        if not is_likely_venv or str(venv_path).startswith(('/usr', '/System', '/Library')):
             logger.error(f"sys.prefix ({venv_path}) does not look like a virtualenv directory. Cannot reliably determine venv path.")
             # Provide more context for debugging
             logger.error(f"  sys.prefix = {sys.prefix}")
             logger.error(f"  sys.base_prefix = {sys.base_prefix}") # Often points to system python
             logger.error(f"  sys.executable = {sys.executable}")
             return "" # Return empty to signal failure

        abs_path = str(venv_path)
        logger.debug(f"Determined venv path using sys.prefix: {abs_path}")
        return abs_path
    except Exception as e:
         logger.error(f"Could not determine venv path using sys.prefix: {e}", exc_info=True)
         return ""

def _get_template_dir() -> Path:
    """Finds the template directory, checking near executable or in share dir."""
    # Path relative to this file (for development)
    dev_path = Path(__file__).parent / "templates"
    if dev_path.is_dir():
         logger.debug(f"Found templates in development path: {dev_path}")
         return dev_path

    # Path relative to installation prefix (for installed app/AppDir)
    # Assumes templates are installed to 'share/chromadesk/templates' relative to prefix
    try:
        prefix = Path(sys.prefix)
        installed_path = prefix / "share" / "chromadesk" / "templates"
        if installed_path.is_dir():
             logger.debug(f"Found templates in installed path: {installed_path}")
             return installed_path
    except Exception: # Catch errors if sys.prefix is weird
         pass

    logger.error("Template directory not found!")
    # Raise an error or return a Path that will fail later?
    raise FileNotFoundError("ChromaDesk systemd templates not found.")


def create_unit_files() -> bool:
    """Creates the .service and .timer files from templates."""
    logger.info("Creating systemd unit files...")
    # --- Add @@VENV_PATH@@ to placeholders ---
    placeholders = {
        "@@PYTHON_EXEC@@": _get_python_executable(),
        "@@SCRIPT_PATH@@": _get_script_path(),
        "@@WORKING_DIR@@": _get_project_root(),
        "@@DBUS_ADDRESS@@": _get_dbus_address(),
        "@@VENV_PATH@@": _get_venv_path(), # Add this line
    }

    # Check if paths were found (include venv_path check)
    if not all(placeholders.values()): # Check if any value is empty
         logger.error("Could not determine necessary paths (python, script, workdir, venv) for unit files. Aborting.")
         return False

    # Ensure systemd user directory exists
    try:
        TEMPLATE_DIR = _get_template_dir() # Use the helper function
        logger.debug(f"Ensured systemd user directory exists: {SYSTEMD_USER_DIR}")
    except FileNotFoundError:
         logger.critical("Cannot create unit files because template directory was not found.")
         return False

    files_to_create = {
        SERVICE_FILE: TEMPLATE_DIR / f"{SERVICE_FILE}.in",
        TIMER_FILE: TEMPLATE_DIR / f"{TIMER_FILE}.in",
    }

    all_success = True
    for filename, template_path in files_to_create.items():
        dest_path = SYSTEMD_USER_DIR / filename
        logger.debug(f"Processing template {template_path} to {dest_path}")
        try:
            if not template_path.is_file():
                logger.error(f"Template file not found: {template_path}")
                all_success = False
                continue # Skip to next file

            # Read template content
            content = template_path.read_text()

            # Substitute placeholders
            for key, value in placeholders.items():
                content = content.replace(key, value)

            # Write final unit file
            dest_path.write_text(content)
            logger.info(f"Successfully wrote unit file: {dest_path}")

        except OSError as e:
            logger.error(f"Failed to read template or write unit file {dest_path}: {e}")
            all_success = False
        except Exception as e:
             logger.error(f"Unexpected error processing template {template_path}: {e}", exc_info=True)
             all_success = False

    # Reload systemd daemon if files were possibly changed
    if all_success:
        logger.info("Reloading systemd user daemon...")
        result = _run_systemctl(['daemon-reload'])
        if result is None:
             logger.error("Failed to reload systemd daemon after creating unit files.")
             # This might not be fatal, but enabling might fail
             return False # Indicate potential issue
    else:
         logger.error("One or more unit files failed to be created.")

    return all_success

def enable_timer() -> bool:
    """Creates unit files and enables/starts the systemd timer."""
    logger.info(f"Enabling systemd timer: {TIMER_FILE}")
    # Ensure files are up-to-date first
    if not create_unit_files():
        logger.error("Failed to create necessary unit files. Cannot enable timer.")
        return False

    # Enable and start the timer immediately
    result = _run_systemctl(['enable', '--now', TIMER_FILE], check=True)
    if result is not None:
        logger.info(f"Systemd timer {TIMER_FILE} enabled and started successfully.")
        return True
    else:
        logger.error(f"Failed to enable/start systemd timer {TIMER_FILE}.")
        return False

def disable_timer() -> bool:
    """Disables and stops the systemd timer."""
    logger.info(f"Disabling systemd timer: {TIMER_FILE}")
    # Stop and disable the timer
    result = _run_systemctl(['disable', '--now', TIMER_FILE]) # Don't use check=True, disable fails if not enabled
    if result is not None: # Command ran successfully (even if it did nothing)
        logger.info(f"Systemd timer {TIMER_FILE} disabled and stopped.")
        # Optionally remove the files? Or leave them for easy re-enabling? Leave for now.
        # try:
        #     (SYSTEMD_USER_DIR / TIMER_FILE).unlink(missing_ok=True)
        #     (SYSTEMD_USER_DIR / SERVICE_FILE).unlink(missing_ok=True)
        #     _run_systemctl(['daemon-reload']) # Reload after removing
        # except OSError as e:
        #      logger.warning(f"Could not remove unit files: {e}")
        return True
    else:
        # Only log error if systemctl command itself failed (e.g., couldn't connect)
        if result is None: # Check if _run_systemctl indicated command failure
             logger.error(f"Failed to execute disable command for systemd timer {TIMER_FILE}.")
        return False

def is_timer_active() -> bool:
    """Checks if the timer unit is currently active."""
    logger.debug(f"Checking active state of timer: {TIMER_FILE}")
    result = _run_systemctl(['is-active', TIMER_FILE])
    # is-active returns 0 and prints "active" if active, non-zero otherwise
    # We check return code directly
    active = result is not None and result.returncode == 0
    logger.debug(f"Timer active state: {active}")
    return active

def is_timer_enabled() -> bool:
    """Checks if the timer unit is enabled to start on login."""
    logger.debug(f"Checking enabled state of timer: {TIMER_FILE}")
    result = _run_systemctl(['is-enabled', TIMER_FILE])
    # is-enabled returns 0 and prints "enabled" if enabled, 1 otherwise
    enabled = result is not None and result.returncode == 0
    logger.debug(f"Timer enabled state: {enabled}")
    return enabled


# Example Usage (can be tested manually, CAUTION: modifies systemd state)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - MANAGER_TEST - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
    print("--- Testing Systemd Service Manager ---")
    print(f"Systemd User Dir: {SYSTEMD_USER_DIR}")
    print(f"Service File: {SERVICE_FILE}")
    print(f"Timer File: {TIMER_FILE}")

    print("\n1. Creating unit files...")
    created = create_unit_files()
    print(f"   Success: {created}")
    if created:
         print(f"   Check files in: {SYSTEMD_USER_DIR}")

    print("\n2. Checking if timer is enabled (before enabling)...")
    enabled_before = is_timer_enabled()
    print(f"   Is Enabled: {enabled_before}")

    print("\n3. Checking if timer is active (before enabling)...")
    active_before = is_timer_active()
    print(f"   Is Active: {active_before}")

    if created: # Only try enabling if files were created
        print("\n4. Enabling timer...")
        enabled_cmd = enable_timer()
        print(f"   Enable Command Success: {enabled_cmd}")

        print("\n5. Checking if timer is enabled (after enabling)...")
        enabled_after = is_timer_enabled()
        print(f"   Is Enabled: {enabled_after}")

        print("\n6. Checking if timer is active (after enabling)...")
        active_after = is_timer_active()
        print(f"   Is Active: {active_after}")

        input("\n---> Press Enter to disable the timer...") # Pause for inspection

        print("\n7. Disabling timer...")
        disabled_cmd = disable_timer()
        print(f"   Disable Command Success: {disabled_cmd}")

        print("\n8. Checking if timer is enabled (after disabling)...")
        enabled_final = is_timer_enabled()
        print(f"   Is Enabled: {enabled_final}")

        print("\n9. Checking if timer is active (after disabling)...")
        active_final = is_timer_active()
        print(f"   Is Active: {active_final}")
    else:
         print("\nSkipping enable/disable tests as unit file creation failed.")

    print("\n--- Test Complete ---")
