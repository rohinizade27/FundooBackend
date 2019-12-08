from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from rest_framework import status
from django.http import HttpResponse
import json


class LoginRequired(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(" middleware executed")
        url = request.path
        print("url------>>>",url.split("/")[1])
        current_url = url.split("/")[1]
        if current_url == "note_api":
            print("This request required authentication")
            try:
                token = request.META['HTTP_AUTHORIZATION']
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                new_token = str(token).split("Bearer ")[1]
                print("token ===== >>>>>>", new_token)
                encoded_token = jwt_decode_handler(new_token)
                print(encoded_token)
                username = encoded_token['username']
                print(username)
                user = User.objects.get(username=username)
                try:
                    if user and user.is_active:
                        print("user is authenticated")
                        pass
                except User.DoesNotExist:
                    smd = {'success': False, 'message': 'login is required'}
                    return HttpResponse(json.dumps(smd), status=status.HTTP_400_BAD_REQUEST)
            except KeyError:
                if request.session:
                    user = request.user
                    if user.is_authenticated:
                        pass
                    else:
                        smd = {'success': False, 'message': 'Users credential not provided..!!'}
                        return HttpResponse(json.dumps(smd), status=status.HTTP_400_BAD_REQUEST)
                else:
                    smd = {'success': False, 'message': 'Users credential not provided..!!'}
                    return HttpResponse(json.dumps(smd), status=status.HTTP_400_BAD_REQUEST)
        else:
            print("This request does not required authentication")
        return self.get_response(request)
