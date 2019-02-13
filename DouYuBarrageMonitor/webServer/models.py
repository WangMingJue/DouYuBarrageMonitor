from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    douyu_id = models.IntegerField()
    douyu_name = models.CharField(max_length=200)


class Barrage(models.Model):
    barrage_id = models.AutoField(primary_key=True)
    douyu_id = models.IntegerField()
    douyu_name = models.CharField(max_length=200)
    barrage_content = models.TextField()
    user_level = models.IntegerField()
    user_image = models.TextField()
    room_id = models.IntegerField()
    barrage_time = models.DateTimeField()
    barrage_date = models.DateField()
    room_status = models.CharField(max_length=10)
