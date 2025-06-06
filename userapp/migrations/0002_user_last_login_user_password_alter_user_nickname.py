# Generated by Django 4.1 on 2025-05-19 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(default='123456', max_length=128),
        ),
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(default='cy1', max_length=50, unique=True),
        ),
    ]
