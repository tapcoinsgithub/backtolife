from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import RegistrationSerializer, LoginSerializer, GetUserSerializer
from .models import *
from decouple import config
import binascii
import os
import json

@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    data = {}
    try:
        print("1")
        if serializer.is_valid():
            print("2")
            print(serializer.is_valid())
            user = serializer.save()
            if user:
                print("3")
                print(user)
                if type(user) == dict:
                    print("4")
                    return Response(user)
                print("5")
                data['response'] = "LoggedIn"
                data['username'] = user.username
                if user.logged_in:
                    print("6")
                    newData = {
                        'response': "User already logged in.",
                        'username': "",
                        'token': "",
                        'level': 1,
                        'level_progress': 0
                    }
                    return Response(newData)
                print("7")
                user.logged_in = True
                user.is_active = True
                user.save()
                print("8")
                token = binascii.hexlify(os.urandom(config('TOKEN', cast=int))).decode()
                token1 = user.token
                token1.token = token
                token1.save()
                print("9")
                data['token'] = token
                data['level'] = user.level
                data['level_progress'] = user.level_progress
                print("THE TOKEN IS BELOW")
                print(token)
            else:
                print("10")
                serializer = RegistrationSerializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save()
                    if type(user) == str:
                        data["response"] = user
                        data['username'] =  "",
                        data['token'] = ""
                        data['level'] = 1
                        data['level_progress'] = 0
                        return Response(data)
                    data['response'] = "Registered"
                    data['username'] = user.username
                    token = user.token
                    data['token'] = token.token
                    data['level'] = user.level
                    data['level_progress'] = user.level_progress
                    user.logged_in = True
                    user.is_active = True
                    user.save()
                    token.save()
                else: 
                    data = {
                        'response': "Something went wrong registering.",
                        'username': "",
                        'token': "",
                        'level': 1,
                        'level_progress': 0
                    }
    except Exception as e:
        print(e)
        data = {
            'response': "Something went wrong.",
            'username': "",
            'token': "",
            'level': 1,
            'level_progress': 0
        }
    print("RETURNING DATA HERE:")
    print(data)
    return Response(data)

@api_view(['GET'])
def get_block_groups(request):
    token = request.GET.get('token', None)
    token1 = Token.objects.get(token=token)
    user = User.objects.get(token=token1)
    data = {}
    try:
        block_groups = []
        users_block_groups = BlockGroup.objects.filter(user_id=user.token_id)
        print("GOT USER BLOCK GROUPS")
        print(users_block_groups)
        for block_group in users_block_groups:
            b_group = {
                "name": block_group.block_group_name,
                "token_list": block_group.app_tokens
            }
            block_groups.append(str(b_group))
        data['block_groups'] = block_groups
        data['response'] = "Success"
    except Exception as e:
        print(f"E IS HERE: {e}")
        data['block_groups'] = []
        data['response'] = "Failed to get block groups."
    return Response(data)

@api_view(['POST'])
def save_block_group(request):
    token = request.data['token']
    block_group_name = request.data['block_group_name']
    app_tokens = request.data['app_tokens']
    print(f"BLOCK GROUP NAME: {block_group_name}")
    print(f"APP TOKENS LIST: {app_tokens}")
    print(f"APP TOKENS LIST TYPE: {type(app_tokens)}")
    print(f"TOKEN: {token}")
    token1 = Token.objects.get(token=token)
    print("Got TOKEN")
    user = User.objects.get(token=token1)
    print("GOT USER")
    data = {
        "response": "Success"
    }
    if block_group_name and app_tokens and token:
        try:
            print("GETTING IN HERE AT ALL?")
            print("GETTING IN HERE AT ALL?")
            print("GETTING IN HERE AT ALL?")
            BlockGroup.objects.create(user=user, block_group_name=block_group_name, app_tokens=app_tokens)
            print("CREATED BLOCK GROUP")
            data['response'] = "Success"
        except Exception as e:
            print(f"E HERE: {e}")
            try:
                array_data = json.loads(app_tokens)
                print(array_data)
                print(type(array_data))
                BlockGroup.objects.create(user=user, block_group_name=block_group_name, app_tokens=array_data)
                print("CREATED BLOCK GROUP")
                data['response'] = "Success"
            except Exception as e:
                print(f"E IS NOW HERE: {e}")
                data['response'] = "Something went wrong."
    else:
        data['response'] = "Invalid information."
    return Response(data)

