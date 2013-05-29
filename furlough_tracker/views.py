from django.shortcuts import render, render_to_response
from django import forms

from . import models

class CapabilityForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('name', 'phone')


def index(request):
    return render(request, 'index.html')

def person(request):
    return render(request, 'person.html')

def settings(request):
    context = {'form': CapabilityForm}
    return render_to_response('settings.html', context)

