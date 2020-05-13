from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    def clean(self):
        self.email = self.cleaned_data.get('email')
        if User.objects.filter(email=self.email).exists():
            self.add_error('email',"Email exists")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    