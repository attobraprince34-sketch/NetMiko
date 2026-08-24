from django.contrib import messages
from django.shortcuts import render, redirect
from net.models import Equipements
from django.contrib.auth.decorators import login_required
from net.froms import SignUpForm, LoginForm
from django.contrib.auth import login, authenticate, logout
# Create your views here.
def index(request):
    return render(request, "index.html")


# la inscription
def inscription(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'compte crée avec succès. Bienvenue !')
            return redirect("dashboard")
        else :
            messages.error(request, 'veillez corriger les messages ci-dessous')
    else :
        form = SignUpForm()

    return render(request, 'auth/inscription.html', {'form':form})



# creation, connexion
def connection(request):
    if request.user.is_authenticated :
        return redirect('dashboard')
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid() :
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'content de te revoir {user.username}')
                return redirect("dashboard")
            else :
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrecte")
    else:
        form = LoginForm()
    return render(request, 'auth/connection.html', {'form':form})


# deconnection
def logout_user(request):
    logout(request)
    return redirect("/")

# creation du dashboard
@login_required 
def dahboard(request):
    equipements = Equipements.objects.filter(owner = request.user)

    context = {
        'equipements':equipements,
    }

    return render(request, 'service/dashboard.html', context)

# fonction cdes devices
@login_required
def device(request):
    return render(request, 'service/device.html')

#fonction interfaces
@login_required
def interface(request):
    return render(request, 'service/interface.html')

# fonction des alertes
@login_required
def alerte(request):
    return render(request, 'service/alerte.html')

# incidents 
@login_required
def incident(request):
    return render(request, 'service/incident.html') 

# rapports
@login_required
def rapport(request):
    return render(request, 'service/rapport.html')

# utilisateurs
@login_required
def user(request):
    return render(request, 'service/user.html')

# administration
@login_required
def admin(request):
    return render(request, 'service/admin.html')