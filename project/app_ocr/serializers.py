from rest_framework import serializers
from app_ocr.models import Document, Page, Content
from django.contrib.auth.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'snippets']

class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Document
        fields = ['created', 'state', 'file', 'file_name', 'file_type', 'total_pages']

class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = ['doc', 'image', 'state', 'page_number', 'width_px', 'height_px']

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Content
        fields = ['page', 'bbox', 'content', 'direction', 'rec_score', 'det_score']