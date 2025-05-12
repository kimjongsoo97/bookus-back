from django.db import models
from accounts.models import User
# Create your models here.


class Message(models.Model):
    STATUS_CHOICES=[
        ("UNREAD","읽지 않음"),
        ("READ","읽음")
    ]
    sender=models.ForeignKey(User,related_name='sent_messages',on_delete=models.CASCADE)
    reciever=models.ForeignKey(User,related_name='received_message',on_delete=models.CASCADE)
    title=models.CharField(max_length=20)
    content=models.TextField()
    create_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default="UNREAD")
    def __str__(self):
        return f"From {self.sender} to {self.receiver} - {self.get_status_display()}"