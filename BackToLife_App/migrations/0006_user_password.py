# Generated by Django 4.2.11 on 2024-11-26 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BackToLife_App', '0005_rename_length_block_time_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=80, null=True),
        ),
    ]