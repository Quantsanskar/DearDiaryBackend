from django.urls import path
from . import views
from django.core.management import call_command
from django.http import HttpResponse

def backup_db(request):
    if request.method == 'POST':
        call_command('backup_db')
        return HttpResponse('Database backup initiated')
    return HttpResponse('Method not allowed', status=405)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/backup-db/', backup_db, name='backup_db'),
] 