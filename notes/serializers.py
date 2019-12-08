from .models import Notes
from rest_framework import serializers


# Serializers define the API representation.
class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['id','title', 'description', 'is_archived', 'pinned', 'image', 'color', 'trash', 'collaborate',
                  'remainder','created_time','user']


class CreateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title','description','is_archived','pinned','image','color','trash','collaborate','remainder','user']


class UpdateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'


class SearchNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title','description']




