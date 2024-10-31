# Backup Utility Application

The Backup Utility Application is a graphical interface (GUI) tool that facilitates file backups, encryption, scheduling, and restoration. Built using Python and Tkinter, the application allows users to configure backup locations, set backup frequencies, and securely store data with encryption.

## Features
- **Backup Options**: Supports full and incremental backups.
- **Encryption**: Optional encryption with password protection for secure data.
- **Restore**: Restore any version of the backup with a simple selection.
- **Scheduling**: Set the backup frequency (Daily, Weekly, or Monthly).
- **User Preferences**: Save and load user preferences in a configuration file.
- **Backup Statistics**: View details and statistics of all backups.
- **Preview Schedule**: Displays upcoming scheduled backups.

## Requirements
To run the application, you need:
- Python 3.7 or higher
- The following Python packages:

### requirements.txt
```plaintext
cryptography==3.3.2
matplotlib==3.3.4
Pillow==8.1.0
ttkbootstrap==1.0.0
```

### Install Dependencies
To install dependencies, use:
```bash
pip install -r requirements.txt
```

## Project Structure
- **assets/**: Folder containing application images and icons.
  - `logo.png`: Main application logo.
  - `backup_icon.png`: Icon for the backup button.
- **backup_stats.csv**: CSV file to log backup statistics.
- **backup_metadata.json**: JSON file to store metadata of backups.
- **user_config.ini**: Configuration file to save user preferences.

## Usage Guide

1. **Run the Application**:
    ```bash
    python main.py
    ```

2. **User Interface**:
    - The application will display a splash screen upon startup.
    - After the splash screen, the main backup utility interface appears.

3. **Setting Backup Configuration**:
    - **Select Source Directories**: Choose directories you want to back up.
    - **Backup Location**: Set the location where backups will be stored.
    - **Backup Frequency**: Select frequency from `Daily`, `Weekly`, or `Monthly`.
    - **Enable Encryption** (Optional): Encrypt backup files with a password.

4. **Backup Operations**:
    - **Full Backup**: Run a complete backup of selected directories.
    - **Incremental Backup**: Backup only newly modified files.
    - **Show Backup Statistics**: View past backup statistics, including file size and type.
    - **Restore Backup**: Choose a backup version to restore.
    - **Save Preferences**: Save the current configuration for future use.
    - **Preview Backup Schedule**: View upcoming backup tasks.

## Function Descriptions
- **password_to_key(password)**: Generates an encryption key from a password.
- **show_splash(root)**: Displays a splash screen when the app starts.
- **init_main_window(root)**: Initializes the main GUI window.
- **calculate_next_backup_time(frequency)**: Calculates the next scheduled backup based on frequency.
- **record_backup_metadata(...)**: Records metadata for each backup in JSON format.
- **load_backup_metadata()**: Loads metadata of all backups from JSON.
- **list_backup_versions()**: Lists available backup versions.
- **show_restore_window()**: Displays a window to restore selected backups.
- **restore_backup_by_version(...)**: Restores a backup based on the selected version.
- **delete_backup(...)**: Deletes a selected backup and updates metadata.
- **load_user_preferences()**: Loads user preferences from `user_config.ini`.
- **save_user_preferences()**: Saves user preferences in `user_config.ini`.
- **show_backup_preview()**: Displays a preview of upcoming scheduled backups.

## Example
To create a new backup and schedule it for weekly frequency with encryption enabled:
1. Open the application and configure directories, backup location, and frequency.
2. Enable the encryption option and set a password.
3. Click on **Run Full Backup** or **Run Incremental Backup** to initiate the backup.

## License
This project is licensed under the MIT License.


