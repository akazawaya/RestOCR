from rest_framework import serializers
from app_ocr.models import Document, Page, Content
from django.contrib.auth.models import User

# http -f POST http://localhost:8000/documents/ file@"/mnt/..." file_name=test file_type=0

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username']

class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    state_display = serializers.CharField(source="get_state_display", read_only=True)
    file_type_display = serializers.CharField(source="get_file_type_display", read_only=True)
    class Meta:
        model = Document
        fields = ['state', 'state_display', 'created', 'file', 'file_name', 'file_type', 'file_type_display', 'total_pages']

class PageSerializer(serializers.HyperlinkedModelSerializer):
    state_display = serializers.CharField(source="get_state_display", read_only=True)
    doc = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all())
    class Meta:
        model = Page
        fields = ['doc', 'image', 'state', 'state_display', 'page_number', 'width_px', 'height_px']

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    direction_display = serializers.CharField(source="get_direction_display", read_only=True)
    class Meta:
        model = Content
        fields = ['page', 'bbox', 'content', 'direction', 'direction_display', 'rec_score', 'det_score']