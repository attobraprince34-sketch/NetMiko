import uuid

from django.db import models
from django.conf import settings

# Create your models here.
class Equipements(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mes_equipements',
    )
    name = models.CharField(max_length=300)
    ip = models.CharField(max_length=15, unique=True, blank=False)
    image = models.CharField(max_length=1000, blank=True)
    type = models.CharField(max_length=300)
    fabriquant = models.CharField(max_length=300)
    modele = models.CharField(max_length=300)
    localisation = models.CharField(max_length=300)
    snmp = models.CharField(max_length=300)
    snmp_port = models.IntegerField()
    snmp_version = models.CharField(max_length=300)
    uptime = models.DurationField(help_text='temps ecoulé depuis le dernier demarrage')
    statut = models.BooleanField(default=False)
    cpu = models.IntegerField()
    memoire = models.IntegerField()
    temperature = models.IntegerField()
    latence = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'equiment => {self.name} de {self.owner} '