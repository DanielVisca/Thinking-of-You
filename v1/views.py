from django.http import HttpResponse, JsonResponse
# from v1.models import *
# from rest_framework.decorators import api_view
# from rest_framework.decorators import parser_classes
# from rest_framework.parsers import JSONParser

# from django.shortcuts import render
# from django.contrib.auth.hashers import make_password, check_password
# from django.core.exceptions import ObjectDoesNotExist

# import json
# import server.secure as secure
# import requests
# # Create your views here.

# @api_view(['post'])
# @parser_classes([JSONParser])
# def send(request):
#     requestJSON = json.loads(request.body)
#     auth_token = requestJSON['auth_token']
#     send_to_id = requestJSON["send_to_id"]
#     try:
#         receiver = User.objects.get(pk=send_to_id)
#     except ObjectDoesNotExist:
#         return JsonResponse(status=400, data={'success': False, 'msg': 'send failure'})


#     return JsonResponse({'success': True})