from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import TrainingNote, CircuitTraining, EventReaction, ContentPage, ContentBlock

User = get_user_model()


class TrainingNoteForm(forms.ModelForm):
    class Meta:
        model = TrainingNote
        fields = ['date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }


class CircuitTrainingForm(forms.ModelForm):
    is_public = forms.BooleanField(
        required=False,
        initial=False,
        label="Zveřejnit",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = CircuitTraining
        fields = ['name', 'description', 'exercises', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'exercises': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }


class EventReactionForm(forms.ModelForm):
    class Meta:
        model = EventReaction
        fields = ['will_attend', 'comment']
        widgets = {
            'will_attend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    registration_password = forms.CharField(
        max_length=100,
        required=True,
        label="Zadejte registrační kód poskytnutý administrátorem",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_registration_password(self):
        from decouple import config
        registration_password = self.cleaned_data.get('registration_password')
        expected_password = config('REGISTRATION_PASSWORD', default='')
        
        if not expected_password:
            raise forms.ValidationError('Registrace není momentálně povolena. Kontaktujte administrátora.')
        
        if registration_password != expected_password:
            raise forms.ValidationError('Neplatný registrační kód.')
        
        return registration_password
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # auth_user.first_name/last_name are NOT NULL in DB; UserCreationForm may leave them unset/NULL.
        user.first_name = ""
        user.last_name = ""
        if commit:
            user.save()
        return user


class ProfileMatchingForm(forms.Form):
    profile_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ContentPageForm(forms.ModelForm):
    class Meta:
        model = ContentPage
        fields = [
            "section",
            "slug",
            "title",
            "intro",
            "is_published",
            "show_in_nav",
            "nav_order",
            "nav_icon",
        ]
        widgets = {
            "section": forms.Select(attrs={"class": "form-select"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "intro": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_in_nav": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "nav_order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "nav_icon": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip().lower()
        if not slug:
            raise ValidationError("Slug je povinný.")
        return slug

    def clean(self):
        cleaned = super().clean()
        section = cleaned.get("section")
        slug = cleaned.get("slug")
        if section and slug:
            qs = ContentPage.objects.filter(section=section, slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Stránka s tímto slugem v této sekci už existuje.")
        return cleaned


class ContentPageCreateForm(forms.ModelForm):
    class Meta:
        model = ContentPage
        fields = [
            "section",
            "slug",
            "title",
            "intro",
            "is_published",
            "show_in_nav",
            "nav_order",
            "nav_icon",
        ]
        widgets = {
            "section": forms.Select(attrs={"class": "form-select"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "intro": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_in_nav": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "nav_order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "nav_icon": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip().lower()
        if not slug:
            raise ValidationError("Slug je povinný.")
        return slug

    def clean(self):
        cleaned = super().clean()
        section = cleaned.get("section")
        slug = cleaned.get("slug")
        if section and slug and ContentPage.objects.filter(section=section, slug=slug).exists():
            raise ValidationError("Stránka s tímto slugem v této sekci už existuje.")
        return cleaned


class ContentBlockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["block_type"].widget = forms.HiddenInput()
        if not self.initial.get("block_type"):
            self.initial["block_type"] = ContentBlock.BlockType.TEXT
        self.fields["block_type"].initial = self.initial.get("block_type", ContentBlock.BlockType.TEXT)

    class Meta:
        model = ContentBlock
        fields = [
            "position",
            "title",
            "layout",
            "block_type",
            "body",
            "image_url",
            "image_alt",
            "link_url",
            "link_text",
            "is_visible",
        ]
        widgets = {
            "position": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "block_type": forms.HiddenInput(),
            "layout": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
            "image_url": forms.URLInput(attrs={"class": "form-control"}),
            "image_alt": forms.TextInput(attrs={"class": "form-control"}),
            "link_url": forms.URLInput(attrs={"class": "form-control"}),
            "link_text": forms.TextInput(attrs={"class": "form-control"}),
            "is_visible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

