from django.contrib.auth.models import User
from app_ocr.models import FileType, Document, Page, Content

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.core.files.base import ContentFile
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
from django.db import transaction
"""
http -f POST http://127.0.0.1:8000/documents/analyze/ file@/mnt/q/N-106.pdf
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
        with transaction.atomic():
            file = request.FILES.get('file')   
            images, ext_label, total_pages = validate_and_analyze(file)
            doc = DocumentSerializer(data={"file":file, "file_name":file.name, "file_type":FileType.label_to_value(ext_label), "total_pages":total_pages})
            if doc.is_valid(raise_exception=True):
                doc.save() #　modelインスタンスでないとidを受取れない　doc.instanceでモデルにアクセス可能
                for p, img in enumerate(images):
                    img_file = ContentFile(img, name=f"{file}_{p}.png")
                    page = PageSerializer(data={"doc":doc.instance.pk, "image":img_file, "page_number":total_pages})
                    if page.is_valid(raise_exception=True):
                        page.save()
            return Response({"document": doc.data}, status=status.HTTP_201_CREATED)
                        
        
class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
