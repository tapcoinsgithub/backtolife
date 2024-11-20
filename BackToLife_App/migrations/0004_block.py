# Generated by Django 4.2.11 on 2024-11-20 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BackToLife_App', '0003_alter_blockgroup_app_tokens'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('length', models.IntegerField(default=0, null=True, verbose_name='time length')),
                ('completed', models.BooleanField(default=False, null=True, verbose_name='completed block')),
                ('user_level', models.IntegerField(default=1, null=True, verbose_name='users level')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='BackToLife_App.user')),
            ],
        ),
    ]
