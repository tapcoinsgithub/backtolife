from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import RegistrationSerializer, LoginSerializer, GetUserSerializer
from .models import *
from decouple import config
import binascii
import os
import json
from django.utils.timezone import make_aware
import requests
from datetime import datetime, timedelta
from random import randrange
import bcrypt
from django.core.exceptions import ObjectDoesNotExist

@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    data = {}
    try:
        if serializer.is_valid():
            user = serializer.save()
            if user:
                if type(user) == dict:
                    return Response(user)
                data['response'] = "LoggedIn"
                data['username'] = user.username
                if user.logged_in:
                    newData = {
                        'response': "User already logged in.",
                        'username': "",
                        'token': "",
                        'level': 1,
                        'level_progress': 0
                    }
                    return Response(newData)
                user.logged_in = True
                user.is_active = True
                user.save()
                token = binascii.hexlify(os.urandom(config('TOKEN', cast=int))).decode()
                token1 = user.token
                token1.token = token
                token1.save()
                data['token'] = token
                data['level'] = user.level
                data['level_progress'] = user.level_progress
            else:
                confirm_password = request.data['confirm_password']
                if confirm_password == "":
                    data["response"] = "Registering"
                    data['username'] =  ""
                    data['token'] = ""
                    data['level'] = 1
                    data['level_progress'] = 0
                    return Response(data)
                else:
                    serializer = RegistrationSerializer(data=request.data)
                    if serializer.is_valid():
                        user = serializer.save()
                        if type(user) == str:
                            data["response"] = user
                            data['username'] =  ""
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
        data = {
            'response': "Something went wrong.",
            'username': "",
            'token': "",
            'level': 1,
            'level_progress': 0
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
        users_block_groups = BlockGroup.objects.filter(user_id=user.token_id)
        for block_group in users_block_groups:
            b_group = {
                "name": block_group.block_group_name,
                "token_list": block_group.app_tokens
            }
            block_groups.append(str(b_group))
        data['block_groups'] = block_groups
        data['response'] = "Success"
    except Exception as e:
        data['block_groups'] = []
        data['response'] = "Failed to get block groups."
    return Response(data)

@api_view(['POST'])
def save_block_group(request):
    token = request.data['token']
    block_group_name = request.data['block_group_name']
    app_tokens = request.data['app_tokens']
    token1 = Token.objects.get(token=token)
    user = User.objects.get(token=token1)
    data = {
        "response": "Success"
    }
    if block_group_name and app_tokens and token:
        try:
            BlockGroup.objects.create(user=user, block_group_name=block_group_name, app_tokens=app_tokens)
            data['response'] = "Success"
        except Exception as e:
            try:
                array_data = json.loads(app_tokens)
                BlockGroup.objects.create(user=user, block_group_name=block_group_name, app_tokens=array_data)
                data['response'] = "Success"
            except Exception as e:
                data['response'] = "Something went wrong."
    else:
        data['response'] = "Invalid information."
    return Response(data)

@api_view(['POST'])
def logout_view(request):
    session = request.data['token']
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
        lock_block_status = request.data['lock_block']
        locked = False
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        str_time_length = str(time_length)
        only_int_time = str_time_length.split(".")[0]
        int_time_length = int(only_int_time)
        if lock_block_status == "0":
            locked = True
        Block.objects.create(user=user, time_length=int_time_length, user_level=user.level, locked=locked)
        data['result'] = True
    except Exception as e:
        data['result'] = False
    return Response(data)

@api_view(['POST'])
def stop_block(request):
    data = {}
    try:
        token = request.data['token']
        take_ten_percent = request.data['take_ten_percent']
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        stopping_block = Block.objects.get(user=user, completed=False)
        if stopping_block.locked:
            data['result'] = False
            return Response(data)
        if take_ten_percent == "0":
            tempLevelprogress = user.level_progress
            if tempLevelprogress - 10 < 0:
                if user.level > 1:
                    user.level -= 1
                    user.level_progress = 100 + (tempLevelprogress - 10)
                else:
                    user.level_progress = 0
            else:
                user.level_progress -= 10
            user.save()
        stopping_block.delete()
        data['result'] = True
    except Exception as e:
        data['result'] = False
    return Response(data)

@api_view(['POST'])
def block_ended(request):
    print("IN BLOCK ENDED CALL")
    data = {}
    try:
        token = request.data['token']
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        ending_block = Block.objects.get(user=user, completed=False)
        if ending_block.user_level == user.level:
            ending_block.completed = True
            ending_block.save()
            current_max_time = (30 * user.level) * 60
            total_time_to_progress = current_max_time * 5
            block_time_length = ending_block.time_length
            block_locked_status = ending_block.locked
            progress_gained = total_time_to_progress/block_time_length
            percent_gained = 100 / progress_gained
            if block_locked_status:
                print("DOUBLED PERCENT GAINED")
                double_pg = percent_gained * 2
                user.level_progress += double_pg
            else:
                print("NORMAL BLOCK")
                user.level_progress += percent_gained
            if user.level_progress >= 100:
                user.level += 1
                user.level_progress = user.level_progress - 100
            user.save()
            data['result'] = True
            # data['user_level'] = user.level
            # data['user_level_progress'] = user.level_progress
        else:
            print("IN ELSE BLOCK")
            ending_block.delete()
            data['result'] = False
            # data['user_level'] = user.level
            # data['user_level_progress'] = user.level_progress
    except Exception as e:
        print(f"EXCEPTION HERE: {e}")
        data['result'] = False
        # data['user_level'] = 0
        # data['user_level_progress'] = 0
    return Response(data)

@api_view(['POST'])
def delete_block_group(request):
    data = {}
    try:
        token = request.data['token']
        block_group_name = request.data['block_group_name']
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        deleting_block_group = BlockGroup.objects.filter(user_id=user.token_id, block_group_name=block_group_name)
        deleting_block_group.delete()
        data['response'] = True
    except Exception as e:
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
        editing_block_group = editing_block_groups[0]
        editing_block_group.block_group_name = block_group_name
        editing_block_group.app_tokens = array_data
        editing_block_group.save()
        data['response'] = "Success"
    except Exception as e:
        data['response'] = "Failed to update."
    return Response(data)

@api_view(['GET'])
def get_user_info(request):
    data = {}
    try:
        token = request.GET.get('token', None)
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        data['result'] = True
        data['username'] = user.username
        data['user_level'] = user.level
        data['user_level_progress'] = user.level_progress
        if user.phone_number != None:
            data['user_phone_number'] = user.phone_number
        else:
            data['user_phone_number'] = "None"
        return Response(data)
    except Exception as e:
        data['result'] = False
        data['username'] = "None"
        data['user_level'] = 1
        data['user_level_progress'] = 0
        data['user_phone_number'] = "None"
        return Response(data)
    
@api_view(['POST'])
def save_phone_number(request):
    data = {}
    try:
        token = request.data['token']
        _token = Token.objects.get(token=token)
        user = User.objects.get(token=_token)
        phone_number = request.data['phone_number']
        code = ""
        for i in range(4):
            num = randrange(10)
            code += str(num)
        right_now = make_aware(datetime.now())
        try:
            requests.post('https://textbelt.com/text', {
                'phone': phone_number,
                'message': f'Your temporary code is: {code}',
                'key': config('TEXT_BELT_KEY'),
            })
            try:
                text_tracker = TextTracker.objects.get(active=True)
                text_tracker.count += 1
                text_tracker.save()
            except:
                text_tracker = TextTracker.objects.create(count=1, active=True)
            user.p_code = int(code)
            user.p_code_time = right_now
            user.save()
            data['result'] = True
        except Exception as e:
            data['result'] = False
    except Exception as e:
        data['result'] = False
    return Response(data)

@api_view(['POST'])
def confirm_code(request):
    data = {}
    try:
        right_now = make_aware(datetime.now())
        token = request.data['token']
        _token = Token.objects.get(token=token)
        user = User.objects.get(token=_token)
        code = request.data['code']
        phone_number = request.data['phone_number']
        p_code_datetime_limit = user.p_code_time + timedelta(minutes=5)
        if user.p_code == int(code):
            if p_code_datetime_limit > right_now:
                user.phone_number = phone_number
                user.p_code = None
                user.p_code_time = None
                user.save()
                data['result'] = True
                data['response'] = "Successfully saved phone number."
            else:
                data['result'] = False
                data['response'] = "Code time limit reached."
        else:
            data['result'] = False
            data['response'] = "Invalid code."
    except Exception as e:
        data['result'] = False
        data['response'] = "Something went wrong."
    return Response(data)

@api_view(['POST'])
def send_username(request):
    phone_number = request.data['phone_number']
    data = {
        "response": True,
        "message" : ""
    }

    try:
        user = User.objects.get(phone_number=phone_number)
        data['message'] = "BEFORE SEND TEXT"
        requests.post('https://textbelt.com/text', {
            'phone': phone_number,
            'message': f'Your username is: {user.username}',
            'key': config('TEXT_BELT_KEY'),
        })
        try:
            text_tracker = TextTracker.objects.get(active=True)
            text_tracker.count += 1
            text_tracker.save()
        except:
            text_tracker = TextTracker.objects.create(count=1, active=True)
        data['message'] = "RESPONSE IS A SUCCESS"
    except Exception as e:
        data['response'] = False
        data['message'] = f"{e}"
    
    return Response(data)

@api_view(['POST'])
def send_code(request):
    phone_number = request.data['phone_number']
    code = ""
    for i in range(4):
        num = randrange(10)
        code += str(num)
    data = {}
    right_now = make_aware(datetime.now())
    try:
        user = User.objects.get(phone_number=phone_number)
        requests.post('https://textbelt.com/text', {
            'phone': phone_number,
            'message': f'Your temporary code is: {code}',
            'key': config('TEXT_BELT_KEY'),
        })
        try:
            text_tracker = TextTracker.objects.get(active=True)
            text_tracker.count += 1
            text_tracker.save()
        except:
            text_tracker = TextTracker.objects.create(count=1, active=True)
        user.p_code = int(code)
        user.p_code_time = right_now
        user.save()
        data['response'] = True
    except Exception as e:
        data['response'] = False    
    return Response(data)

@api_view(['POST'])
def change_password(request):
    if request.data['code'] == "Change_Password":
        data = {
            "response": True,
            "message": "",
            "error_type": 0,
            "expired": False
        }
        try:
            password = request.data['password']
            if password.strip() == "":
                data["response"] = False
                data["error_type"] = 0
                data["message"] = "Password can't be blank."
                return Response(data)
            token = request.data['token']
            _token = Token.objects.get(token=token)
            user = User.objects.get(token=_token)
            newPW = bcrypt.hashpw(password.encode(config('ENCODE')), user.password.encode(config('ENCODE')))
            if newPW == user.password.encode(config('ENCODE')):
                data["response"] = False
                data["error_type"] = 1
                data["message"] = "Password can't be previous password."
                return Response(data)
            salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
            hashed = bcrypt.hashpw(password.encode(config('ENCODE')), salt).decode()
            user.password = hashed
            user.save()
            data["response"] = True
            data["error_type"] = 0
            data["message"] = "Success"
            data['expired'] = False
        except:
            data["response"] = False
            data["error_type"] = 3
            data["message"] = "Something went wrong."
        return Response(data)
    data = {
        "response": True,
        "expired": False,
        "message": "",
        "error_type": 0
    }
    code = request.data['code']
    password = request.data['password']
    if password.strip() == "":
        data["response"] = False
        data["error_type"] = 0
        data["message"] = "Password can't be blank."
        data["expired"] = False
        return Response(data)
    user = None
    try:
        user = User.objects.get(p_code=int(code))
    except:
        data['response'] = False
        data["error_type"] = 3
        data['message'] = "Something went wrong."
        data['expired'] = False
        return Response(data)
    newPW = bcrypt.hashpw(password.encode(config('ENCODE')), user.password.encode(config('ENCODE')))
    if newPW == user.password.encode(config('ENCODE')):
        data["response"] = False
        data["error_type"] = 1
        data["message"] = "Password can't be previous password."
        data["expired"] = False
        return Response(data)
    
    code_datetime_limit = user.p_code_time + timedelta(minutes=5)
    right_now = make_aware(datetime.now())
    try:
        if code_datetime_limit > right_now:
            salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
            hashed = bcrypt.hashpw(password.encode(config('ENCODE')), salt).decode()
            user.password = hashed
            user.save()
            data['message'] = f"Successfully saved password."
        else:
            data["response"] = False
            data['message'] = "Time limit reached. Invalid code."
            data["error_type"] = 2
            data['expired'] = True
    except:
        data['response'] = False
        data["error_type"] = 3
        data['message'] = "Something went wrong."
        data['expired'] = False

    return Response(data)

@api_view(['POST'])
def confirm_password(request):
    data = {}
    try:
        token = request.data['token']
        _token = Token.objects.get(token=token)
        user = User.objects.get(token=_token)
        password = request.data['password']
        serializer_data = {
            "username" : user.username,
            "password" : password
        }
        serializer = LoginSerializer(data=serializer_data)
        if serializer.is_valid():
            _user = serializer.save()
            if _user != None:
                if type(_user) == dict:
                    data['response'] = False
                    return Response(data)
                data['response'] = True
            else:
                data['response'] = False
    except Exception as e:
        data['response'] = False
    return Response(data)

@api_view(['POST'])
def save_username(request):
    data = {}

    try:
        token = request.data['token']
        _token = Token.objects.get(token=token)
        user = User.objects.get(token=_token)
        username = request.data['username']
        try:
            User.objects.get(username=username)
            data['response'] = False
            data['message'] = "Duplicate username."
        except:
            user.username = username
            user.save()
            data['response'] = True
            data['message'] = username
    except Exception as e:
        data['response'] = False
        data['message'] = "Something went wrong."
    return Response(data)

@api_view(['GET'])
def get_current_block_time(request):
    data = {
        "result": True,
        "isBlocking": True,
        "blockEnded": False,
        "currentTime": 0,
        "initialTime": 0
    }
    try:
        token = request.GET.get('token', None)
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        check_block = Block.objects.get(user=user, completed=False)
        right_now = make_aware(datetime.now())
        block_time_length = check_block.time_length
        time_passed_check = check_block.created_at + timedelta(seconds=block_time_length)
        if time_passed_check > right_now:
            # hasnt run out of time yet
            time_difference = time_passed_check - right_now
            time_difference_in_seconds = time_difference.total_seconds()
            data['currentTime'] = int(time_difference_in_seconds)
            data['initialTime'] = block_time_length
        else:
            data['blockEnded'] = True
        return Response(data)
    except Block.DoesNotExist:
        data['isBlocking'] = False
        return Response(data)
    except Exception as e:
        data['result'] = False
        return Response(data)
