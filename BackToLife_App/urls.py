from django.urls import path
from .views import *

app_name = "backtolife_api"
urlpatterns = [
    path('user_login', login_view, name="loginUser"),
    path('get_block_groups', get_block_groups, name="getBlockGroups"),
    path("save_block_group", save_block_group, name="saveBlockGroup"),
    path("logout", logout_view, name="logout")
]