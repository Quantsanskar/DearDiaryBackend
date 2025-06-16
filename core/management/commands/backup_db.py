from django.core.management.base import BaseCommand
from backend.db_backup import backup_database

class Command(BaseCommand):
    help = 'Backs up the SQLite database to GitHub'

    def handle(self, *args, **options):
        try:
            backup_file = backup_database()
            self.stdout.write(self.style.SUCCESS(f'Successfully backed up database to {backup_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to backup database: {str(e)}')) 