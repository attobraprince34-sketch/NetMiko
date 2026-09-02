from datetime import timedelta
import random
import pandas as pd
from io import StringIO
from weasyprint import HTML
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpResponse
from bs4 import BeautifulSoup
from django.template.loader import render_to_string
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render, redirect
from net.forms import EquipementForm
from net.models import Equipements
from django.contrib.auth.decorators import login_required
from net.froms import SignUpForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404
from .alerte import Alerte
# Create your views here.

def get_fragment_html(request, contexte, template_name, element_id):
    html_complet = render_to_string(template_name, contexte, request=request)
    soup = BeautifulSoup(html_complet, "html.parser")
    fragment = soup.find(id=element_id)
    if fragment is None:
        raise ValueError(f"Élément #{element_id} introuvable dans {template_name}")
    return str(fragment)



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

    equipement_inactifs =0
    equipement_actifs = 0

    if request.method=="GET":
        for e in equipements :
            if e.statut:
                equipement_actifs += 1
            else :
                equipement_inactifs += 1 

        
        nbr_appareils = equipements.count()
        alerte = Alerte(equipements)
        if nbr_appareils > 0 :
            pourcentage_actif = (equipement_actifs/nbr_appareils)*100
            pourcentage_inactif = (equipement_inactifs / nbr_appareils)* 100

        else :
            pourcentage_actif = 0
            pourcentage_inactif = 0

        paginator = Paginator(equipements, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        

            
        context = {
            "equipement_inactif":equipement_inactifs,
            "equipement_actif": equipement_actifs,
            "nbr_appareils":nbr_appareils,
            "alerte":alerte,
            "pourcentage_actif": pourcentage_actif,
            "pourcentage_inactif" : pourcentage_inactif,
            "equipements":page_obj,

        }

    return render(request, 'service/dashboard.html', context)


@login_required
def appareils_actifs(request):
    appareils_actifs = Equipements.objects.filter(statut=True, owner=request.user)
    q = request.GET.get("q", '').strip()
    if q:
        appareils_actifs = appareils_actifs.filter(name__icontains=q)
    paginator = Paginator(appareils_actifs, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    context = {
        "appareils":page_obj,
        "page_obj":page_obj,
    }
    return render(request, 'service/appareils_actifs.html', context)



@login_required
def appareils_inactifs(request):
    appareils_inactifs = Equipements.objects.filter(statut=False, owner=request.user)
    q = request.GET.get("q", '').strip()
    if q:
        appareils_inactifs = appareils_inactifs.filter(name__icontains=q)
    paginator = Paginator(appareils_inactifs, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    context = {
        "appareils":page_obj,
        "page_obj":page_obj,
    }
    return render(request, 'service/appareils_inactifs.html', context)



@login_required
def alerte(request):
    alerte = Equipements.objects.filter(cpu__gte=80, owner=request.user)


    q = request.GET.get("q", '').strip()


    if q:
        alerte = alerte.filter(name__icontains=q)

    paginator = Paginator(alerte, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)


    context = {"alerte": page_obj, "page_obj": page_obj}
    return render(request, 'service/alerte.html', context)



#fonction interfaces
@login_required
def interface(request):

    equipements = Equipements.objects.filter(owner=request.user).order_by('name')

    total = equipements.count()
    up = equipements.filter(statut=True).count()
    down = total - up

    context = {
        'equipements': equipements,
        'total': total,
        'up': up,
        'down': down,
    }
    return render(request, 'service/interface.html', context)

# fonction des alertes



# rapports
@login_required
def rapport(request):
    equipements = Equipements.objects.filter(owner=request.user)

    total = equipements.count()
    actifs = equipements.filter(statut=True).count()
    inactifs = total - actifs

    # Répartitions
    par_type = list(
        equipements.values('type').annotate(total=Count('id')).order_by('-total')
    )
    par_localisation = list(
        equipements.values('localisation').annotate(total=Count('id')).order_by('-total')
    )
    par_fabriquant = list(
        equipements.values('fabriquant').annotate(total=Count('id')).order_by('-total')
    )

    # Moyennes (santé du parc)
    moyennes = equipements.aggregate(
        cpu_moyen=Avg('cpu'),
        memoire_moyenne=Avg('memoire'),
        temperature_moyenne=Avg('temperature'),
        latence_moyenne=Avg('latence'),
    )

    # Points d'attention
    sans_snmp = equipements.filter(Q(snmp='') | Q(snmp__isnull=True)).count()
    inactifs_liste = equipements.filter(statut=False).order_by('-created_at')[:10]
    recents = equipements.order_by('-created_at')[:5]

    # Données formatées pour Chart.js (labels / data séparés)
    chart_statut = {
        'labels': ['Actifs', 'Inactifs'],
        'data': [actifs, inactifs],
    }
    chart_type = {
        'labels': [item['type'] for item in par_type],
        'data': [item['total'] for item in par_type],
    }
    chart_localisation = {
        'labels': [item['localisation'] for item in par_localisation],
        'data': [item['total'] for item in par_localisation],
    }

    context = {
        'total': total,
        'actifs': actifs,
        'inactifs': inactifs,
        'pourcentage_actifs': round((actifs / total * 100), 1) if total else 0,
        'par_type': par_type,
        'par_localisation': par_localisation,
        'par_fabriquant': par_fabriquant,
        'moyennes': moyennes,
        'sans_snmp': sans_snmp,
        'inactifs_liste': inactifs_liste,
        'recents': recents,
        'chart_statut': chart_statut,
        'chart_type': chart_type,
        'chart_localisation': chart_localisation,
    }
    return render(request, 'service/rapport.html', context)

# utilisateurs
@login_required
def user(request):

    equipements = Equipements.objects.filter(owner=request.user)

    total = equipements.count()
    actifs = equipements.filter(statut=True).count()
    inactifs = total - actifs

    context = {
        'total': total,
        'actifs': actifs,
        'inactifs': inactifs,
        'derniers_equipements': equipements.order_by('-created_at')[:5],
    }
    return render(request, 'service/user.html', context)






def get_equipements_filtres(request):
    """Centralise la logique de filtrage, réutilisée par voir() et les exports."""
    equipements = Equipements.objects.filter(owner=request.user)
    q = request.GET.get("q", '').strip()
    if q:
        equipements = equipements.filter(name__icontains=q)
    return equipements

@login_required
def voir(request):
    equipements = get_equipements_filtres(request)

    paginator = Paginator(equipements, 10)  # 10 équipements par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "equipements": page_obj,  # on passe page_obj au template, pas le queryset complet
        "page_obj": page_obj,
    }
    return render(request, 'service/voir.html', context)


@login_required
def export_equipements_excel(request):
    equipements = get_equipements_filtres(request)

    data = list(equipements.values(
        "name", "ip", "localisation", "type", "modele", "statut"
    ))
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["name", "ip", "localisation", "type", "modele", "statut"])

    df = df.rename(columns={
        "name": "Nom",
        "ip": "Adresse IP",
        "localisation": "Localisation",
        "type": "Type",
        "modele": "Modèle",
        "statut": "Statut",
    })
    df["Statut"] = df["Statut"].apply(lambda x: "Actif" if x else "Inactif")

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="equipements.xlsx"'
    df.to_excel(response, index=False, engine="openpyxl")
    return response





@login_required
def export_equipements_pdf(request):
    equipements = get_equipements_filtres(request)
    context = {"equipements": equipements}

    html_complet = render_to_string("service/voir.html", context, request=request)
    soup = BeautifulSoup(html_complet, "html.parser")

    table = soup.find("table")
    if table is None:
        return HttpResponse("Aucune donnée à exporter.", status=400)

    # Retirer la colonne "Actions" (dernière colonne) : en-tête + chaque ligne
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if cells:
            cells[-1].decompose()

    html_pour_pdf = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 12px; }}
        h2 {{ color: #16a34a; margin-bottom: 12px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 6px; text-align: left; }}
        th {{ background-color: #f3f4f6; text-transform: uppercase; font-size: 10px; }}
        img {{ width: 40px; height: auto; }}
    </style>
    </head>
    <body>
        <h2>Liste des équipements</h2>
        {str(table)}
    </body>
    </html>
    """

    pdf_file = HTML(
        string=html_pour_pdf,
        base_url=request.build_absolute_uri("/")
    ).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="equipements.pdf"'
    return response

@require_POST
@login_required
def delete(request, id):
    equipement = get_object_or_404(Equipements, id=id)
    equipement.delete()
    return redirect("dashboard")


SEUIL_CPU = 85
SEUIL_MEMOIRE = 85
SEUIL_TEMPERATURE = 70
SEUIL_LATENCE = 100
def detecter_incidents(equipements):
    """Génère une liste d'incidents à partir des métriques de chaque équipement."""
    incidents = []

    for e in equipements:
        if not e.statut:
            incidents.append({
                'equipement': e,
                'type': 'Hors ligne',
                'gravite': 'critique',
                'detail': "L'équipement est signalé comme inactif.",
            })
        if e.cpu >= SEUIL_CPU:
            incidents.append({
                'equipement': e,
                'type': 'CPU élevé',
                'gravite': 'critique' if e.cpu >= 95 else 'avertissement',
                'detail': f"Utilisation CPU à {e.cpu}%.",
            })
        if e.memoire >= SEUIL_MEMOIRE:
            incidents.append({
                'equipement': e,
                'type': 'Mémoire élevée',
                'gravite': 'critique' if e.memoire >= 95 else 'avertissement',
                'detail': f"Utilisation mémoire à {e.memoire}%.",
            })
        if e.temperature >= SEUIL_TEMPERATURE:
            incidents.append({
                'equipement': e,
                'type': 'Température élevée',
                'gravite': 'critique' if e.temperature >= 85 else 'avertissement',
                'detail': f"Température à {e.temperature}°C.",
            })
        if e.latence >= SEUIL_LATENCE:
            incidents.append({
                'equipement': e,
                'type': 'Latence élevée',
                'gravite': 'avertissement',
                'detail': f"Latence à {e.latence} ms.",
            })

    # Tri : critiques d'abord
    ordre_gravite = {'critique': 0, 'avertissement': 1}
    incidents.sort(key=lambda i: ordre_gravite.get(i['gravite'], 2))
    return incidents

@login_required
def incident(request):
    equipements = Equipements.objects.filter(owner=request.user)
    liste_incidents = detecter_incidents(equipements)

    nb_critiques = sum(1 for i in liste_incidents if i['gravite'] == 'critique')
    nb_avertissements = sum(1 for i in liste_incidents if i['gravite'] == 'avertissement')

    # Filtre optionnel via ?gravite=critique
    filtre_gravite = request.GET.get('gravite')
    if filtre_gravite in ('critique', 'avertissement'):
        liste_incidents = [i for i in liste_incidents if i['gravite'] == filtre_gravite]

    context = {
        'incidents': liste_incidents,
        'nb_total': nb_critiques + nb_avertissements,
        'nb_critiques': nb_critiques,
        'nb_avertissements': nb_avertissements,
        'filtre_gravite': filtre_gravite,
    }
    return render(request, 'service/incident.html', context)

def detail_equipement(request, id):
    equipement = get_object_or_404(Equipements, id=id, owner=request.user)
    context = {
        'e': equipement,
    }
    return render(request, 'service/detail_equipement.html', context)


@login_required
def form_equipement(request, id=None):
    equipement = get_object_or_404(Equipements, id=id, owner=request.user) if id else None

    if request.method == "POST":
        form = EquipementForm(request.POST, instance=equipement, owner=request.user)
        if form.is_valid():
            e = form.save()
            return redirect("detail_equipement", id=e.id)
    else:
        form = EquipementForm(instance=equipement, owner=request.user)

    context = {
        "form": form,
        "equipement": equipement,
    }
    return render(request, "service/form_equipement.html", context)