from django.db import models
from accounts.models import User

# Create your models here.
class Community(models.Model):
    STATUS_DELETE_CHOICES = [("UNDELETE", "삭제 안함"), ("DELETE", "삭제")]
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='communities')
    title=models.CharField(max_length=20,null=False)
    content=models.TextField(null=False)
    img=models.ImageField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    delete_status = models.CharField(max_length=20, choices=STATUS_DELETE_CHOICES, default="UNDELETE")
