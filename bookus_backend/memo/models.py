from django.db import models
from accounts.models import User
from books.models import Book
# Create your models here.


class Memo(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    book=models.ForeignKey(Book,on_delete=models.SET_NULL,null=True)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    