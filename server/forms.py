from django import forms
from django.contrib.auth.models import User
from server.models import Move

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)
		self.fields['username'].help_text = ''

	class Meta:
		model = User
		fields = ('username', 'password')

class MoveForm(forms.ModelForm):
	origin = forms.IntegerField(initial=0)
	target = forms.IntegerField()

	class Meta:
		model = Move
		fields = ('origin', 'target')