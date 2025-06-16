import os
import shutil
from datetime import datetime
import subprocess
from pathlib import Path

def backup_database():
    # Get the base directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Database file path
    db_file = BASE_DIR / 'db.sqlite3'
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BASE_DIR / f'db_backup_{timestamp}.sqlite3'
    
    # Copy the database file
    shutil.copy2(db_file, backup_file)
    
    # Add the backup file to git
    subprocess.run(['git', 'add', str(backup_file)], cwd=BASE_DIR)
    
    # Commit the changes
    commit_message = f'Database backup {timestamp}'
    subprocess.run(['git', 'commit', '-m', commit_message], cwd=BASE_DIR)
    
    # Push to GitHub
    subprocess.run(['git', 'push', 'origin', 'main'], cwd=BASE_DIR)
    
    return str(backup_file)

def restore_database():
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Get all backup files
    backup_files = sorted(BASE_DIR.glob('db_backup_*.sqlite3'))
    if not backup_files:
        return False
    
    # Get the most recent backup
    latest_backup = backup_files[-1]
    db_file = BASE_DIR / 'db.sqlite3'
    
    # Restore the database
    shutil.copy2(latest_backup, db_file)
    return True

if __name__ == '__main__':
    backup_database() 