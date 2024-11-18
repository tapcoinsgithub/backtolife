from rest_framework import serializers
from .models import User, Token
import bcrypt
from decouple import config
import binascii
import os

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=config('CHAR', cast=int))

    def create(self, validated_data):
        try:
            print("IN SERIALIZER")
            user = User.objects.get(username=validated_data['username'])
            if user:
                print("RETURNING USER")
                print(user)
                return user   
            else:
                print("RETURNING FALSE")
                return False
        except Exception as e:
            print("IN EXCEPTION")
            return False
        
class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=config('CHAR', cast=int))
 
    def create(self, validated_data):
        try:
            uName = validated_data.pop("username")
            print("VALIDATED DATA USERNAME")
            print(uName)
            if len(uName) <=1 or uName is None:
                return "Username must be greater than two characters long."
            for char in uName:
                if char == " ":
                    return "Username cannot have any spaces."
            print("11")
            token = binascii.hexlify(os.urandom(config('TOKEN', cast=int))).decode()
            print("12")
            token1 = Token.objects.create(token=token)
            print("13")
            try:
                user = User.objects.create(token=token1, username=uName)
                print("CREATED USER BELOW")
                print(user)
            except Exception as e:
                print("IS AN ERROR IN SERIALIZER")
                newError = str(e)
                newErr = newError.split("DETAIL:")[1]
                error = newErr.split("=")[1]
                return error
            print("RETURNING THE USER NOW")
            return user
        except:
            return "Something went wrong."
        
class GetUserSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=config('TK', cast=int))

    def create(self, validated_data):
        token1 = None
        user = None
        try:
            for token in Token.objects.all():
                if token.token == validated_data['token']:
                    token1 = token
                    break
            for user in User.objects.all():
                if user.token.token == token1.token:
                    user = user
                    break
        except:
            return False
        if user:
            return user
        else:
            return False