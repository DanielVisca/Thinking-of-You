from django.http import HttpResponse, JsonResponse
from v1.models import *
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

import json
import server.secure as secure
import requests

# Security
from django.contrib.auth.hashers import make_password, check_password
from secrets import token_urlsafe


# Create your views here.

@api_view(['post'])
@parser_classes([JSONParser])
def send_toy(request):
    requestJSONh = json.loads(request.header)

    requestJSONb = json.loads(request.body)
    auth_token = requestJSONh['key']
    send_to_id = requestJSONb["send_to_phone_number"]
    try:
        receiver = User.objects.get(phone_number=send_to_id)
        sender = User.objects.get(auth_token=auth_token)
        
        # Create a 'Thinking of You' object
        TOY.objects.create(
            sender=sender,
            receiver=receiver,
        )
    except ObjectDoesNotExist:
        return JsonResponse(status=400, data={'success': False, 'msg': 'send failure'})


    return JsonResponse({'success': True})

@api_view(['post'])
@parser_classes([JSONParser])
def init(request):
    """
    When a user logs in, this method is called. Check if the user is in the database,
    if they are return auth token and mark as active, if they aren't, deny access.
    """
    try:
        requestJSON = json.loads(request.body)
        print("request: "+ str(requestJSON))
        user_phone_number = requestJSON['phone_number']
        user_password = requestJSON['password']

        # Authentication, might throw an ObjectDoesNotExist error
        user = user_authenticate(user_phone_number,user_password)
        if user is None:
            print("Authentication failed")
            user = User.objects.get(phone_number=user_phone_number, password=user_password)
        else:
            print("authentication worked")

        # Set the user to active and generate an auth token for them
        user.active = True
        user_auth_token = token_urlsafe(64)
        user.auth_token = user_auth_token
        user.save()

        return JsonResponse(data={
            'success': True,
            'user_auth_token': user.auth_token
        })

    except (json.JSONDecodeError):
        # These errors imply invalid json, so we send 400
        return JsonResponse(status=400, data={'success': False})
    except (KeyError):
        # These errors imply invalid json, so we send 400
        return JsonResponse(status=400, data={'success': False})

    except Exception as e: # django.core.exceptions.ObjectDoesNotExist
        # All other errors imply invalid authentication, so we send 401
        print(e)
        return JsonResponse(status=401, data={'success': False})

    # Shouldn't get here, something's gone wrong
    return JsonResponse(status=500, data={'success': False})


# Helper Functions
def user_authenticate(user_phone_number=None, password=None, first_name=None, last_name=None, phone_number=None, username=None):
    """
    Authenticate a user
    """
    try:
        user = User.objects.get(phone_number=user_phone_number)
        pwd = User.password
        pwd_valid = check_password(password, pwd)
        if pwd_valid is False:
            print("wrong password")
            return None
        else: return User
    except: # User does not exist, creating new driver
        hashed_pwd = make_password(password)
        user = User.objects.create(phone_number=user_phone_number,password=hashed_pwd)
        #user = User.objects.create(first_name=first_name,last_name=last_name,phone_number=user_phone_number,password=hashed_pwd)
        print("User: " + str(user))
        pwd_valid = check_password(password, hashed_pwd)
        return user