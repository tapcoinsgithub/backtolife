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
                confirm_password = request.data['confirm_password']
                if confirm_password == "":
                    print("SHOWING CONFIRM PASSWORD")
                    data["response"] = "Registering"
                    data['username'] =  ""
                    data['token'] = ""
                    data['level'] = 1
                    data['level_progress'] = 0
                    return Response(data)
                else:
                    print("10")
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
        take_ten_percent = request.data['take_ten_percent']
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
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
        # If user level progress is negative then decrease level and set level progress equal to 100 minus the |negative number| TODO!!!
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
            # do a check here in the future to make sure that the time for the block has actually ended.
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
                # Adjust user level progress based on if the percent gained goes above 100 percent TODO!!!
                user.level_progress = user.level_progress - 100
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
        print(f"EXCEPTION HERE: {e}")
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
        # Function to send confirmation text
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
            print("88888888888")
            print("IN EXCEPTION")
            print(e)
            data['result'] = False
    except Exception as e:
        print(f"Exception here: {e}")
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
            print("CODE MATCHES")
            if p_code_datetime_limit > right_now:
                print("DATE IS VALID")
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
        print(f"Exception here: {e}")
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
        print(f"USER PCODE BEFORE: {user.p_code}")
        print(f"CODE TO SAVE: {code}")
        user.p_code = int(code)
        user.p_code_time = right_now
        user.save()
        data['response'] = True
    except Exception as e:
        print("SOMETHING WENT WRONG")
        print(e)
        data['response'] = False    
    print("DATA IS HERE")
    print(data)
    return Response(data)

@api_view(['POST'])
def change_password(request):
    # if request.data['code'] == "SAVE":
    #     print("IN SAVED IF STATMENT")
    #     data = {
    #         "response": True,
    #         "message": "",
    #         "error_type": 0
    #     }
    #     try:
    #         print("IN THE TRY BLOCK")
    #         password = request.data['password']
    #         if password.strip() == "":
    #             data["response"] = False
    #             data["error_type"] = 0
    #             data["message"] = "Password can't be blank."
    #             return Response(data)
    #         print("AFTER CHECKING FOR EMPTY")
    #         token = Token.objects.get(token=request.data['token'])
    #         user = User.objects.get(token=token)
    #         print("GOT USER")
    #         newPW = bcrypt.hashpw(password.encode(config('ENCODE')), user.password.encode(config('ENCODE')))
    #         print("GOT NEW PW")
    #         if newPW == user.password.encode(config('ENCODE')):
    #             print("PASSWORD IS PREVIOUS PASSWORD")
    #             data["response"] = False
    #             data["error_type"] = 1
    #             data["message"] = "Password can't be previous password."
    #             print(data)
    #             return Response(data)
    #         print("PASSWORDS ARE DIFFERENT")
    #         salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
    #         print("GOT THE SALT")
    #         hashed = bcrypt.hashpw(password.encode(config('ENCODE')), salt).decode()
    #         print("GOT THE HASHED")
    #         user.password = hashed
    #         print("SET USER PASSWORD")
    #         user.is_guest = False
    #         print("SET THE GUEST")
    #         user.save()
    #     except:
    #         print("IN EXCEPT BLOCK")
    #         data["response"] = False
    #         data["error_type"] = 3
    #         data["message"] = "Something went wrong."
    #     return Response(data)
    if request.data['code'] == "Change_Password":
        print("IN Change_Password IF STATMENT")
        data = {
            "response": True,
            "message": "",
            "error_type": 0,
            "expired": False
        }
        try:
            print("IN THE TRY BLOCK")
            password = request.data['password']
            if password.strip() == "":
                data["response"] = False
                data["error_type"] = 0
                data["message"] = "Password can't be blank."
                return Response(data)
            print("AFTER CHECKING FOR EMPTY")
            token = request.data['token']
            _token = Token.objects.get(token=token)
            user = User.objects.get(token=_token)
            print("GOT USER")
            newPW = bcrypt.hashpw(password.encode(config('ENCODE')), user.password.encode(config('ENCODE')))
            print("GOT NEW PW")
            if newPW == user.password.encode(config('ENCODE')):
                print("PASSWORD IS PREVIOUS PASSWORD")
                data["response"] = False
                data["error_type"] = 1
                data["message"] = "Password can't be previous password."
                print(data)
                return Response(data)
            print("PASSWORDS ARE DIFFERENT")
            salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
            print("GOT THE SALT")
            hashed = bcrypt.hashpw(password.encode(config('ENCODE')), salt).decode()
            print("GOT THE HASHED")
            user.password = hashed
            print("SET USER PASSWORD")
            user.save()
            data["response"] = True
            data["error_type"] = 0
            data["message"] = "Success"
            data['expired'] = False
        except:
            print("IN EXCEPT BLOCK")
            data["response"] = False
            data["error_type"] = 3
            data["message"] = "Something went wrong."
        print("DATA IS BELOW")
        print(data)
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
            print("Login Serializer is valid")
            print(serializer.is_valid())
            _user = serializer.save()
            if _user != None:
                if type(_user) == dict:
                    print("Is Error")
                    data['response'] = False
                    return Response(data)
                print("GOT THE USER")
                data['response'] = True
            else:
                print("DID NOT GET THE USER")
                data['response'] = False
    except Exception as e:
        print(f"Exception here: {e}")
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
            print("GOT USER WITH THE GIVEN USERNAME")
        except:
            user.username = username
            user.save()
            print("SAVED THE NEW USERNAME")
            data['response'] = True
            data['message'] = username
    except Exception as e:
        print(f"Exception here: {e}")
        data['response'] = False
        data['message'] = "Something went wrong."
    return Response(data)

@api_view(['GET'])
def get_current_block_time(request):
    data = {
        "result": True,
        "isBlocking": True,
        "currentTime": "Current Time"
    }
    try:
        token = request.GET.get('token', None)
        token1 = Token.objects.get(token=token)
        user = User.objects.get(token=token1)
        check_block = Block.objects.get(user=user, completed=False)
        print(f"CHECK BLOCK IS HERE: {check_block}")
        right_now = make_aware(datetime.now())
        block_time_length = check_block.time_length
        time_passed_check = check_block.created_at + timedelta(minutes=block_time_length)
        if time_passed_check > right_now:
            # hasnt run out of time yet
            time_difference = time_passed_check - right_now
            print(f"TIME DIFF HERE: {time_difference}")
            # Subtract right_now from time_pass_check to see if that gives the correct amount of min/hours left in block
            # return the answer to the frontend to start the time again from that time.
        else:
            # has run out of time
            # Send string back saying that block has ended to call end_block function
            data['currentTime'] = "Block Ended"
        return Response(data)
    except Exception as e:
        print(f"EXCEPTION IS HERE: {e}")
        if e == "Block matching query does not exist.":
            data['isBlocking'] = False
        else:
            data['isBlocking'] = False
            data['result'] = False
        return Response(data)
