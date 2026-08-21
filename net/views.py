from django.shortcuts import render, redirect
from net.models import Equipements
# Create your views here.
def index(request):
    return render(request, "index.html")


# la connecxion 
def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth/login.html')

# creation de de l'inscription
def register(request):
    if request.user.is_authenticated :
        return redirect('dashboard')
    return render(request, 'auth/register.html')

# creation du dashboard
def dahboard(request):
    equipements = Equipements.objects.filter(owner = request.user)

    context = {
        'equipements':equipements,
    }

    return render(request, 'service/dashboard.html', context)