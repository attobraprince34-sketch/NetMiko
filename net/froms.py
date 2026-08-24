# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


# ============================================================
# Classes Tailwind communes pour les champs
# ============================================================

INPUT_CLASSES = (
    "w-full px-4 py-3 rounded-xl border border-slate-200 bg-white "
    "text-slate-900 placeholder-slate-400 "
    "focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent "
    "transition"
)


# ============================================================
# FORMULAIRE D'INSCRIPTION
# ============================================================

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Prénom",
        }),
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Nom",
        }),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "adresse@email.com",
        }),
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Nom d'utilisateur",
        }),
    )

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "••••••••",
        }),
    )

    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "••••••••",
        }),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cette adresse e-mail.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


# ============================================================
# FORMULAIRE DE CONNEXION
# ============================================================

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Nom d'utilisateur",
            "autofocus": True,
        }),
    )

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "••••••••",
        }),
    )

    error_messages = {
        "invalid_login": "Nom d'utilisateur ou mot de passe incorrect.",
        "inactive": "Ce compte est désactivé.",
    }