from django import forms
from .models import Users


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = Users
        fields = ['nickname', 'username', 'password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['nickname'].widget.attrs['placeholder'] = 'Enter Your Nickname'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = Users
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = 'Enter username'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter password '
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'