import re

from django.db import models
from django.forms import ValidationError


class ColorField(models.CharField):
    def validate(self, value, model_instance):
        if not re.match('#[\da-f]', value):
            raise ValidationError("Color doesn't have a valid hex code!")
        super(type(self), self).validate(value, model_instance)


class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    deleted = models.BooleanField(default=False)


class Capability(models.Model):
    name = models.CharField(max_length=30)


class PersonCapability(models.Model):
    person = models.ForeignKey(Person)
    capability = models.ForeignKey(Capability, on_delete=models.PROTECT)


class OfftimeType(models.Model):
    FURLOUGH = 'furlough'
    VACATION = 'vacation'
    UNTRACKED = 'untracked'
    CALCULATED_CHOICES = (
        (FURLOUGH, 'Furlough'),
        (VACATION, 'Vacation'),
        (UNTRACKED, 'Untracked Time')
    )
    name = models.CharField(null=False, max_length=30)
    color = ColorField(null=False, max_length=7, default='#000000')
    type_choice = models.CharField(null=False, default='furlough',
                                   max_length=20, choices=CALCULATED_CHOICES)

    class Meta:
        db_table = 'offtime_type'

    @property
    def type(self):
        return dict(self.CALCULATED_CHOICES)[self.type_choice]


class Offtime(models.Model):
    person = models.ForeignKey(Person)
    type = models.ForeignKey(OfftimeType, on_delete=models.PROTECT)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
