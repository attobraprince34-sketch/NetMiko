import re
from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError

from .models import Equipements

TYPE_CHOICES = [
    ('switch', 'Switch'),
    ('routeur', 'Routeur'),
    ('pare_feu', 'Pare-feu'),
    ('point_acces', "Point d'accès"),
    ('serveur', 'Serveur'),
    ('autre', 'Autre'),
]

FABRIQUANT_CHOICES = [
    ('cisco', 'Cisco'),
    ('huawei', 'Huawei'),
    ('hp_aruba', 'HP / Aruba'),
    ('juniper', 'Juniper'),
    ('tp_link', 'TP-Link'),
    ('autre', 'Autre'),
]

SNMP_VERSION_CHOICES = [
    ('v1', 'v1'),
    ('v2c', 'v2c'),
    ('v3', 'v3'),
]

IP_REGEX = re.compile(
    r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
)

CHAMP_CLASSES = (
    "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white "
    "focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
)


class EquipementForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={"class": CHAMP_CLASSES}),
    )
    fabriquant = forms.ChoiceField(
        choices=FABRIQUANT_CHOICES,
        widget=forms.Select(attrs={"class": CHAMP_CLASSES}),
    )
    snmp_version = forms.ChoiceField(
        choices=SNMP_VERSION_CHOICES,
        widget=forms.Select(attrs={"class": CHAMP_CLASSES}),
    )

    uptime_jours = forms.IntegerField(
        min_value=0, required=False, initial=0,
        widget=forms.NumberInput(attrs={"class": CHAMP_CLASSES, "placeholder": "Jours"}),
    )
    uptime_heures = forms.IntegerField(
        min_value=0, max_value=23, required=False, initial=0,
        widget=forms.NumberInput(attrs={"class": CHAMP_CLASSES, "placeholder": "Heures"}),
    )
    uptime_minutes = forms.IntegerField(
        min_value=0, max_value=59, required=False, initial=0,
        widget=forms.NumberInput(attrs={"class": CHAMP_CLASSES, "placeholder": "Minutes"}),
    )

    class Meta:
        model = Equipements
        fields = [
            "name", "type", "fabriquant", "modele", "localisation", "image",
            "ip", "statut", "snmp", "snmp_port", "snmp_version",
            "cpu", "memoire", "temperature", "latence",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": CHAMP_CLASSES, "placeholder": "Nom de l'équipement"}),
            "modele": forms.TextInput(attrs={"class": CHAMP_CLASSES}),
            "localisation": forms.TextInput(attrs={"class": CHAMP_CLASSES}),
            "image": forms.URLInput(attrs={"class": CHAMP_CLASSES, "placeholder": "https://..."}),
            "ip": forms.TextInput(attrs={"class": CHAMP_CLASSES, "placeholder": "192.168.1.1"}),
            "statut": forms.CheckboxInput(attrs={"class": "w-5 h-5 accent-green-500"}),
            "snmp": forms.TextInput(attrs={"class": CHAMP_CLASSES, "placeholder": "Community string"}),
            "snmp_port": forms.NumberInput(attrs={"class": CHAMP_CLASSES}),
            "cpu": forms.NumberInput(attrs={"class": CHAMP_CLASSES, "min": 0, "max": 100}),
            "memoire": forms.NumberInput(attrs={"class": CHAMP_CLASSES, "min": 0, "max": 100}),
            "temperature": forms.NumberInput(attrs={"class": CHAMP_CLASSES}),
            "latence": forms.NumberInput(attrs={"class": CHAMP_CLASSES, "min": 0}),
        }
        labels = {
            "name": "Nom",
            "modele": "Modèle",
            "localisation": "Localisation",
            "image": "Image (URL)",
            "ip": "Adresse IP",
            "statut": "Équipement actif",
            "snmp": "Community SNMP",
            "snmp_port": "Port SNMP",
            "cpu": "CPU (%)",
            "memoire": "Mémoire (%)",
            "temperature": "Température (°C)",
            "latence": "Latence (ms)",
        }

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)

        # Pré-remplissage de l'uptime en jours/heures/minutes lors d'une modification
        if self.instance and self.instance.pk and self.instance.uptime is not None:
            total_seconds = int(self.instance.uptime.total_seconds())
            self.fields["uptime_jours"].initial = total_seconds // 86400
            self.fields["uptime_heures"].initial = (total_seconds % 86400) // 3600
            self.fields["uptime_minutes"].initial = (total_seconds % 3600) // 60

        if not self.instance.pk:
            self.fields["snmp_port"].initial = 161

    def clean_ip(self):
        ip = self.cleaned_data["ip"].strip()
        if not IP_REGEX.match(ip):
            raise ValidationError("Adresse IP invalide (format attendu : 192.168.1.1).")
        qs = Equipements.objects.filter(ip=ip)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Cette adresse IP est déjà utilisée par un autre équipement.")
        return ip

    def clean_snmp_port(self):
        port = self.cleaned_data["snmp_port"]
        if not (1 <= port <= 65535):
            raise ValidationError("Le port doit être compris entre 1 et 65535.")
        return port

    def clean_cpu(self):
        cpu = self.cleaned_data["cpu"]
        if not (0 <= cpu <= 100):
            raise ValidationError("Le CPU doit être un pourcentage entre 0 et 100.")
        return cpu

    def clean_memoire(self):
        memoire = self.cleaned_data["memoire"]
        if not (0 <= memoire <= 100):
            raise ValidationError("La mémoire doit être un pourcentage entre 0 et 100.")
        return memoire

    def clean_temperature(self):
        temperature = self.cleaned_data["temperature"]
        if not (-40 <= temperature <= 150):
            raise ValidationError("Température hors limites réalistes (-40°C à 150°C).")
        return temperature

    def clean_latence(self):
        latence = self.cleaned_data["latence"]
        if latence < 0:
            raise ValidationError("La latence ne peut pas être négative.")
        return latence

    def clean(self):
        cleaned_data = super().clean()
        jours = cleaned_data.get("uptime_jours") or 0
        heures = cleaned_data.get("uptime_heures") or 0
        minutes = cleaned_data.get("uptime_minutes") or 0
        cleaned_data["uptime"] = timedelta(days=jours, hours=heures, minutes=minutes)
        return cleaned_data

    def save(self, commit=True):
        equipement = super().save(commit=False)
        equipement.uptime = self.cleaned_data["uptime"]
        if self.owner:
            equipement.owner = self.owner
        if commit:
            equipement.save()
        return equipement