@api_view(['POST'])
def logout_view(request):
    session = request.data['token']
    print("THE TOKEN IS BELOW")
    print(session)
    data = {}
    token1 = None
    try:
        for token in Token.objects.all():
            if token.token == session:
                token1 = token
        data['result'] = "Success"
    except:
        data['result'] = "Failure"
        return Response(data)
    user = User.objects.get(token=token1)
    user.logged_in = False
    user.is_active = False
    token1.token = None
    token.save()
    user.save()
    return Response(data)

@api_view(['POST'])
def start_block(request):
    data = {}
    try:
        token = request.data['token']
        time_length = request.data['time_length']
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        str_time_length = str(time_length)
        only_int_time = str_time_length.split(".")[0]
        int_time_length = int(only_int_time)
        Block.objects.create(user=user, time_length=int_time_length, user_level=user.level)
        data['result'] = True
    except Exception as e:
        print(f"EXCEPTION HERE: {e}")
        data['result'] = False
    return Response(data)

@api_view(['POST'])
def stop_block(request):
    data = {}
    try:
        token = request.data['token']
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        stopping_block = Block.objects.get(user=user, completed=False)
        stopping_block.delete()
        data['result'] = True
    except Exception as e:
        print(f"EXCEPTION HERE: {e}")
        data['result'] = False
    return Response(data)

@api_view(['POST'])
def block_ended(request):
    data = {}
    try:
        token = request.data['token']
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        ending_block = Block.objects.get(user=user, completed=False)
        if ending_block.user_level == user.level:
            print("ENDING USER BLOCK")
            ending_block.completed = True
            ending_block.save()
            current_max_time = (30 * user.level) * 60
            total_time_to_progress = current_max_time * 5
            block_time_length = ending_block.time_length
            progress_gained = total_time_to_progress/block_time_length
            percent_gained = 100 / progress_gained
            user.level_progress += percent_gained
            print(f"PERCENT GAINED: {percent_gained}")
            if user.level_progress >= 100:
                print("PROGRESSING TO NEXT LEVEL")
                user.level += 1
                user.level_progress = 0
            user.save()
            data['result'] = True
            data['user_level'] = user.level
            data['user_level_progress'] = user.level_progress
            print("SUCCESSFULLY ENDED BLOCK")
        else:
            ending_block.delete()
            data['result'] = False
            data['user_level'] = user.level
            data['user_level_progress'] = user.level_progress
    except Exception as e:
        print(f"EXCEPTION HERE: {e}")
        data['result'] = False
        data['user_level'] = 0
        data['user_level_progress'] = 0
    return Response(data)

@api_view(['POST'])
def delete_block_group(request):
    data = {}
    try:
        token = request.data['token']
        print("REQUEST TOKEN")
        block_group_name = request.data['block_group_name']
        print("BGROUP NAME")
        token1 = Token.objects.get(token=token)
        print("GOT TOKEN OBJECT")
        user = User.objects.get(token=token1)
        print("GOT USER")
        deleting_block_group = BlockGroup.objects.filter(user_id=user.token_id, block_group_name=block_group_name)
        print("GOT DELETING BLOCK GROUP")
        deleting_block_group.delete()
        print("DELETE BLOCK GROUP")
        data['response'] = True
    except Exception as e:
        print("Something went wrong")
        print(e)
        data['response'] = False
    return Response(data)

@api_view(['POST'])
def edit_block_group(request):
    data = {}
    try:
        token = request.data['token']
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        block_group_name = request.data['block_group_name']
        old_block_group_name = request.data['old_block_group_name']
        app_tokens = request.data['app_tokens']
        array_data = json.loads(app_tokens)
        editing_block_groups = BlockGroup.objects.filter(user_id=user.token_id, block_group_name=old_block_group_name)
        print(editing_block_groups)
        editing_block_group = editing_block_groups[0]
        print(editing_block_group)
        editing_block_group.block_group_name = block_group_name
        editing_block_group.app_tokens = array_data
        editing_block_group.save()
        data['response'] = "Success"
    except Exception as e:
        print("Something went wrong")
        print(e)
        data['response'] = "Failed to update."
    return Response(data)