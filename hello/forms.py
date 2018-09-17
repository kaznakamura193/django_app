from django import forms
from.models import Friend

class FriendForm(forms.ModelForm):
    class Meta:
         model = Friend
         fields=['name','mail','gender','age','birthday']

class FindForm(forms.Form):
    find = forms.CharField(label='Find',required=False)

class CheckForm(forms.Form):
    empty = forms.CharField(label='Empty', empty_value=True)
    min = forms.CharField(label='Min', min_length=10)
    max = forms.CharField(label='Max', max_length=10)

