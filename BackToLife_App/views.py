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
                        'token': ""
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
                        return Response(data)
                    data['response'] = "Registered"
                    data['username'] = user.username
                    token = user.token
                    data['token'] = token.token
                    user.logged_in = True
                    user.is_active = True
                    user.save()
                    token.save()
                else: 
                    data = {
                        'response': "Something went wrong registering.",
                        'username': "",
                        'token': ""
                    }
    except Exception as e:
        print(e)
        data = {
            'response': "Something went wrong.",
            'username': "",
            'token': ""
        }
    return Response(data)

@api_view(['GET'])
def get_block_groups(request):
    token = request.GET.get('token', None)
    token1 = Token.objects.get(token=token)
    user = User.objects.get(token=token1)
    data = {}
    try:
        block_groups = []
        users_block_groups = BlockGroup.objects.get(user_id=user.token_id)
        print("GOT USER BLOCK GROUPS")
        print(users_block_groups)
        for block_group in users_block_groups:
            b_group = {
                "name": block_group.block_group_name,
                "token_list": block_group.app_tokens
            }
            block_groups.append(b_group)
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