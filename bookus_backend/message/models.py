from django.db import models
from accounts.models import User
# Create your models here.


class Message(models.Model):
    STATUS_READ_CHOICES = [("UNREAD", "읽지 않음"), ("READ", "읽음")]
    STATUS_DELETE_CHOICES = [("UNDELETE", "삭제 안함"), ("DELETE", "삭제")]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # 이 쪽지를 갖고 있는 사용자 (보낸 사람 or 받은 사람)
    counterpart = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_partner')
    is_sender = models.BooleanField()  # 보낸 쪽지인지 여부
    title = models.CharField(max_length=20)
    content = models.TextField()
    read_status = models.CharField(max_length=10, choices=STATUS_READ_CHOICES, default="UNREAD")
    delete_status = models.CharField(max_length=20, choices=STATUS_DELETE_CHOICES, default="UNDELETE")
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        direction = "보낸 쪽지" if self.is_sender else "받은 쪽지"
        return f"[{direction}] {self.owner} ↔ {self.counterpart} / 제목: {self.title}"