from django.urls import path
from net.views import *


urlpatterns = [
    path('', index , name='index.html'),
    path('inscription/', inscription, name='inscription'),
    path('connection/', connection, name='connection'),
    path('logout/', logout_user, name='logout'),
    path('dashboard/', dahboard, name='dashboard' ),
    path('interface/', interface, name='interface'),
    path('alerte/', alerte, name='alerte'),
    path('incident/', incident, name='incident'),
    path('rapport/', rapport, name='rapport'),
    path('user/', user, name='user'),
    path('dashboard/voir/', voir, name='voir'),
    path('equipements/export/excel/', export_equipements_excel, name='export_equipements_excel'),
    path('equipements/export/pdf/', export_equipements_pdf, name='export_equipements_pdf'),
    path('dashboard/appareils_actifs/', appareils_actifs, name='appareils_actifs'),
    path('dashboard/appareils_inactifs/', appareils_inactifs, name='appareils_inactifs'),
    path('delete/<uuid:id>/', delete, name='delete'),
    path("equipement/<uuid:id>/", detail_equipement, name="detail_equipement"),
    path("equipement/ajouter/", form_equipement, name="ajouter_equipement"),
    path("equipement/<uuid:id>/modifier/", form_equipement, name="modifier_equipement"),
]
