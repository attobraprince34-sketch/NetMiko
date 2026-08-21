from django.urls import path
from net.views import index, register, login, dahboard


urlpatterns = [
    path('', index , name='index.html'),
    path('connexion/', login, name='login'),
    path('inscription/', register, name='register'),
    path('dashboard/', dahboard, name='dashboard' )
]
