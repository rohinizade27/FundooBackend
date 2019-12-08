from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from rest_framework import status
from django.http import HttpResponse
import json


def user_login_required(view_func):

    def wrapper(request, *args,**kwargs):
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
                    return view_func(request, *args, **kwargs)
            except User.DoesNotExist:
                smd = {'success': False, 'message': 'login is required'}
                return HttpResponse(json.dumps(smd), status=status.HTTP_400_BAD_REQUEST)
        except KeyError :
            if request.session:
                user = request.user
                if user.is_authenticated:
                    return view_func(request, *args, **kwargs)
                else:
                    smd = {'success': False, 'message': 'Users credential not provided..!!'}
                    return HttpResponse(json.dumps(smd),  status=status.HTTP_400_BAD_REQUEST)
            else:
                smd = {'success': False, 'message': 'Users credential not provided..!!'}
                return HttpResponse(json.dumps(smd), status=status.HTTP_400_BAD_REQUEST)
    return wrapper
