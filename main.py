import os
import tarfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime, timedelta
import csv
import json
import configparser
import time
from tkinter import simpledialog
import matplotlib.pyplot as plt
import platform
import subprocess
from cryptography.fernet import Fernet
import hashlib
import base64
from PIL import Image, ImageTk
import ttkbootstrap as tb

# Constants
STATS_FILE = 'backup_stats.csv'
CONFIG_FILE = 'user_config.ini'

def password_to_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())


# Splash screen display
def show_splash(root):
    splash = tk.Toplevel()
    splash.geometry("400x400")
    splash.title("Welcome")
    
    splash_label = tk.Label(splash, text="Backup Utility", font=("Helvetica", 24))
    splash_label.pack(expand=True)
    
    root.after(3000, splash.destroy)

# Main app window initialization
def init_main_window(root):
    root.title("Backup Utility")
    root.geometry("800x500")

    frame = tb.Frame(root, padding="10 10 10 10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    logo_img = Image.open("assets/logo.png")
    logo_img = logo_img.resize((50, 50), Image.LANCZOS)
    logo = ImageTk.PhotoImage(logo_img)
    
    logo_label = tk.Label(frame, image=logo)
    logo_label.image = logo
    logo_label.grid(row=0, column=0, columnspan=3)
    
    tb.Label(frame, text="Select Source Directories:").grid(row=1, column=0, sticky='w')
    tb.Entry(frame, textvariable=selected_dirs, width=50).grid(row=1, column=1)
    tb.Button(frame, text="Browse", command=choose_directories, bootstyle="primary").grid(row=1, column=2)

    tb.Label(frame, text="Backup Location:").grid(row=2, column=0, sticky='w')
    tb.Entry(frame, textvariable=backup_location, width=50).grid(row=2, column=1)
    tb.Button(frame, text="Browse", command=choose_backup_location, bootstyle="primary").grid(row=2, column=2)

    tb.Label(frame, text="Backup Frequency:").grid(row=3, column=0, sticky='w')
    frequency_options = tb.Combobox(frame, textvariable=backup_frequency, values=["Daily", "Weekly", "Monthly"], bootstyle="info")
    frequency_options.grid(row=3, column=1)

    tb.Checkbutton(frame, text="Enable Encryption", variable=encryption_enabled, bootstyle="success-round-toggle").grid(row=4, columnspan=3, sticky='w')

    tb.Label(frame, text="Password for Encryption:").grid(row=5, column=0, sticky='w')
    global password_entry
    password_entry = tb.Entry(frame, show='*')
    password_entry.grid(row=5, column=1)

    full_backup_icon = Image.open("assets/backup_icon.png")
    full_backup_icon = full_backup_icon.resize((20, 20), Image.LANCZOS)
    full_backup_image = ImageTk.PhotoImage(full_backup_icon)
    
    tb.Button(frame, text="Run Full Backup", image=full_backup_image, compound="left", command=run_full_backup, bootstyle="success").grid(row=6, column=0, pady=5)
    tb.Button(frame, text="Run Incremental Backup", command=run_incremental_backup, bootstyle="info").grid(row=6, column=1, pady=5)
    tb.Button(frame, text="Show Backup Statistics", command=show_backup_statistics, bootstyle="warning").grid(row=6, column=2, pady=5)
    tb.Button(frame, text="Restore Backup", command=show_restore_window, bootstyle="danger").grid(row=7, column=0, pady=5)
    tb.Button(frame, text="Save Preferences", command=save_user_preferences, bootstyle="primary").grid(row=7, column=1, pady=5)
    tb.Button(frame, text="Preview Backup Schedule", command=show_backup_preview, bootstyle="info").grid(row=7, column=2, pady=5)
    
    # tb.Button(frame, text="List Backup Versions", command=list_backup_versions_ui, bootstyle="info").grid(row=7, column=3, pady=5)
    # tb.Button(frame, text="Restore by Version", command=restore_by_version_ui, bootstyle="danger").grid(row=8, column=3, pady=5)
    # tb.Button(frame, text="Restore by Date", command=restore_by_date_ui, bootstyle="danger").grid(row=9, column=3, pady=5)


    logo_label_bottom = tk.Label(frame, image=logo)
    logo_label_bottom.image = logo
    logo_label_bottom.grid(row=8, column=0, columnspan=3)

def record_backup_metadata(backup_file, backup_type, size, backup_location, backup_folder, encrypted=False):
    metadata_file = 'backup_metadata.json'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if encrypted:
        backup_file += ".enc"
    
    metadata = {
        'timestamp': timestamp,
        'backup_file': backup_file,
        'backup_type': backup_type,
        'size': size,
        'backup_location': backup_location,
        'backup_folder': backup_folder
    }

    # Check if metadata file exists
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            all_metadata = json.load(f)
    else:
        all_metadata = []

    all_metadata.append(metadata)

    with open(metadata_file, 'w') as f:
        json.dump(all_metadata, f, indent=4)

def load_backup_metadata():
    metadata_file = 'backup_metadata.json'
    
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    else:
        return []

def list_backup_versions():
    metadata = load_backup_metadata()
    
    version_list = []
    for i, entry in enumerate(metadata):
        version_list.append(f"{i+1}. {entry['timestamp']} - {entry['backup_type']} - Size: {entry['size']} bytes")
    
    return version_list

def show_restore_window():
    backups = load_backup_metadata()
    
    if not backups:
        messagebox.showinfo("No Backups", "No backup versions found.")
        return
    
    restore_window = tk.Toplevel()
    restore_window.title("Restore Backups")
    
    for i, backup in enumerate(backups):
        backup_info = f"{i+1}. {backup['timestamp']} - {backup['backup_type']} - Size: {backup['size']} bytes"
        backup_label = tk.Label(restore_window, text=backup_info)
        backup_label.grid(row=i, column=0, sticky='w')
        
        restore_button = tk.Button(restore_window, text="Restore", command=lambda i=i: prompt_restore_path(i))
        restore_button.grid(row=i, column=1)
        
        delete_button = tk.Button(restore_window, text="Delete", command=lambda i=i: delete_backup(i))
        delete_button.grid(row=i, column=2)

def prompt_restore_path(version_number):
    restore_location = filedialog.askdirectory(title="Select Restore Location")
    if restore_location:
        restore_backup_by_version(version_number, restore_location)
    
def restore_backup_by_version(version_number, restore_location):
    metadata = load_backup_metadata()
    if 0 <= version_number < len(metadata):
        backup_file = metadata[version_number]['backup_file']
        backup_location = metadata[version_number]['backup_location']
        backup_path = os.path.join(backup_location, backup_file)
        if not os.path.exists(backup_path) and backup_path.endswith(".enc"):
            backup_path = backup_path.replace(".enc", "")
        restore_backup(backup_path, restore_location)  # Call the restore_backup function that takes two arguments
    else:
        messagebox.showerror("Error", "Invalid version number selected.")

def restore_backup(backup_file, restore_location):
    try:
        # Debug statement to check the file path
        print(f"Attempting to restore backup from: {backup_file}")

        # If it's an encrypted file, decrypt it first
        if backup_file.endswith(".enc"):
            decrypted_backup_file = decrypt_backup_file(backup_file)
            if not decrypted_backup_file:  # Decryption failed, stop the restore process
                return
            backup_file = decrypted_backup_file  # Use decrypted file path for extraction

        # Debug statement to check if the file exists
        if not os.path.exists(backup_file):
            print(f"Backup file does not exist: {backup_file}")
            messagebox.showerror("Restore Failed", f"Backup file does not exist: {backup_file}")
            return

        # Extract the backup file
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(path=restore_location)

        messagebox.showinfo("Restore Completed", f"Backup restored to {restore_location}")

    except Exception as e:
        messagebox.showerror("Restore Failed", f"Error: {str(e)}")
        
def delete_backup(version_number):
    metadata = load_backup_metadata()
    if 0 <= version_number < len(metadata):
        backup_file = metadata[version_number]['backup_file']
        backup_location = metadata[version_number]['backup_location']
        backup_path = os.path.join(backup_location, backup_file)
        
        # Check for both encrypted and decrypted file paths
        if os.path.exists(backup_path):
            os.remove(backup_path)
        elif backup_path.endswith(".enc") and os.path.exists(backup_path.replace(".enc", "")):
            os.remove(backup_path.replace(".enc", ""))
        else:
            messagebox.showerror("Error", f"Backup file does not exist: {backup_path}")
            return
        
        del metadata[version_number]
        with open('backup_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)
        messagebox.showinfo("Backup Deleted", "Backup has been deleted.")
    else:
        messagebox.showerror("Error", "Invalid version number selected.")

# Function to load user preferences from a config file
def load_user_preferences():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'Preferences' in config:
            selected_dirs.set(config['Preferences'].get('source_dirs', ''))
            backup_location.set(config['Preferences'].get('backup_dir', ''))
            backup_frequency.set(config['Preferences'].get('frequency', ''))
            encryption_enabled.set(config['Preferences'].getboolean('encryption_enabled', False))

# Function to save user preferences to a config file
def save_user_preferences():
    config = configparser.ConfigParser()
    config['Preferences'] = {
        'source_dirs': selected_dirs.get(),
        'backup_dir': backup_location.get(),
        'frequency': backup_frequency.get(),
        'encryption_enabled': encryption_enabled.get()
    
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    messagebox.showinfo("Preferences Saved", "Your preferences have been saved.")

def show_backup_preview():
    frequency = backup_frequency.get()
    frequency_map = {
        "Daily": timedelta(days=1),
        "Weekly": timedelta(weeks=1),
        "Monthly": timedelta(weeks=4)
    }

    if frequency in frequency_map:
        next_backup = datetime.now() + frequency_map[frequency]
        preview_text = f"Next Backup: {next_backup.strftime('%Y-%m-%d %H:%M:%S')}\nFrequency: {frequency}"
    else:
        preview_text = "Please select a backup frequency."

    cancel_button = messagebox.askyesno("Backup Schedule Preview", f"{preview_text}\n\nDo you want to cancel the upcoming backup?")
    if cancel_button:
        cancel_scheduled_backup()

def cancel_scheduled_backup():
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system('crontab -r')
        messagebox.showinfo("Backup Canceled", "Scheduled backup has been canceled.")
    elif platform.system() == "Windows":
        task_name = "BackupTask"
        command = f'schtasks /delete /tn {task_name} /f'
        subprocess.run(command, shell=True)
        messagebox.showinfo("Backup Canceled", "Scheduled backup has been canceled.")

# Function to encrypt the backup file
def encrypt_backup_file(backup_path):
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Password is required for encryption.")
        return

    key = password_to_key(password)
    cipher = Fernet(key)

    with open(backup_path, 'rb') as file:
        original_file = file.read()
        encrypted_file = cipher.encrypt(original_file)

    encrypted_backup_path = backup_path + ".enc"
    with open(encrypted_backup_path, 'wb') as file:
        file.write(encrypted_file)

    os.remove(backup_path)  # Remove original file after encryption
    messagebox.showinfo("Backup Encrypted", f"Backup file encrypted and saved as {encrypted_backup_path}")

# Function to get the last backup time from the statistics file
def get_last_backup_time():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as csvfile:
            reader = csv.reader(csvfile)
            last_row = list(reader)[-1]
            last_backup_time = last_row[0]
            return time.mktime(datetime.strptime(last_backup_time, '%Y%m%d_%H%M%S').timetuple())
    return 0

# Function to record backup statistics
def record_backup_stat(timestamp, size, success):
    with open(STATS_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, size, str(success)])

# Function to choose directories for backup
def choose_directories():
    dirs = filedialog.askdirectory()
    if dirs:
        selected_dirs.set(dirs)

def choose_backup_location():
    dest_dir = filedialog.askdirectory()
    backup_location.set(dest_dir)

# Function to run full backup (not incremental)
def run_full_backup():
    source_dirs = selected_dirs.get().split('; ')
    backup_dir = backup_location.get()

    if not source_dirs or not backup_dir:
        messagebox.showerror("Input Error", "Please select source directories and backup destination.")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_{timestamp}_full.tar.gz"
    backup_path = os.path.join(backup_dir, backup_file)

    try:
        # Create tar.gz backup file
        with tarfile.open(backup_path, "w:gz") as tar:
            for source in source_dirs:
                tar.add(source, arcname=os.path.basename(source))

        password = password_entry.get()
        if password:
            # Encrypt if password is provided
            encrypt_backup_file(backup_path)
            encrypted_backup_path = backup_path + ".enc"
            backup_path = encrypted_backup_path

        # Get backup file size
        size = os.path.getsize(backup_path)
        
        # Record backup metadata
        backup_type = 'Full'
        record_backup_metadata(backup_file, backup_type, size, backup_dir, backup_file, encrypted=bool(password))
        
        # Notify user of success
        messagebox.showinfo("Backup Completed", f"Full backup saved as {backup_file} in {backup_dir}")

    except Exception as e:
        # Log failure in metadata with size = 0
        record_backup_metadata(backup_file, 'Full', 0, backup_dir, backup_file)
        messagebox.showerror("Backup Failed", f"Error: {str(e)}")

def run_incremental_backup():
    source_dirs = selected_dirs.get().split('; ')
    backup_dir = backup_location.get()
    frequency = backup_frequency.get()

    if not source_dirs or not backup_dir:
        messagebox.showerror("Input Error", "Please select source directories and backup destination.")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_{timestamp}_incremental.tar.gz"
    backup_path = os.path.join(backup_dir, backup_file)

    last_backup_time = get_last_backup_time()

    try:
        # Create tar.gz backup file for files modified since the last backup
        with tarfile.open(backup_path, "w:gz") as tar:
            for source in source_dirs:
                for root, dirs, files in os.walk(source):
                    for file in files:
                        filepath = os.path.join(root, file)
                        if os.path.getmtime(filepath) > last_backup_time:
                            tar.add(filepath, arcname=os.path.relpath(filepath, source))

        password = password_entry.get()
        if password:
            # Encrypt if password is provided
            encrypt_backup_file(backup_path)
            encrypted_backup_path = backup_path + ".enc"
            backup_path = encrypted_backup_path

        # Get backup file size
        size = os.path.getsize(backup_path)
        
        # Record backup metadata
        backup_type = 'Incremental'
        record_backup_metadata(backup_file, backup_type, size, backup_dir, backup_file, encrypted=bool(password))

        # Notify user of success
        messagebox.showinfo("Backup Completed", f"Incremental backup saved as {backup_file} in {backup_dir}")

    except Exception as e:
        # Log failure in metadata with size = 0
        record_backup_metadata(backup_file, 'Incremental', 0, backup_dir, backup_file)
        messagebox.showerror("Backup Failed", f"Error: {str(e)}")

    # Schedule next backup according to specified frequency
    schedule_backup(frequency)

# Function to schedule backup based on frequency
def schedule_backup(frequency):
    cron_command = generate_cron_command(frequency)
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system(f'(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -')
        messagebox.showinfo("Backup Scheduled", f"Backup scheduled with cron: {cron_command}")
    elif platform.system() == "Windows":
        schedule_task_windows(frequency)
        messagebox.showinfo("Backup Scheduled", f"Backup scheduled with Task Scheduler")

# Function to generate cron command based on frequency
def generate_cron_command(frequency):
    script_path = os.path.abspath(__file__)
    if frequency == 'Daily':
        return f"0 0 * * * python3 {script_path}"
    elif frequency == 'Weekly':
        return f"0 0 * * 0 python3 {script_path}"
    elif frequency == 'Monthly':
        return f"0 0 1 * * python3 {script_path}"
    return ""

# Function to schedule tasks in Windows using Task Scheduler
def schedule_task_windows(frequency):
    task_name = "BackupTask"
    script_path = os.path.abspath(__file__)
    time_map = {'Daily': 'DAILY', 'Weekly': 'WEEKLY', 'Monthly': 'MONTHLY'}
    time_interval = time_map.get(frequency, 'DAILY')

    command = f'schtasks /create /tn {task_name} /tr "python {script_path}" /sc {time_interval} /f'
    subprocess.run(command, shell=True)

# Function to show backup statistics
def show_backup_statistics():
    metadata_file = 'backup_metadata.json'
    
    try:
        if not os.path.exists(metadata_file):
            raise FileNotFoundError

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        if not metadata:
            raise FileNotFoundError

        dates, sizes, successes = [], [], []

        for entry in metadata:
            dates.append(entry['timestamp'])
            sizes.append(entry['size'])
            successes.append(entry['size'] > 0)  # Assuming size > 0 indicates success

        plt.figure(figsize=(10, 5))
        plt.subplot(2, 1, 1)
        plt.plot(dates, sizes, marker='o')
        plt.title('Backup Size Over Time')
        plt.xlabel('Date')
        plt.ylabel('Size (bytes)')
        plt.xticks(rotation=45)

        plt.subplot(2, 1, 2)
        plt.bar(dates, [1 if s else 0 for s in successes], color=['green' if s else 'red' for s in successes])
        plt.title('Backup Success Rates')
        plt.xlabel('Date')
        plt.ylabel('Success (1=Success, 0=Failure)')
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        messagebox.showerror("Error", "No backup statistics found.")
        
# Function to decrypt the backup file
def decrypt_backup_file(backup_path):
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Password is required for decryption.")
        return None

    key = password_to_key(password)
    cipher = Fernet(key)

    try:
        with open(backup_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
            decrypted_data = cipher.decrypt(encrypted_data)

        decrypted_backup_path = backup_path.replace(".enc", "")
        with open(decrypted_backup_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)

        os.remove(backup_path)  # Remove encrypted file after decryption
        return decrypted_backup_path

    except Exception as e:
        messagebox.showerror("Decryption Failed", f"Error: {str(e)}")
        return None
# Main application logic
def main():
    root = tb.Window(themename="superhero")
    
    global selected_dirs, backup_location, backup_frequency, encryption_enabled, password_entry
    selected_dirs = tk.StringVar()
    backup_location = tk.StringVar()
    backup_frequency = tk.StringVar()
    encryption_enabled = tk.BooleanVar(value=False)

    load_user_preferences()
    show_splash(root)
    root.after(3000, lambda: init_main_window(root))
    root.mainloop()

if __name__ == "__main__":
    main()