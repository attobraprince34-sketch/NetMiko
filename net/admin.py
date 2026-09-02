from django.contrib import admin
from net.models import Equipements
# Register your models here.

@admin.register(Equipements)
class EquipementAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'name',
        'ip',
        'image' ,
        'type' ,
        'fabriquant' ,
        'modele',
        'localisation',
        'snmp',
        'snmp_port' ,
        'snmp_version' ,
        'uptime',
       'statut',
        'cpu' ,
       'memoire',
        'temperature',
        'latence',
        'created_at',
    )

    ordering = ('-created_at',)

admin.site.site_header = "NetMonitor Admin"
admin.site.site_title = 'NetMonitor'
admin.site.index_title = "tableau de bord"
