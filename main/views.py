import json
from datetime import timedelta, datetime
from collections import OrderedDict

from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django import forms
from django.template import RequestContext
from django.db.models import ProtectedError
from django.forms.widgets import TextInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.decorators import login_required

from . import models


class DateWidget(TextInput):
    """Changes a datetime to a date"""
    def _format_value(self, value):
        if isinstance(value, datetime):
            value = value.date()
        return super(DateWidget, self)._format_value(value)


class EndDateWidget(TextInput):
    def _format_value(self, value):
        if isinstance(value, datetime):
            value = (value - timedelta(1)).date()
        return super(EndDateWidget, self)._format_value(value)


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
    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.fields["person"].queryset = \
                            models.Person.objects.filter(deleted=False)
        q = models.Offtime.objects.all()
        if self.instance.person_id is not None:
            q = q.filter(person__id=self.instance.person_id)
        if self.instance.id is not None:
            q = q.exclude(pk=self.instance.id)
        self.fields["parent_offtime"].queryset = q

    def clean(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")

        if end_date is not None:
            if end_date.hour == end_date.minute == end_date.second == 0:
                # just add another day, because that's what it means for users
                end_date += timedelta(1)
                self.cleaned_data["end_date"] = end_date
        if None not in (start_date, end_date) and end_date <= start_date:
            msg = u"End date should be greater than start date."
            self._errors["end_date"] = self.error_class([msg])
        if start_date and end_date:
            self._check_if_between_dates()
        return super(type(self), self).clean()

    def _check_if_between_dates(self):
        parent_offtime = self.cleaned_data["parent_offtime"]
        start = self.cleaned_data["start_date"]
        end = self.cleaned_data["end_date"]
        f = self.cleaned_data["person"].offtimes()
        f = f.exclude(pk=self.instance.id).filter
        if parent_offtime is None:
            overlapping = f(start_date__lte=start, end_date__gt=start) \
                        | f(start_date__lt=end, end_date__gte=end) \
                        | f(start_date__gt=start, end_date__lt=end)

            for offtime in overlapping:
                msg = 'Dates are overlapping with an event from %s to %s.' \
                        % (offtime.start_date.date(), offtime.end_date.date())
                self._errors["start_date"] = self.error_class([msg])
        else:
            overlapping = f(start_date__lte=start, end_date__gte=end)
            if not len(overlapping):
                msg = 'Dates are not in parent offtime range (%s to %s).' \
                      % (parent_offtime.start_date.date(),
                         parent_offtime.end_date.date())
                self._errors["start_date"] = self.error_class([msg])

    class Meta:
        model = models.Offtime
        exclude = 'deleted', 'added_date'
        widgets = {'start_date': DateWidget(), 'end_date': EndDateWidget()}


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
    def add_offtimes(person):
        offtimes = []
        # Order by should be by pk - the timeline javascript displays the
        # former below the latter (which can be parent offtimes).
        for o in person.offtimes().order_by('pk'):
            t = add_offtime_type(o.type)
            tup = o.pk, t, o.start_date.isoformat(), o.end_date.isoformat(), o.approved
            offtimes.append(tup)
        return offtimes

    def add_offtime_type(typ):
        offtime_types[typ.pk] = typ.name, typ.color
        return typ.pk

    NO_CAP = 'No capabilities'
    capabilities = {NO_CAP: []}
    persons = {}
    offtime_types = {}

    for person in models.Person.objects.filter(deleted=False):
        caps = person.capabilities()
        for c in caps:
            if c.name not in capabilities:
                capabilities[c.name] = []
            capabilities[c.name].append(person)
        if not caps:
            capabilities[NO_CAP].append(person)

        persons[person.pk] = person.name, add_offtimes(person)

    for k, pers in capabilities.items():
        capabilities[k] = [p.pk for p in pers], \
                          models.capability_available_dates(pers, iso_dates=True)

    # sort capabilities in an ordered dict
    capabilities = OrderedDict(sorted(capabilities.items(), key=lambda t: t[0]))
    content = {
        'persons': persons,
        'capabilities': capabilities,
        'offtime_types': offtime_types,
    }
    return HttpResponse(json.dumps(content), mimetype="application/json")


def offtime(request, offtime_id, action=None):
    offtime = models.Offtime.objects.get(pk=offtime_id)
    if action is not None and request.user.is_authenticated():
        if action == 'accept':
            offtime.approved = True
        elif action == 'unaccept':
            offtime.approved = False
        elif action == 'delete':
            offtime.deleted = True
            for o in offtime.child_offtimes():
                o.deleted = True
                o.save()
        elif action == 'undelete':
            offtime.deleted = False
        offtime.save()
    return render(request, 'offtime.html', {'offtime': offtime},
                  context_instance=RequestContext(request))


def person_detail(request, person_id):
    person = models.Person.objects.get(pk=person_id)

    # Only show vacation periods that are now enough.
    context = {
        'person': person,
        'unapproved_offtimes': person.offtimes().filter(approved=False)
    }

    return render(request, 'person_detail.html', context,
                  context_instance=RequestContext(request))


@login_required
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


@login_required
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


@login_required
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


@login_required
def delete_person_capability(request, person_id, capability_id):
    models.PersonCapability.objects.filter(person__pk=person_id,
                                       capability__pk=capability_id).delete()
    return redirect('person')


@login_required
def modify_offtime(request, edit_id=None, parent_offtime=None):
    instance = models.Offtime.objects.get(pk=edit_id) if edit_id else None
    if request.method == 'POST':
        f = OfftimeForm(request.POST, instance=instance)
        if f.is_valid():
            f.save()
            return HttpResponse('', mimetype="application/json")
    else:
        data = {}
        if parent_offtime:
            offtime = models.Offtime.objects.get(pk=parent_offtime)
            data['person'] = offtime.person
            data['parent_offtime'] = parent_offtime
        f = OfftimeForm(data, instance=instance)

    return render_to_response('offtime_form_modal.html', {'offtime_form': f},
                              context_instance=RequestContext(request))
