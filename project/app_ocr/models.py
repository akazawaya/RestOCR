from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator,  FileExtensionValidator

class FileType(models.IntegerChoices):
    # name, value, label で各要素にアクセス可能
    JPG   = 1, "jpg"
    PNG   = 2, "png"
    BMP   = 3, "bmp"
    TIF   = 4, "tif" 
    PDF   = 5, "pdf"
    # label → valueは　cls(label).value　で変換できるが
    # その逆は関数を作成する必要がある
    @classmethod
    def label_to_value(cls, ext_label):
        for ext in cls:
            if ext.label == ext_label:
                return ext.value
    
class Direction(models.IntegerChoices):
    HORIZONTAL = 0, "横書き"
    VERTICAL   = 1, "縦書き"
    
class State(models.IntegerChoices):
    QUEUED     = 0, "待機中"
    PROCESSING = 1, "処理中"
    SUCCESS    = 2, "完了"
    FAILED     = 3, "失敗"

# Userモデルはdjango.contrib.auth.models
# から自動で作成される
class Document(models.Model):
    created = models.DateTimeField(auto_now_add=True) 
    state = models.PositiveSmallIntegerField(choices=State.choices, default=State.QUEUED)  
    file = models.FileField(upload_to="input/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "bmp", "tif", "pdf"])],
    )
    # FileField / ImageField は自動で日付ごとのサブディレクトリを作成する
    file_name = models.CharField(max_length=255)  
    file_type = models.PositiveSmallIntegerField(choices=FileType.choices)
    total_pages = models.PositiveSmallIntegerField(default=1)  
    class Meta:
        ordering = ['created']

class Page(models.Model):
    doc = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="page")
    image = models.ImageField(upload_to="input/img/", null=True, blank=True,
                              width_field="width_px", height_field="height_px") # 自動でwhを取得できるらしい
    state = models.PositiveSmallIntegerField(choices=State.choices, default=State.QUEUED)
    page_number = models.PositiveSmallIntegerField(default=1)
    width_px = models.PositiveIntegerField(null=True, blank=True)
    height_px = models.PositiveIntegerField(null=True, blank=True) 

class Content(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="content")
    bbox = models.JSONField(blank=True, null=True)
    content = models.TextField(blank=True, null=True) 
    direction = models.PositiveSmallIntegerField(choices=Direction.choices)
    rec_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    det_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])