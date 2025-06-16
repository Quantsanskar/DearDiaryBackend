from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import pytz

User = get_user_model()

class Diary(models.Model):
    """Diary model - can be personal or shared"""
    DIARY_TYPES = [
        ('personal', 'Personal'),
        ('shared', 'Shared'),
    ]
    
    title = models.CharField(max_length=200)
    diary_type = models.CharField(max_length=10, choices=DIARY_TYPES)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_diaries')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='shared_diaries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Diaries"
    
    def __str__(self):
        return f"{self.title} ({self.diary_type})"

class Entry(models.Model):
    """Diary entry model"""
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name='entries')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    mood = models.CharField(max_length=50, blank=True)
    is_timed = models.BooleanField(default=False)
    unlock_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title or 'Entry'} by {self.author.username}"
    
    def save(self, *args, **kwargs):
        # Convert unlock_at to Asia/Kolkata timezone if it's provided
        if self.unlock_at and timezone.is_naive(self.unlock_at):
            ist = pytz.timezone('Asia/Kolkata')
            self.unlock_at = ist.localize(self.unlock_at)
        super().save(*args, **kwargs)
    
    @property
    def is_unlocked(self):
        if not self.is_timed:
            return True
        now = timezone.now()
        return now >= self.unlock_at if self.unlock_at else True

class Reaction(models.Model):
    """Reaction model for entries"""
    REACTION_TYPES = [
        ('heart', '💖'),
        ('star', '⭐'),
        ('hug', '🤗'),
        ('smile', '😊'),
        ('love', '💕'),
    ]
    
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['entry', 'user', 'reaction_type']
    
    def __str__(self):
        return f"{self.get_reaction_type_display()} by {self.user.username}"

class ReadStatus(models.Model):
    """Track read status of entries"""
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['entry', 'user']
    
    def __str__(self):
        return f"{self.entry.title} read by {self.user.username}"
