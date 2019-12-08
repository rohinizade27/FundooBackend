from .models import UserProfile
from django.contrib.auth.models import User
from rest_framework import serializers


# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='id')

    class Meta:
        model = User
        # fields = '__all__'
        fields = ['id','username', 'email', 'password']


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'password']


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id','image','user','s3_image_link']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id','image','user']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id','image']

