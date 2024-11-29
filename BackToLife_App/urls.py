from django.urls import path
from .views import *

app_name = "backtolife_api"
urlpatterns = [
    path('user_login', login_view, name="loginUser"),
    path('get_block_groups', get_block_groups, name="getBlockGroups"),
    path("save_block_group", save_block_group, name="saveBlockGroup"),
    path("logout", logout_view, name="logout"),
    path("start_block", start_block, name="startBlock"),
    path("stop_block", stop_block, name="stopBlock"),
    path("block_ended", block_ended, name="blockEnded"),
    path("delete_block_group", delete_block_group, name="deleteBlockGroup"),
    path("edit_block_group", edit_block_group, name="editBlockGroup"),
    path("get_user_info", get_user_info, name="getUserInfo")
]