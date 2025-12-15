import sys
from io import BytesIO
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator
from django.db import models
from app.rooms.models import RoomModel


def validate_image_size(image):
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError(
            f'La taille de l\'image ne doit pas dépasser 5MB. Taille actuelle : {image.size / (1024 * 1024):.2f}MB')


def room_photo_path(instance, filename):
    return f'room_photos/chambre-{instance.room.id}/photo_{filename}'


def room_thumbnail_path(instance, filename):
    return f'room_photos/chambre-{instance.room.id}/thumbnails/thumb_{filename}'


class Photo(models.Model):
    room = models.ForeignKey(RoomModel,on_delete=models.CASCADE,related_name='photos')
    file = models.ImageField(upload_to=room_photo_path,validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),  validate_image_size],help_text='Formats acceptés : JPG, PNG, WebP. Taille max : 5MB')
    thumbnail = models.ImageField(upload_to=room_thumbnail_path,blank=True,null=True,editable=False,verbose_name='Miniature')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Ordre d\'affichage')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

    def __str__(self):
        return f"Photo {self.id} - {self.room.name}"

    def save(self, *args, **kwargs):
        if self.file:
            img = Image.open(self.file)

            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            max_width = 1920
            max_height = 1080

            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            filename = self.file.name.split('/')[-1]
            if not filename.lower().endswith('.jpg'):
                filename = filename.rsplit('.', 1)[0] + '.jpg'

            self.file = InMemoryUploadedFile(
                output,
                'ImageField',
                filename,
                'image/jpeg',
                sys.getsizeof(output),
                None
            )

            img_for_thumb = Image.open(self.file)

            thumb_size = (300, 300)
            img_for_thumb.thumbnail(thumb_size, Image.Resampling.LANCZOS)

            thumb_output = BytesIO()
            img_for_thumb.save(thumb_output, format='JPEG', quality=80, optimize=True)
            thumb_output.seek(0)

            thumb_filename = f"thumb_{filename}"

            self.thumbnail = InMemoryUploadedFile(
                thumb_output,
                'ImageField',
                thumb_filename,
                'image/jpeg',
                sys.getsizeof(thumb_output),
                None
            )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete(save=False)

        if self.thumbnail:
            self.thumbnail.delete(save=False)

        super().delete(*args, **kwargs)