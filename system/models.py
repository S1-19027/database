from django.db import models

# Create your models here.

class Update(models.Model):
    update_id = models.AutoField(primary_key=True)
    previous_version = models.CharField(max_length=20)
    current_version = models.CharField(max_length=20)
    update_time = models.DateTimeField()
    
    class Meta:
        db_table = 'update'
        
    def __str__(self):
        return f"Update to {self.current_version}"