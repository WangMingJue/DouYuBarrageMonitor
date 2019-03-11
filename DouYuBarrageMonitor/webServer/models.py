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


class SignIn(models.Model):
    sign_in_id = models.AutoField(primary_key=True)
    douyu_id = models.IntegerField()
    douyu_name = models.CharField(max_length=200)
    room_id = models.IntegerField()
    sign_in_time = models.DateTimeField()
    sign_in_date = models.DateField()
    sign_in_score = models.IntegerField()
    is_continuous = models.BooleanField()
    continuous_day = models.IntegerField()

    def return_model(self):
        return self.douyu_id, self.room_id, self.sign_in_time, self.sign_in_date, self.douyu_name
