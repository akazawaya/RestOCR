from django.contrib.auth.models import User
from app_ocr.models import FileType, Direction, Document, Page, Content

from rest_framework.response import Response

from django.core.files.base import ContentFile
from app_ocr.serializers import UserSerializer, DocumentSerializer, PageSerializer, ContentSerializer

#from app_ocr.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from app_ocr.etc.tools import validate_and_analyze
from app_ocr.etc.e_yomitoku import test_ocr

from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from pathlib import Path

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
                    img_file = ContentFile(img, name=f"{p}.png")
                    page = PageSerializer(data={"doc":doc.instance.pk, "image":img_file, "page_number":total_pages})
                    if page.is_valid(raise_exception=True):
                        page.save()
                        # 全体のdirはPath(page.instance.image.name).parent.as_posix()でアクセス可能
                        page_paths = page.instance.image.name
                        # breakpoint() 
                        content_ = test_ocr(page_paths)
                        for w in content_:
                            ct = ContentSerializer(data={"page":page.instance.pk, "bbox":w["points"], "content":w["content"], "direction":Direction.label_to_value(w["direction"]), "rec_score":w["rec_score"], "det_score":w["det_score"]})
                            if ct.is_valid(raise_exception=True):
                                ct.save()
            return Response({"document": doc.data}, status=status.HTTP_201_CREATED)
                        
        
class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
