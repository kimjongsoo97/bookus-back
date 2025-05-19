# meetings/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from books.models import Book

class Meeting(models.Model):
    STATUS_DELETE_CHOICES = [
        ("UNDELETE", "삭제 안함"),
        ("DELETE", "삭제")
    ]
    STATUS_MEMBER_CHOICES = [
        ("MEETING_ADMIN", "모임장"),
        ("MEETING_USER", "모임사용자")
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        null=False,
        related_name='selected_meetings'
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meeting_date = models.DateTimeField()
    map_directions = models.JSONField(null=True, blank=True)
    meeting_directions = models.CharField(max_length=255, blank=False)
    max_members = models.PositiveBigIntegerField(
        default=3,
        validators=[
            MinValueValidator(1, message=_("최대 인원은 1명 이상이어야 합니다.")),
            MaxValueValidator(6, message=_("최대 인원은 6명을 초과할 수 없습니다."))
            ]
    )
    delete_status = models.CharField(
        max_length=20,
        choices=STATUS_DELETE_CHOICES,
        default='UNDELETE'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_meetings'
    )
    members = models.ManyToManyField(
        User,
        through='Membership',
        related_name='joined_meetings'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.creator and not Membership.objects.filter(user=self.creator, meeting=self).exists():
            Membership.objects.create(
                user=self.creator,
                meeting=self,
                member_status='MEETING_ADMIN'
            )

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['creator']),
            models.Index(fields=['book']),
        ]

class Membership(models.Model):
    STATUS_MEMBER_CHOICES = [
        ("MEETING_ADMIN", "모임장"),
        ("MEETING_USER", "모임사용자")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    member_status = models.CharField(
        max_length=20,
        choices=STATUS_MEMBER_CHOICES,
        default='MEETING_USER'
    )

    class Meta:
        unique_together = ('user', 'meeting')

    def __str__(self):
        return f"{self.user.nickname} in {self.meeting.name} ({self.member_status})"