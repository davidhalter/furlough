import re

from django.db import models
from django.forms import ValidationError
from django.template.defaultfilters import date


class ColorField(models.CharField):
    def validate(self, value, model_instance):
        if not re.match('#[\da-f]', value):
            raise ValidationError("Color doesn't have a valid hex code!")
        super(type(self), self).validate(value, model_instance)


class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    deleted = models.BooleanField(default=False)

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.name

    def capabilities(self):
        return Capability.objects.filter(personcapability__person=self)

    def offtimes(self):
        return Offtime.objects.filter(person=self, deleted=False)

    def latest_furlough(self):
        return Offtime.objects.filter(
                        person=self,
                        type__type_choice=OfftimeType.FURLOUGH,
                        deleted=False).latest('end_date')

    def vacation_periods(self):
        latest_furlough_end = self.latest_furlough().end_date
        return Offtime.objects.filter(
                        person=self,
                        start_date__gt=latest_furlough_end,
                        type__type_choice=OfftimeType.VACATION,
                        deleted=False)


class Capability(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def persons(self):
        return Person.objects.filter(personcapability__capability=self)


class PersonCapability(models.Model):
    person = models.ForeignKey(Person)
    capability = models.ForeignKey(Capability, on_delete=models.PROTECT)

    class Meta:
        unique_together = 'person', 'capability'
        db_table = 'person_capability'


class OfftimeType(models.Model):
    FURLOUGH = 'furlough'
    VACATION = 'vacation'
    UNTRACKED = 'untracked'
    CALCULATED_CHOICES = (
        (FURLOUGH, 'Furlough'),
        (VACATION, 'Vacation'),
        (UNTRACKED, 'Untracked Time')
    )
    name = models.CharField(max_length=30)
    color = ColorField(max_length=7, default='#000000')
    type_choice = models.CharField(default=UNTRACKED,
                                   max_length=20, choices=CALCULATED_CHOICES)

    class Meta:
        db_table = 'offtime_type'

    @property
    def type(self):
        return dict(self.CALCULATED_CHOICES)[self.type_choice]

    def __str__(self):
        return self.name


class Offtime(models.Model):
    person = models.ForeignKey(Person)
    type = models.ForeignKey(OfftimeType, on_delete=models.PROTECT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    accepted = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    deleted = models.BooleanField(default=False)
    added_date = models.DateTimeField(auto_now_add=True, blank=True)

    def from_to_str(self):
        return "from %s to %s" % (date(self.start_date), date(self.end_date))
