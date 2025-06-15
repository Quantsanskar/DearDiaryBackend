from rest_framework import serializers
from .models import Diary, Entry, Reaction, ReadStatus
from django.contrib.auth import get_user_model

User = get_user_model()

class ReactionSerializer(serializers.ModelSerializer):
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)
    reaction_emoji = serializers.CharField(source='get_reaction_type_display', read_only=True)
    
    class Meta:
        model = Reaction
        fields = ('id', 'reaction_type', 'reaction_emoji', 'user_display_name', 'created_at')
        read_only_fields = ('id', 'created_at')

class EntrySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.display_name', read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    reaction_counts = serializers.SerializerMethodField()
    is_unlocked = serializers.ReadOnlyField()
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Entry
        fields = ('id', 'title', 'content', 'mood', 'is_timed', 'unlock_at', 
                 'created_at', 'updated_at', 'author_name', 'reactions', 
                 'reaction_counts', 'is_unlocked', 'is_read')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_reaction_counts(self, obj):
        reactions = obj.reactions.all()
        counts = {}
        for reaction in reactions:
            reaction_type = reaction.reaction_type
            counts[reaction_type] = counts.get(reaction_type, 0) + 1
        return counts
    
    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReadStatus.objects.filter(entry=obj, user=request.user).exists()
        return False

class DiarySerializer(serializers.ModelSerializer):
    entries = EntrySerializer(many=True, read_only=True)
    entry_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Diary
        fields = ('id', 'title', 'diary_type', 'created_at', 'updated_at', 
                 'entries', 'entry_count', 'unread_count')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_entry_count(self, obj):
        return obj.entries.count()
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            read_entry_ids = ReadStatus.objects.filter(
                user=request.user,
                entry__diary=obj
            ).values_list('entry_id', flat=True)
            return obj.entries.exclude(id__in=read_entry_ids).count()
        return 0

class CreateEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('title', 'content', 'mood', 'is_timed', 'unlock_at')
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['diary'] = self.context['diary']
        return super().create(validated_data)
