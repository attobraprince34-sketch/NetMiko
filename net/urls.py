from django.urls import path
from net.views import index,logout_user, connection, inscription, dahboard, interface, admin, user, incident, alerte, rapport, device


urlpatterns = [
    path('', index , name='index.html'),
    path('inscription/', inscription, name='inscription'),
    path('connection/', connection, name='connection'),
    path('logout/', logout_user, name='logout'),
    path('dashboard/', dahboard, name='dashboard' ),
    path('device/', device, name='device'),
    path('interface/', interface, name='interface'),
    path('alerte/', alerte, name='alerte'),
    path('incident/', incident, name='incident'),
    path('rapport/', rapport, name='rapport'),
    path('user/', user, name='user'),
    path('admin', admin, name='admin'),
]
