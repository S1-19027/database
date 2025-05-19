from django.db import models
from userapp.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.


class AI_CustomerService(models.Model):
    id = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    version = models.CharField(max_length=20)

    class Meta:
        db_table = "ai_customer_service"

    def __str__(self):
        return self.nickname


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Human_CustomerService(models.Model):
    staff_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True,default='cy')
    password = models.CharField(max_length=128,default='123456')  # 建议用Django的make_password加密
    online_status = models.BooleanField(default=False, db_index=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])

    class Meta:
        db_table = "human_customer_service"

    def __str__(self):
        return f"Staff {self.staff_id}"


class Consultation(models.Model):
    consultation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_service = models.ForeignKey(
        Human_CustomerService, on_delete=models.SET_NULL, null=True, blank=True
    )
    ai_service = models.ForeignKey(
        AI_CustomerService, on_delete=models.SET_NULL, null=True, blank=True
    )
    consultation_time = models.DateTimeField(db_index=True)
    user_rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )

    class Meta:
        db_table = "consultation"
        indexes = [
            models.Index(fields=["user", "customer_service"]),
        ]

    def __str__(self):
        return f"Consultation {self.consultation_id}"


class FAQ(models.Model):
    question_id = models.AutoField(primary_key=True)
    question = models.TextField()
    standard_answer = models.TextField()

    class Meta:
        db_table = "faq"

    def __str__(self):
        return f"FAQ {self.question_id}"


class ConversationRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    time = models.DateTimeField(db_index=True)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_service = models.ForeignKey(
        Human_CustomerService, on_delete=models.SET_NULL, null=True, blank=True
    )
    ai_service = models.ForeignKey(
        AI_CustomerService, on_delete=models.SET_NULL, null=True, blank=True
    )
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('user', '用户'),
        ('ai', 'AI客服'),
        ('human', '人工客服'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    class Meta:
        db_table = "conversation_record"
        indexes = [
            models.Index(fields=["user", "consultation"]),
        ]

    def __str__(self):
        return f"Record {self.record_id}"
