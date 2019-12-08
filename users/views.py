import pdb
import os
import json
import boto3
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from .serializers import UserSerializer,FileSerializer,LoginSerializer,UserProfileUpdateSerializer,UserProfileSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.conf import settings
from .models import UserProfile
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class UserList(APIView):
    """
        API to create new user and read all users from database
    """
    serializer_class = UserSerializer
    parser_classes = FormParser,JSONParser,MultiPartParser

    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user,many=True)
        return Response(serializer.data,status=200)

    def post(self,request):
        data = request.data
        serializer = UserSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status = 201)
        return Response(serializer.errors,status = 400)


class UserDetails(APIView):
    """
    API to update,delete and read given note
    """
    serializer_class = UserSerializer
    parser_classes = FormParser,JSONParser,MultiPartParser

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self,request,pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_200_OK)


class UserRegistration(APIView):
    serializer_class = UserSerializer
    parser_classes = FormParser,JSONParser,MultiPartParser

    """
       This method is to register the new user
       :param request:take Http request(username,password1,password2,email)
       :return:HTTP response with message
    """
    def post(self,request):
        try:
            data = request.data
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                print("validations are done ----")
                username = serializer.data['username']
                email = serializer.data['email']
                password = serializer.data['password']
                print(username,email,password)
                print(User.objects.all())
                try:
                    if User.objects.get(email=email):
                        print("email exist ---")
                        return HttpResponse("User with same email already exist.")

                    if User.objects.get(username=username):
                        print("username exist ---")
                        return HttpResponse("User with same username already exist.")

                except User.DoesNotExist:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.is_active = False
                    user.save()
                current_site = get_current_site(request)
                print("----->",current_site)
                # import pdb
                # pdb.set_trace()
                print(type(urlsafe_base64_encode(force_bytes(user.pk))), user.pk)
                message = render_to_string('acc_active_email.html', {
                    'user': user, 'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':  account_activation_token.make_token(user),
                })
                mail_subject = 'Activate your account.'
                to_email = email
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
                smd = {'success': True, 'message': "Please confirm your email address to complete the registration" }
                return HttpResponse(json.dumps(smd), status=status.HTTP_200_OK)
        except Exception:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def activate(request, uidb64, token):
    """
    :param request: Http request
    :param uidb64: user's id encoded in base 64
    :param token: generated token for user
    :return: http response with text message
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and  account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        smd = {'success': True, 'message': "Thank you for your email confirmation . Now you can login your account."}
        return HttpResponse(json.dumps(smd), status=status.HTTP_200_OK)
    else:
        smd = {'success': False, 'message': "Activation link is invalid!"}
        return HttpResponse(json.dumps(smd), status=status.HTTP_400_BAD_REQUEST)


def get_jwt_token(user):
    """
    This method is to generate jwt token
    :param user: current logged in user
    :return: encoded jwt token
    """
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    print(payload)
    print(jwt_encode_handler(payload))
    return jwt_encode_handler(payload)


@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(APIView):
    serializer_class = LoginSerializer
    parser_classes = FormParser,JSONParser,MultiPartParser
    """
       This method allow authorised user to login
       :param request: Http request (with username and password)
       :return: response with jwt token
   """
    def post(self,request):
        try:
            data = request.data
            print(data)
            username = data['username']
            password = data['password']
            if username == "":
                return HttpResponse("please pass the username")
            if password == "":
                return HttpResponse("please pass the password")
            print(username, password)
            user = authenticate(username=username, password=password)
            print('usr', user, username, password)
            if user:
                if user.is_active:
                    # login(request, user)
                    jwt_token = get_jwt_token(user)
                    print(jwt_token)
                    cache.set('jwt_token', jwt_token)
                    print("token is fetched from redis cache :=======>>>",cache.get('jwt_token'))
                    smd = {'success': True, 'message':'login successfully','data':jwt_token}
                    return Response(smd, status=status.HTTP_200_OK)

                else:
                    smd = {'success': False, 'message':'Your account was inactive.'}
                    return Response(smd,status=status.HTTP_404_NOT_FOUND)
            else:
                smd = {'success': False, 'message': 'Invalid username and password.'}
                return HttpResponse(json.dumps(smd),status=status.HTTP_404_NOT_FOUND)
        except Exception:
            smd = {'success': False, 'message': 'Please ensure you are connected with redis server..'}
            return HttpResponse(json.dumps(smd), status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class ResetPassword(APIView):
    """
    This API is for reset password by using email verification
    """
    serializer_class = LoginSerializer

    def post(self,request):
        try:
            data = request.data
            print(data)
            password1 = data['password1']
            password2 = data['password2']
            email = data['email']

            if password1 is None:
                raise Exception("password1 is required")

            if password2 is None:
                raise Exception("password2 is required")

            if email is None:
                raise Exception("Email is required")
            validator = EmailValidator()
            try:
                validator(email)
            except ValidationError:
                raise Exception('You have entered invalid email-id ')
            associated_users = User.objects.filter(email=email)

            if associated_users.exists():
                for user in associated_users:
                    current_site = get_current_site(request)
                    message = render_to_string('password_reset_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                        'password1':urlsafe_base64_encode(force_bytes(password1)),
                        'password2':urlsafe_base64_encode(force_bytes(password2)),
                    })
                    mail_subject = 'Reset your Password.'
                    to_email = email
                    send_mail(mail_subject, message, "rohinizade43@gmailcom", [to_email], fail_silently=False)
                smd = {'success': True, 'message': 'An email has been sent to ' + to_email +'. Please check its inbox to continue reseting password.'}
                return Response(smd, status=status.HTTP_200_OK)
            else:
                smd = {'success': False, 'message':'No user is associated with this email address'}
                return Response(smd, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def password_reset_confirm(request, uidb64, password1, password2):
    password1 = str(urlsafe_base64_decode(password1))
    password2 = str(urlsafe_base64_decode(password2))
    if password1 != password2:
        raise Exception("password is not match")
    user = User.objects.get(pk=int(urlsafe_base64_decode(uidb64)))
    password = password1.split("'")[1]
    print('password -------->',password)
    user.set_password(password)
    user.save()
    login(request, user)
    smd = {'success': True, 'message': 'password reset successfully'}
    return Response(smd, status=status.HTTP_200_OK)


class FileUploadView(APIView):
    """
    This API is for read and create user profile ,upload image on aws s3 bucket
    """
    serializer_class = UserProfileSerializer

    def upload_file_s3(self,file):
        s3 = boto3.client('s3', aws_access_key_id = os.getenv('AWS_access_key_id'),
                          aws_secret_access_key = os.getenv('AWS_secret_access_key'),region_name="us-east-2")
        MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media/profile_pics')
        print("MEDIA_ROOT",MEDIA_ROOT)
        with open(os.path.join(MEDIA_ROOT, str(file)), 'rb') as f:
            b = bytearray(f.read())
            filename = str(file)
            bucket_name = os.getenv('bucket_name')
            new_filepath = filename.split('\\')[-1]
            link = "https://s3.us-east-2.amazonaws.com/{}/{}".format(bucket_name, new_filepath,)
            res = s3.put_object(Key=new_filepath, Bucket=bucket_name, Body=b)
            return link

    def get(self,request):
        user_profile = UserProfile.objects.all()
        serializer = FileSerializer(user_profile, many=True)
        return Response(serializer.data, status=200)

    def post(self,request):
        # pdb.set_trace()
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            file = request.data['image']
            user = request.data['user']
            user_obj = User.objects.get(id = int(user))
            s3_image_link = self.upload_file_s3(file)
            print("s3_image_link ------>>>",s3_image_link)
            profile_object = UserProfile.objects.get(user = user_obj)
            profile_object.s3_image_link = s3_image_link
            profile_object.save()
            smd = {'success': True, 'message': 'User Profile is created successfully.'}
            return Response(smd, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileUpdateView(APIView):
    """
       This API is for update and delete user profile ,upload image on aws s3 bucket
       """
    serializer_class = UserProfileUpdateSerializer

    def get_profile_object(self, pk):
        try:
            return UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise Http404

    def get(self,request,pk):
        user_profile = self.get_profile_object(pk)
        serializer = FileSerializer(user_profile)
        return Response(serializer.data)

    def put(self,request,pk):
        user_profile = self.get_profile_object(pk)
        serializer = UserProfileUpdateSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            file = request.data['image']
            f = FileUploadView()
            s3_image_link = f.upload_file_s3(file)
            print("s3_image_link ------>>>", s3_image_link)
            user_profile.s3_image_link = s3_image_link
            user_profile.save()
            smd = {'success': True, 'message': 'User Profile is updated successfully.'}
            return Response(smd, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request, pk):
        user_profile = self.get_profile_object(pk)
        user_profile.delete()
        return Response(status=status.HTTP_200_OK)


from django.shortcuts import render
def social_login(request):
    return render(request, 'sociall_login.html')






