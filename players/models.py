from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _
# from location_field.models.plain import PlainLocationField

class CategoryChoices(models.TextChoices):
    pass

class Player(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name=_('nombre'),
                            error_messages={
                                'unique': 'A file with that name already exists.'
                            })

    status = models.BooleanField(default=True,
                                 verbose_name=_('estado'))

    start_time = models.DateField(auto_now_add=True,
                                  editable=False,
                                  verbose_name=_('hora de inicio'))

    last_update = models.DateTimeField(auto_now=True,
                                       editable=False,
                                       verbose_name=_('última actualización'))

    category = models.CharField(max_length=50,
                                blank=True,
                                verbose_name=_('categoria'))

    # location = PlainLocationField(based_fields=['city'], zoom=7)

    long = models.DecimalField(max_digits=9, decimal_places=6,
                               verbose_name=_('longitud'))

    lat = models.DecimalField(max_digits=9, decimal_places=6,
                              verbose_name=_('latitud'))

    def __str__(self):
        return f'{self.name},status:CONNECTED' if self.status == True else f'{self.name}, status:DISCONNECTED'


    class Meta:
        ordering = ('name', 'last_update',)
        verbose_name = _('infobox player')
        verbose_name_plural = _('infobox players')