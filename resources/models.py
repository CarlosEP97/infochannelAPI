import os
from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import pre_save
from .validators import validate_file_extension
from .managers import ResourceManager



def resources_upload_handler(instance,filename):
    return f'{instance.user.first_name}/{filename}'


VIDEOS = 10
IMAGES = 20
SOUNDS = 30

MEDIA = (
    (VIDEOS, _('Videos')),
    (IMAGES, _('Imagenes')),
    (SOUNDS, _('Sonidos')),
)
class Resource(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100, unique=True,
                            verbose_name=_('nombre'),
                            error_messages={
                                'unique': 'A file with that name already exists.'
                            })

    files = models.FileField(upload_to=resources_upload_handler,
                             help_text=_('extensión del archivo'),
                             verbose_name=_('archivos'),
                             validators=[validate_file_extension])

    type_of_file = models.SmallIntegerField(choices=MEDIA,
                                    blank=True,
                                    verbose_name=_('tipo de archivo'), )

    upload_date = models.DateField(auto_now_add=True,
                                   editable= False,
                                   verbose_name=_('Fecha de subida'))

    objects = ResourceManager()


    def __str__(self):
        return f'{self.name}, {self.type_of_file}'

    def extension(self):
        name, extension = os.path.splitext(self.files.name)
        return extension

    class Meta:
        ordering = ('upload_date',)
        verbose_name = _('recurso')
        verbose_name_plural = _('recursos')


@receiver(pre_save, sender=Resource)
def Resources_type_set(sender, instance, *args, **kwargs):
    ext = os.path.splitext(instance.files.name)[1]
    valid_extensions = ['.mp3', '.mp4', '.svg', '.jpeg', '.jpg', '.png', '.gif']
    if ext in valid_extensions[0]:
        instance.type_of_file = SOUNDS
    if ext in valid_extensions[1:2]:
        instance.type_of_file = VIDEOS
    if ext in valid_extensions[2:7]:
        instance.type_of_file = IMAGES

