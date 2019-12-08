import pdb
from .models import Notes
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .serializers import NoteSerializer, CreateNoteSerializer, UpdateNoteSerializer,SearchNoteSerializer
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from .decorators import user_login_required
from .documents import NoteDocument
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
import json


def get_user(token):
    jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
    new_token = str(token).split("Bearer ")[1]
    print("token ===== >>>>>>", new_token)
    encoded_token = jwt_decode_handler(new_token)
    print(encoded_token)
    username = encoded_token['username']
    print(username)
    user = User.objects.get(username=username)
    return user.id


@method_decorator(user_login_required, name='dispatch')
class NoteList(APIView):
    """
    API for CRUD(read and create) operations on note.
    jwt token based authentication
    """
    serializer_class = NoteSerializer
    parser_classes = FormParser, JSONParser, MultiPartParser

    def get(self, request):
        notes = Notes.objects.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        token = request.META['HTTP_AUTHORIZATION']
        user = get_user(token)
        request.data._mutable = True
        request.data['user'] = user
        data = request.data

        serializer = CreateNoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            smd = {'success': True, 'message': 'Note created successfully.'}
            return Response(smd, status=201)
        return Response(serializer.errors, status=400)


@method_decorator(user_login_required, name='dispatch')
class NoteDetails(GenericAPIView):
    """
    API for CRUD(update and delete) operations on note
    jwt token based authentication
    """
    serializer_class = UpdateNoteSerializer
    parser_classes = FormParser, JSONParser, MultiPartParser

    def get_object(self, pk):
        try:
            return Notes.objects.get(pk=pk)
        except Notes.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        note = self.get_object(pk)
        serializer = NoteSerializer(note)
        return Response(serializer.data, status.HTTP_200_OK)

    def put(self, request, pk):
        note = self.get_object(pk)
        serializer = UpdateNoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            note = Notes.objects.get(pk = pk)
            print('note --->',note)
            if note.is_archived == True:
                note.pinned = False
                note.save()
            smd = {'success': True, 'message': 'Note Updated successfully.'}
            return Response(smd, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        note = self.get_object(pk)
        note.delete()
        notes = Notes.objects.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchNote(APIView):
    """
    API for Search note on basis of title and description(using tokenizer).
    """
    def get(self, request):

        search_data = request.GET.get('search_data')
        if search_data:
            notes = NoteDocument.search().query("multi_match",query = search_data ,fields=["title", "description"])

        if  notes.count() == 0:
            smd = {'success': False, 'message': "No match found ..!!"}
            return HttpResponse(json.dumps(smd))

        print("total match found === >", notes.count())
        serializer = SearchNoteSerializer(notes, many=True)
        return Response(serializer.data, status=200)
