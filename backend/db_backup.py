import os
import shutil
from datetime import datetime
import subprocess
from pathlib import Path

def setup_git():
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Configure Git
    subprocess.run(['git', 'config', '--global', 'user.email', 'sanskarsrdav@gmail.com'], cwd=BASE_DIR)
    subprocess.run(['git', 'config', '--global', 'user.name', 'Quantsanskar'], cwd=BASE_DIR)
    
    # Set up remote if not exists
    result = subprocess.run(['git', 'remote', '-v'], cwd=BASE_DIR, capture_output=True, text=True)
    if 'origin' not in result.stdout:
        subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/Quantsanskar/DearDiaryBackend.git'], cwd=BASE_DIR)

def backup_database():
    # Get the base directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Setup Git configuration
    setup_git()
    
    # Database file path
    db_file = BASE_DIR / 'db.sqlite3'
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BASE_DIR / f'db_backup_{timestamp}.sqlite3'
    
    # Copy the database file
    shutil.copy2(db_file, backup_file)
    
    try:
        # Check if we're in a git repository
        git_status = subprocess.run(['git', 'status'], cwd=BASE_DIR, capture_output=True, text=True)
        if 'fatal: not a git repository' in git_status.stderr:
            # Initialize git repository
            subprocess.run(['git', 'init'], cwd=BASE_DIR, check=True)
            subprocess.run(['git', 'add', '.'], cwd=BASE_DIR, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=BASE_DIR, check=True)
        
        # Check if we're in detached HEAD state
        if 'HEAD detached' in git_status.stdout:
            # Create and switch to main branch
            subprocess.run(['git', 'checkout', '-b', 'main'], cwd=BASE_DIR, check=True)
        
        # Add the backup file to git
        add_result = subprocess.run(['git', 'add', str(backup_file)], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        
        # Commit the changes
        commit_message = f'Database backup {timestamp}'
        commit_result = subprocess.run(['git', 'commit', '-m', commit_message], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        
        # Force push to main branch
        push_result = subprocess.run(['git', 'push', '-f', 'origin', 'main'], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        
        # Return success message with GitHub URL
        repo_url = 'https://github.com/Quantsanskar/DearDiaryBackend'
        return f'Successfully backed up database to {backup_file} and pushed to GitHub: {repo_url}\nGit Status: {git_status.stdout}\nAdd Result: {add_result.stdout}\nCommit Result: {commit_result.stdout}\nPush Result: {push_result.stdout}'
    except subprocess.CalledProcessError as e:
        return f'Error in Git operation: {e.stderr}\nCommand: {e.cmd}\nReturn code: {e.returncode}'

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