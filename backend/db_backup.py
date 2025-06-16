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

def verify_git_status():
    BASE_DIR = Path(__file__).resolve().parent.parent
    status = subprocess.run(['git', 'status'], cwd=BASE_DIR, capture_output=True, text=True)
    branch = subprocess.run(['git', 'branch', '--show-current'], cwd=BASE_DIR, capture_output=True, text=True)
    return f"Current Branch: {branch.stdout.strip()}\nStatus: {status.stdout}"

def cleanup_old_backups():
    BASE_DIR = Path(__file__).resolve().parent.parent
    backup_files = sorted(BASE_DIR.glob('db_backup_*.sqlite3'))
    
    # Keep only the latest backup
    if len(backup_files) > 1:
        for old_backup in backup_files[:-1]:
            try:
                old_backup.unlink()
                print(f"Deleted old backup: {old_backup.name}")
            except Exception as e:
                print(f"Error deleting {old_backup.name}: {e}")

def restore_database():
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Get all backup files
    backup_files = sorted(BASE_DIR.glob('db_backup_*.sqlite3'))
    if not backup_files:
        return False, "No backup files found"
    
    # Get the most recent backup
    latest_backup = backup_files[-1]
    db_file = BASE_DIR / 'db.sqlite3'
    
    # Restore the database
    shutil.copy2(latest_backup, db_file)
    return True, f"Restored from {latest_backup.name}"

def backup_database():
    # Get the base directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Setup Git configuration
    setup_git()
    
    # First, restore the latest backup
    restore_success, restore_message = restore_database()
    
    # Database file path
    db_file = BASE_DIR / 'db.sqlite3'
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BASE_DIR / f'db_backup_{timestamp}.sqlite3'
    
    # Copy the database file
    shutil.copy2(db_file, backup_file)
    assert backup_file.exists(), f"Backup file {backup_file} does not exist!"
    
    try:
        # Initial status check
        initial_status = verify_git_status()
        
        # Check if we're in a git repository
        git_status = subprocess.run(['git', 'status'], cwd=BASE_DIR, capture_output=True, text=True)
        if 'fatal: not a git repository' in git_status.stderr:
            # Initialize git repository
            subprocess.run(['git', 'init'], cwd=BASE_DIR, check=True)
            subprocess.run(['git', 'add', '.'], cwd=BASE_DIR, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=BASE_DIR, check=True)
        
        # Check if we're in detached HEAD state
        if 'HEAD detached' in git_status.stdout:
            # Check if 'main' branch exists
            branch_list = subprocess.run(['git', 'branch'], cwd=BASE_DIR, capture_output=True, text=True)
            if 'main' in branch_list.stdout:
                subprocess.run(['git', 'checkout', 'main'], cwd=BASE_DIR, check=True)
            else:
                subprocess.run(['git', 'checkout', '-b', 'main'], cwd=BASE_DIR, check=True)
        
        # Clean up old backups
        cleanup_old_backups()
        
        # Add the backup file to git (use only the filename)
        add_result = subprocess.run(['git', 'add', backup_file.name], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        
        # Commit the changes
        commit_message = f'Database backup {timestamp}'
        commit_result = subprocess.run(['git', 'commit', '-m', commit_message], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        
        # Force push to main branch
        push_result = subprocess.run(['git', 'push', '-f', 'origin', 'main'], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        
        # Final status check
        final_status = verify_git_status()
        
        # Return success message with GitHub URL
        repo_url = 'https://github.com/Quantsanskar/DearDiaryBackend'
        return f'''Backup Status Report:
1. Initial Git Status:
{initial_status}

2. Restore Status:
{restore_message}

3. Backup File Created: {backup_file}

4. Git Operations:
Add Result: {add_result.stdout}
Commit Result: {commit_result.stdout}
Push Result: {push_result.stdout}

5. Final Git Status:
{final_status}

6. GitHub Repository: {repo_url}'''
    except subprocess.CalledProcessError as e:
        return f'Error in Git operation: {e.stderr}\nCommand: {e.cmd}\nReturn code: {e.returncode}'

if __name__ == '__main__':
    backup_database()