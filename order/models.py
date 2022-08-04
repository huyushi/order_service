from django.db import models


# Create your models here.

class Img(models.Model):
    img_url = models.ImageField(upload_to='img')


class Book(models.Model):
    """
    book table
    """
    name = models.CharField(max_length=32, verbose_name='书籍的名称')
    price = models.CharField(max_length=32, verbose_name='书籍的价格')
    
    class Meta:
        db_table = 'book'
        verbose_name = '书籍表'
        verbose_name_plural = verbose_name