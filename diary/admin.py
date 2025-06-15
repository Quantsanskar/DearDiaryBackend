from django.contrib import admin
from .models import Diary, Entry, Reaction, ReadStatus

@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'diary_type', 'owner', 'created_at')
    list_filter = ('diary_type', 'created_at')
    search_fields = ('title', 'owner__username')

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'diary', 'is_timed', 'created_at')
    list_filter = ('is_timed', 'created_at', 'diary__diary_type')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('entry', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('entry__title', 'user__username')

@admin.register(ReadStatus)
class ReadStatusAdmin(admin.ModelAdmin):
    list_display = ('entry', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('entry__title', 'user__username')
