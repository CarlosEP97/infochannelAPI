from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
# from multiselectfield import MultiSelectField
from users.models import User
from resources.models import Resource
from .managers import CampaignsManager, TimelinesManager,PlaylistManager
# from .validators import array_repit_items
from django.db.models.signals import post_save, pre_save
from django.db.models import Count
from django.dispatch import receiver
from datetime import timedelta
import datetime

HORIZONTAL = 10
VERTICAL = 20

ORIENTATION = (
    (HORIZONTAL, _('Horizontal')),
    (VERTICAL, _('Vertical')),
)

BOOL_CHOICES = ((True, 'Programado'), (False, 'Secuencial'))


class Campaigns(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    campaign_name = models.CharField(max_length=100, unique=True,
                                     verbose_name=_('nombre de la campaña'),
                                     error_messages={
                                         'unique': 'A file with that name already exists.'
                                     })

    screen_orientation = models.SmallIntegerField(
                                                  choices=ORIENTATION,
                                                  verbose_name=_('Horientacion de la pantalla'))

    width = models.SmallIntegerField(default=0,
                                     verbose_name=_('Ancho'),
                                     help_text='resolucion de pantalla ancho')

    height = models.SmallIntegerField(default=0,
                                      verbose_name=_('Alto'),
                                      help_text='resolucion de pantalla alto')


    playback_mode = models.BooleanField(max_length=12,
                                        choices=BOOL_CHOICES,
                                        default=False,
                                        verbose_name=_('Modo de reproducción'))

    created_date = models.DateField(auto_now_add=True,
                                   editable=False,
                                   verbose_name=_('Fecha de creado'))

    last_update = models.DateField(auto_now=True,
                                   editable=False,
                                   verbose_name=_('última actualización'))

    objects = CampaignsManager()

    def __str__(self):
        return f'{self.user} create campaign {self.campaign_name}' \
               f' with resolution {self.width} x {self.height},screen orientation {self.screen_orientation} ' \
               f' and playback mode {self.playback_mode}'
    class Meta:
        ordering = ('campaign_name',)
        verbose_name = _('Campaña')
        verbose_name_plural = _('Campañas')


@receiver(post_save, sender=Campaigns)
def campaign_timelines_playlist_set(sender, instance, created, *args, **kwargs):
    if created:
        t = Timelines.objects.create(campaign=instance)
        Playlist.objects.create(timelines=t, width=instance.width, height=instance.height)



MONDAY = 10
TUESDAY = 20
WEDNESDAY = 30
THURSDAY = 40
FRIDAY = 50
SATURDAY = 60
SUNDAY = 70

DAYS = (
    (MONDAY, _('Lunes')),
    (TUESDAY, _('Martes')),
    (WEDNESDAY, _('Miercoles')),
    (THURSDAY, _('Jueves')),
    (FRIDAY, _('Viernes')),
    (SATURDAY, _('Sabado')),
    (SUNDAY, _('Domingo')),
)


def get_default_days():
    return [10, 20, 30, 40, 50, 60, 70]

def get_today():
    return timezone.make_aware(datetime.datetime.now())

def get_tomorrow():
    return timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=1))



DAILY = 10
WEEKLY = 20
ONCE = 30

MODES = ((DAILY,_('Diariamente')),
         (WEEKLY,_('Semanalmente')),
         (ONCE,_('Una vez')),
)


class Timelines(models.Model):

    campaign = models.ForeignKey(Campaigns,on_delete=models.CASCADE)

    timeline_name = models.CharField(max_length=100, default='default',
                                     verbose_name=_('nombre del timeline'))

    date_start = models.DateTimeField(auto_now=False,
                                      default=get_today,
                                      verbose_name=_('Fecha de inicio')
                                      )

    date_end = models.DateTimeField(auto_now=False,
                                    default=get_tomorrow,
                                    verbose_name=_('fecha de finalización'))

    position = models.PositiveIntegerField(default=0,
                                           help_text='posición en la cola')

    # day_options =MultiSelectField(choices=DAYS,max_choices=7,default=1,max_length=20)

    play_options = models.SmallIntegerField(choices=MODES,default=DAILY,blank=True)

    day_options = ArrayField(models.SmallIntegerField(choices=DAYS),
                             default=get_default_days, size=7)

    objects = TimelinesManager()


    def __str__(self):
        return f'create timeline {self.timeline_name} with date start {self.date_start} and date end {self.date_end}' \
               f' play option {self.play_options} and day options {self.day_options}'

    class Meta:
        ordering = ('position',)
        verbose_name = _('Linea de tiempo')
        verbose_name_plural = _('Lineas de tiempo')



class Playlist(models.Model):

    # user = models.ForeignKey(User, on_delete=models.CASCADE)

    timelines = models.ForeignKey(Timelines,on_delete=models.CASCADE)

    name = models.CharField(max_length=100,
                            verbose_name=_('nombre'),
                            default='default'
                            )

    top = models.SmallIntegerField(default=0,
                                   verbose_name=_('Arriba'),
                                   help_text='posicion en px')

    left = models.SmallIntegerField(default=0,
                                    verbose_name=_('Izquierda'),
                                    help_text='posicion en px')

    width = models.SmallIntegerField(default=0,
                                     verbose_name=_('Ancho'),
                                     help_text='ancho en px')

    height = models.SmallIntegerField(default=0,
                                      verbose_name=_('Alto'),
                                      help_text='alto en px')

    z_index = models.SmallIntegerField(default=0,
                                       help_text=_('orden de un elemento posicionado')
                                       )

    resources = models.ManyToManyField(Resource,
                                       through='AddFiles',
                                       through_fields=('playlist', 'resource'))

    created_at = models.DateField(auto_now_add=True,
                                  editable=False,
                                  verbose_name=_('fecha de creación'))

    last_update = models.DateField(auto_now=True,
                                   editable=False,
                                   verbose_name=_('última actualización'))

    random_order = models.BooleanField(default=False,
                                       verbose_name=_('aleatorio'),)

    objects = PlaylistManager()

    def __str__(self):
        return f'title {self.name}' \
               f' layout with top {self.top}, left {self.left}, height {self.height} and width {self.width}'

    @property
    def count_resource(self):
        return self.resources.count()

    @property
    def ocurrence_files(self):
        return self.resources.all().annotate(count= Count('addfiles__resource')).order_by('-count')



    class Meta:
        ordering = ('name', 'last_update',)
        verbose_name = _('lista de reproducción')
        verbose_name_plural = _('listas de reproducción')




class AddFiles(models.Model):

    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

    position = models.PositiveIntegerField(
        default=0,
        help_text='posición en la cola')


    duration = models.DurationField(
        default=timedelta(seconds=10),
        verbose_name=_('duración'),
        help_text=' horas / minutos / segundos'
    )

    repeat_to_fit = models.BooleanField(default=False,
                                        verbose_name=_('repetir para encajar'),)


    def __str__(self):
        return f'{self.position}'

    class Meta:
        ordering = ('position',)
        verbose_name = _('agregar archivo a la cola')
        verbose_name_plural = _('agregar archivos')