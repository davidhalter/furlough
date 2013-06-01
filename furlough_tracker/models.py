import re

from django.db import models
from django.forms import ValidationError


class ColorField(models.CharField):
    def validate(self, value, model_instance):
        if not re.match('#[\da-f]', value):
            raise ValidationError("Color doesn't have a valid hex code!")
        super(type(self), self).validate(value, model_instance)

class Person(models.Model):
    name = models.CharField()
    deleted = models.BooleanField(default=False)


class Capability(models.Model):
    name = models.CharField()
    deleted = models.BooleanField(default=False)


class PersonCapability(models.Model):
    person = models.ForeignKey(Person)
    capability = models.ForeignKey(Capability)


class OfftimeType(models.Model):
    CALCULATED_CHOICES = (
        ('furlough', 'Furlough'),
        ('vacation', 'Vacation'),
        ('untracked', 'Untracked Time')
    )
    name = models.CharField(null=False, max_length=30)
    color = ColorField(null=False, max_length=7, default='#000000')
    type_choices = models.CharField(null=False, default='furlough',
                                    max_length=20, choices=CALCULATED_CHOICES)


class Offtime(models.Model):
    person = models.ForeignKey(Person)
    type = models.ForeignKey(OfftimeType)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
