from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=50, unique=True,default='cy1')
    password = models.CharField(max_length=128,default='123456')  # 建议用Django的make_password加密
    contact = models.CharField(max_length=100)
    membership_level = models.CharField(max_length=20)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.nickname
