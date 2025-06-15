from django.urls import path
from . import views

urlpatterns = [
    path('diaries/', views.get_diaries, name='get_diaries'),
    path('diaries/<int:diary_id>/entries/', views.get_diary_entries, name='get_diary_entries'),
    path('diaries/<int:diary_id>/entries/create/', views.create_entry, name='create_entry'),
    path('entries/<int:entry_id>/', views.get_entry_detail, name='get_entry_detail'),
    path('entries/<int:entry_id>/react/', views.add_reaction, name='add_reaction'),
    path('entries/<int:entry_id>/read/', views.mark_entry_read, name='mark_entry_read'),
]
