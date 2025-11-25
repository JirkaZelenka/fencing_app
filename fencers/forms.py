from django import forms
from .models import TrainingNote, CircuitTraining, EventReaction


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

