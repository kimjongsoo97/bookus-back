from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from meeting.models import Meeting

class Content(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('DISCUSSION', '토론'),
        ('QUIZ', '퀴즈'),
        ('BOOK_REVIEW', '독후감'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='contents')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contents')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reveal_date = models.DateTimeField(null=True, blank=True)  # 퀴즈 정답 공개, 독후감 합본 공개용
    word_limit = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(50)])  # 독후감 글자 수 제한
   
    def __str__(self):
        return f"{self.content_type}: {self.title} in {self.meeting.name}"

    class Meta:
        indexes = [
            models.Index(fields=['meeting', 'content_type']),
        ]

class DiscussionReply(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='discussion_replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.nickname} on {self.content.title}"

class QuizReply(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='quiz_replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    is_correct = models.BooleanField(default=False)  # 모임장이 정답 여부 표시
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz reply by {self.user.nickname} on {self.content.title}"

class BookReview(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='book_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Book review by {self.user.nickname} on {self.content.title}"

    class Meta:
        unique_together = ('content', 'user')

class BookReviewCompilation(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE, related_name='compilation')
    compiled_body = models.TextField()
    compiled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compilation for {self.content.title}"