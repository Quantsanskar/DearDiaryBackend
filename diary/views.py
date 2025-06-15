from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Diary, Entry, Reaction, ReadStatus
from .serializers import (
    DiarySerializer, 
    EntrySerializer, 
    CreateEntrySerializer,
    ReactionSerializer
)

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_diaries(request):
    """Get all diaries for the current user"""
    user = request.user
    
    # Get personal diary
    personal_diary, created = Diary.objects.get_or_create(
        owner=user,
        diary_type='personal',
        defaults={'title': f"{user.display_name or user.username}'s Personal Diary"}
    )
    
    # Get shared diary (create if doesn't exist)
    shared_diary, created = Diary.objects.get_or_create(
        diary_type='shared',
        defaults={
            'title': 'Our Shared Diary',
            'owner': user
        }
    )
    
    # Get partner's personal diary if partner is set
    partner_diary = None
    if user.partner_username:
        try:
            partner = User.objects.get(username=user.partner_username)
            partner_diary = Diary.objects.filter(
                owner=partner,
                diary_type='personal'
            ).first()
        except User.DoesNotExist:
            pass
    
    diaries = [personal_diary, shared_diary]
    if partner_diary:
        diaries.append(partner_diary)
    
    serializer = DiarySerializer(diaries, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_diary_entries(request, diary_id):
    """Get entries for a specific diary"""
    diary = get_object_or_404(Diary, id=diary_id)
    
    # Check permissions
    user = request.user
    if diary.diary_type == 'personal' and diary.owner != user:
        # Check if this is partner's diary and user has access
        if not (user.partner_username and diary.owner.username == user.partner_username):
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    entries = diary.entries.all()
    serializer = EntrySerializer(entries, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_entry(request, diary_id):
    """Create a new entry in a diary"""
    diary = get_object_or_404(Diary, id=diary_id)
    
    # Check permissions
    user = request.user
    
    # Allow writing in:
    # 1. User's own personal diary
    # 2. Shared diary (anyone can write)
    # Prevent writing in partner's personal diary
    if diary.diary_type == 'personal' and diary.owner != user:
        return Response({'error': 'Cannot write in someone else\'s personal diary'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    serializer = CreateEntrySerializer(data=request.data, context={
        'request': request,
        'diary': diary
    })
    
    if serializer.is_valid():
        entry = serializer.save()
        return Response(EntrySerializer(entry, context={'request': request}).data, 
                       status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_reaction(request, entry_id):
    """Add or remove a reaction to an entry"""
    entry = get_object_or_404(Entry, id=entry_id)
    reaction_type = request.data.get('reaction_type')
    
    if not reaction_type:
        return Response({'error': 'reaction_type is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Check if reaction already exists
    existing_reaction = Reaction.objects.filter(
        entry=entry,
        user=request.user,
        reaction_type=reaction_type
    ).first()
    
    if existing_reaction:
        # Remove reaction
        existing_reaction.delete()
        return Response({'message': 'Reaction removed'})
    else:
        # Add reaction
        reaction = Reaction.objects.create(
            entry=entry,
            user=request.user,
            reaction_type=reaction_type
        )
        serializer = ReactionSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_entry_read(request, entry_id):
    """Mark an entry as read"""
    entry = get_object_or_404(Entry, id=entry_id)
    
    read_status, created = ReadStatus.objects.get_or_create(
        entry=entry,
        user=request.user
    )
    
    return Response({'message': 'Entry marked as read'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_entry_detail(request, entry_id):
    """Get detailed view of a single entry"""
    entry = get_object_or_404(Entry, id=entry_id)
    
    # Check if entry is unlocked
    if not entry.is_unlocked:
        return Response({'error': 'Entry is still locked'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Mark as read
    ReadStatus.objects.get_or_create(entry=entry, user=request.user)
    
    serializer = EntrySerializer(entry, context={'request': request})
    return Response(serializer.data)
