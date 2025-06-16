from django.urls import path
from . import views
from django.core.management import call_command
from django.http import HttpResponse

def backup_db(request):
    # Accept both GET and POST requests
    call_command('backup_db')
    return HttpResponse('Database backup initiated successfully')

urlpatterns = [
    path('', views.index, name='index'),
    path('api/backup-db/', backup_db, name='backup_db'),
] 