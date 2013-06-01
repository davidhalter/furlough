import re

from django.db import models
from django.forms import ValidationError


class ColorField(models.CharField):
    def validate(self, value, model_instance):
        if not re.match('#[\da-f]', value):
            raise ValidationError("Color doesn't have a valid hex code!")
        super(type(self), self).validate(value, model_instance)


class Person(models.Model):
    first_name = models.CharField(null=False, max_length=30)
    last_name = models.CharField(null=False, max_length=30)
    deleted = models.BooleanField(null=False, default=False)

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    def capabilities(self):
        return Capability.objects.filter(personcapability__person=self)



class Capability(models.Model):
    name = models.CharField(null=False, max_length=30)

    def __str__(self):
        return self.name


class PersonCapability(models.Model):
    person = models.ForeignKey(Person, null=False)
    capability = models.ForeignKey(Capability, null=False, on_delete=models.PROTECT)

    class Meta:
        unique_together = 'person', 'capability'


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
    type_choice = models.CharField(null=False, default=UNTRACKED,
                                   max_length=20, choices=CALCULATED_CHOICES)

    class Meta:
        db_table = 'offtime_type'

    @property
    def type(self):
        return dict(self.CALCULATED_CHOICES)[self.type_choice]


class Offtime(models.Model):
    person = models.ForeignKey(Person, null=False)
    type = models.ForeignKey(OfftimeType, null=False, on_delete=models.PROTECT)
    accepted = models.BooleanField(null=False, default=False)
    deleted = models.BooleanField(null=False, default=False)
