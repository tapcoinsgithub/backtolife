from django.db import models
from decouple import config
from django.contrib.postgres.fields import ArrayField

class Token(models.Model):
    token = models.CharField(max_length=config('TK', cast=int), null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(models.Model):
    username = models.CharField(max_length=10, unique=True, null=True)
    password = models.CharField(max_length=config('CHAR', cast=int), unique=False, null=True)
    token = models.OneToOneField(Token, on_delete=models.CASCADE, primary_key=True, null=False)
    level = models.IntegerField(verbose_name="user level", null=True, default=1)
    level_progress = models.IntegerField(verbose_name="user level progress", null=True, default=0)
    phone_number = models.CharField(max_length=16, null=True, unique=True, default=None)
    p_code = models.IntegerField(null=True)
    p_code_time = models.DateTimeField(verbose_name="phone code time added", null=True)
    logged_in = models.BooleanField(verbose_name="logged in", default=False)
    is_active = models.BooleanField(verbose_name="is active", default=False, null=True)
    last_active_date = models.DateTimeField(verbose_name="last active date", auto_now=True, null=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)

class BlockGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    block_group_name = models.CharField(max_length=10, null=True)
    app_tokens = ArrayField(ArrayField(models.CharField(max_length=260, default=""), null=True, blank=True), null=True, blank=True, default=list)
    created_at = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="updated at", auto_now=True)

class Block(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    time_length = models.IntegerField(verbose_name="time length", null=True, default=0)
    completed = models.BooleanField(verbose_name="completed block", default=False, null=True)
    user_level = models.IntegerField(verbose_name="users level", null=True, default=1)
    locked = models.BooleanField(verbose_name="block lock", default=False, null=True)
    created_at = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="updated at", auto_now=True)

class TextTracker(models.Model):
    count = models.IntegerField(verbose_name="text count", null=True)
    active = models.BooleanField(verbose_name="active tracker", default=False)
