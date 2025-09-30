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
from rest_framework import status
from app_ocr.etc.tools import validate_and_analyze
from rest_framework.parsers import MultiPartParser, FormParser

"""
http -f POST http://127.0.0.1:8000/documents/analyze/      file@"/Users/XXXXX.png" Accept:application/json
"""
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        file = request.FILES.get('file')   
        images, ext, total_pages = validate_and_analyze(file)
        doc = DocumentSerializer(data={"file":file, "file_name":file.name, "file_type":ext, "total_pages":total_pages})
        if doc.is_valid():
            doc.save()
            return Response(doc.data, status=status.HTTP_201_CREATED)
        
        return Response(doc.errors, status=status.HTTP_400_BAD_REQUEST)
class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
