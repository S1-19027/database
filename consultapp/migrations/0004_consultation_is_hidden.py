# Generated by Django 4.1 on 2025-05-30 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultapp', '0003_conversationrecord_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultation',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]
