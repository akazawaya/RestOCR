from django.contrib.auth.models import User
from app_ocr.models import Document, Page, Content

from rest_framework.decorators import api_view
from rest_framework.response import Response


from app_ocr.serializers import UserSerializer, DocumentSerializer, PageSerializer, ContentSerializer

#from app_ocr.permissions import IsOwnerOrReadOnly
from rest_framework.reverse import reverse

from rest_framework import permissions
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework import viewsets

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
