from django import forms
from .models import Event, Category, Participant
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import RSVP

User = get_user_model()


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = '__all__'


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User  # ✅ Now points to CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class RSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['status', 'comment']
        widgets = {
            'status': forms.RadioSelect,
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'email']

class ParticipantUpdateForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['phone', 'address']