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

# Pushing to device
from exponent_server_sdk import PushClient, PushMessage, PushResponseError, PushServerError, DeviceNotRegisteredError
from requests.exceptions import ConnectionError, HTTPError



# Security
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from secrets import token_urlsafe

# Timing
from django.utils import timezone
from datetime import datetime, timedelta, date
import pytz

# Create your views here.

@api_view(['post'])
@parser_classes([JSONParser])
def send_toy(request):
    requestJSON = json.loads(request.body)
    print(requestJSON)    
    auth_token = requestJSON['user_auth']
    send_to_id = requestJSON["phone_number"]
    print("TOY recieved")
    print("auth_token: " + auth_token )
    print("send_to_id: " + send_to_id)
    # Time
    tz = pytz.timezone('US/Eastern')
    dt = datetime.now(tz)
    try:
        receiver = User.objects.get(phone_number=send_to_id)
        sender = User.objects.get(auth_token=auth_token)
        
        # Create a 'Thinking of You' object
        toy = TOY.objects.create(
            sender=sender,
            receiver=receiver,
            time_sent=dt
        )
        toy.save()
        print("toy")
        print(toy)
        # send push notification
        send_push_message(receiver.token,sender.phone_number)
        return JsonResponse({'success': True})
    except ObjectDoesNotExist:
        # send via text
        print("Object Does Not Exist")
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
        expo_token = requestJSON['token']

        # Authentication, might throw an ObjectDoesNotExist error
        user = user_authenticate(user_phone_number,user_password)
        print("user in init")
        print(user)
        if user is None:
            print("Authentication failed")
            user = User.objects.get(phone_number=user_phone_number, password=user_password)
        else:
            print("authentication worked")

        # Set the user to active and generate an auth token for them
        user.active = True
        user_auth_token = token_urlsafe(64)
        user.auth_token = user_auth_token
        # save expo token
        print("User token before: " + str(user.token))
        user.token = expo_token
        user.save()

        return JsonResponse(data={
            'success': True,
            'user_auth_token': user.auth_token
        })

    except (json.JSONDecodeError):
        print("failed in 1")
        # These errors imply invalid json, so we send 400
        return JsonResponse(status=400, data={'success': False})
    except (KeyError):
        print("failed in 2")

        # These errors imply invalid json, so we send 400
        return JsonResponse(status=400, data={'success': False})

    except Exception as e: # django.core.exceptions.ObjectDoesNotExist
        # All other errors imply invalid authentication, so we send 401
        print(e)
        return JsonResponse(status=401, data={'success': False})

    # Shouldn't get here, something's gone wrong
    print("bad")
    return JsonResponse(status=500, data={'success': False})

@api_view(['post'])
@parser_classes([JSONParser])
def logoff(request):
    """
    Wrapper function for logging off driver in the event that they completed a shift without needing
    to be kicked out.
    :param request: (HTTPRequest) contains parameters to be used by the function, specifically the
    authorization token associated with the given driver
    :return: (JsonResponse) object containing relevant information about each shelter
    """
    try:
        requestJSON = json.loads(request.body)
        print(requestJSON)
        auth_token = requestJSON['authToken']
        user = User.objects.get(auth_token=auth_token)
        # Nullify their auth token
        user.auth_token = None
        user.active = False
        # Save to the database
        user.save()
        return JsonResponse({'success': True})

    except (json.JSONDecodeError, KeyError):
        # These errors imply invalid json, so we send 400
        return JsonResponse(status=400, data={'success': False})

    except Exception as e:
        print(e)
        return JsonResponse(status=401, data={'success': False})



@api_view(['post'])
@parser_classes([JSONParser])
def signup(request):
    """
    Create a new user given their phone number and a password
    """
    try:
        requestJSON = json.loads(request.body)
        print("request: "+ str(requestJSON))
        user_phone_number = requestJSON['phone_number']
        user_password = requestJSON['password']
        expo_token = requestJSON['token']

        hashed_pwd = make_password(user_password)
        pwd_valid = check_password(user_password, hashed_pwd)

        user_exists = user_authenticate(user_phone_number=user_phone_number)
        if not user_exists and pwd_valid:
    
            print("Creating a new user")
            user = User.objects.create(phone_number=user_phone_number,password=hashed_pwd)
            # Set the user to active and generate an auth token for them
            user.active = True
            user_auth_token = token_urlsafe(64)
            user.auth_token = user_auth_token
            # save expo token
            user.token = expo_token
            user.save()
            return JsonResponse({"success": True, "user_auth_token": user_auth_token})
        else:
            return JsonResponse({"success": False, "msg": "This is not a valid password"})
        #user = User.objects.create(first_name=first_name,last_name=last_name,phone_number=user_phone_number,password=hashed_pwd)
        print("User: " + str(user))
    except Exception as e:
        print(e)
        return JsonResponse(status=401, data={'success': False})

# Helper Functions
def user_authenticate(user_phone_number=None, password=None, first_name=None, last_name=None, phone_number=None, username=None):
    """
    Authenticate a user
    """
    try:

        user = User.objects.get(phone_number=user_phone_number)
        pwd = user.password
        pwd_valid = check_password(password, pwd)
        if pwd_valid is False:
            print("wrong password")
            return None
        else:
            return user
    except: # User does not exist, creating new user
        return None

def send_push_message(token, senders_phone_number):
    """
    Core function for sending messages, leveraged by other functions.
    :param token: (str) ExpoToken of user message is being sent to
    :param message: (str) Message to be sent to user
    :param extra: (json) Any additional information to be added
    :return:
    """
    message = "Somebody is thinking of you"
    try:
        
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=senders_phone_number))
        print("response")
        print(response)
    except PushServerError as exc: 
        print("got push server error")
        pass
    except (ConnectionError, HTTPError) as exc:
        print("got other error")
        pass

    try:
        response.validate_response()
    except DeviceNotRegisteredError: # Mark the push token as inactive
        from notifications.models import PushToken
        PushToken.objects.filter(token=token).update(active=False)
    except PushResponseError as exc: # Encountered some other per-notification error.
        pass
