# Generated by Django 4.2.11 on 2024-12-05 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BackToLife_App', '0008_texttracker_user_p_code_user_p_code_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
    ]
