from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField("카테고리명", max_length=50)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField("책이름", max_length=100)
    content = models.TextField("내용")
    author = models.CharField("저자", max_length=100)
    link = models.CharField("책구매링크", max_length=200)
    img = models.CharField("이미지URL", max_length=200)
    best_seller_rank = models.CharField("베스트셀러순위", max_length=50)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
