import json

from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django import forms
from django.template import RequestContext
from django.db.models import ProtectedError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from . import models


class CapabilityForm(forms.ModelForm):
    helper = FormHelper()
    helper.add_input(Submit('capability', 'Submit'))

    class Meta:
        model = models.Capability
        fields = ('name',)


class PersonCapabilityForm(forms.ModelForm):
    class Meta:
        model = models.PersonCapability
        widgets = {'person': forms.HiddenInput()}


class ColorInput(forms.TextInput):
    input_type = 'color'


class OfftimeTypeForm(forms.ModelForm):
    helper = FormHelper()
    helper.add_input(Submit('offtime', 'Submit'))

    class Meta:
        model = models.OfftimeType
        widgets = {'color': ColorInput()}


class PersonForm(forms.ModelForm):
    helper = FormHelper()
    helper.add_input(Submit('person', 'Submit'))

    class Meta:
        model = models.Person
        fields = 'first_name', 'last_name'


class OfftimeForm(forms.ModelForm):
    class Meta:
        model = models.Offtime
        fields = 'person', 'type', 'start_date', 'end_date', 'accepted'


class ColorInput(forms.TextInput):
    input_type = 'color'


def index(request):
    context = {
        'offtime_form': OfftimeForm(),
        'add_person_warning': not models.Person.objects.filter(deleted=False).count(),
        'add_type_warning': not models.OfftimeType.objects.count(),
    }
    return render(request, 'index.html', context,
                  context_instance=RequestContext(request))


def timeline_json(request):
    lst = []
    for cap in models.Capability.objects.all():
        lst.append(cap.name)
        for person in cap.persons():
            lst.append((person.name, list(person.offtimes())))
    untracked = False
    for person in models.Person.objects.filter(deleted=False):
        if not person.capabilities():
            if not untracked:
                lst.append('No capabilities')
                untracked = True
            lst.append((person.name, list(person.offtimes())))
    return HttpResponse(json.dumps(lst),
                               mimetype="application/json")


def person(request):
    form = PersonForm(request.POST or None)
    data = ((p, PersonCapabilityForm(initial={'person': p})) for p in
                                models.Person.objects.filter(deleted=False))
    context = {
        'active': 'person',
        'person_form': form,
        'persons': data,
        'capabilities': models.Capability.objects.all(),
    }
    if request.method == 'POST':
        if 'capability' in request.POST:
            form2 = PersonCapabilityForm(request.POST)
            if form2.is_valid():
                form2.save()
            return redirect('/person.html')
        else:
            if form.is_valid():
                form.save()
                return redirect('/person.html')
    return render(request, 'person.html', context,
                  context_instance=RequestContext(request))


def settings(request):
    context = {
        'capability_form': CapabilityForm(),
        'offtime_type_form': OfftimeTypeForm(),
        'offtime_types': models.OfftimeType.objects.all(),
        'capabilities': models.Capability.objects.all(),
    }

    if request.method == 'POST':
        if request.POST.get('offtime') is None:
            form = CapabilityForm(data=request.POST)
            context['capability_form'] = form
        else:
            form = OfftimeTypeForm(data=request.POST)
            context['offtime_type_form'] = form
        redirect('/settings.html')
        if form.is_valid():
            form.save()
            return redirect('/settings.html')

    return render_to_response('settings.html', context,
                              context_instance=RequestContext(request))


def change_api(request, origin, what, action, id):
    mapping = {
        'offtime_type': (models.OfftimeType, OfftimeTypeForm, 'Offtime Type'),
        'capability': (models.Capability, CapabilityForm, 'Capability'),
        'person': (models.Person, PersonForm, 'Person')
    }
    data = mapping[what][0].objects.get(pk=id)
    form = mapping[what][1](instance=data)
    delete_error = False
    if request.method == 'POST':
        if action == 'delete':
            if hasattr(data, 'deleted'):
                data.deleted = True
                data.save()
                return redirect(origin)
            else:
                try:
                    data.delete()
                    return redirect(origin)
                except ProtectedError:
                    delete_error = True
        else:
            form = mapping[what][1](request.POST, instance=data)
            if form.is_valid():
                form.save()
                return redirect(origin)

    context = {
        'name': mapping[what][2],
        'action': action,
        'data': data,
        'data_form': form,
        'delete_error': delete_error
    }
    return render_to_response('api.html', context,
                              context_instance=RequestContext(request))


def delete_person_capability(self, person_id, capability_id):
    models.PersonCapability.objects.filter(person__pk=person_id,
                                       capability__pk=capability_id).delete()
    return redirect('person')