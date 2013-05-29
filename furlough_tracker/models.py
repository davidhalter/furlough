from django.db import models


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
    color = models.CharField()
    type_choices = models.CharField(choices=CALCULATED_CHOICES)


class Offtime(models.Model):
    person = models.ForeignKey(Person)
    type = models.ForeignKey(OfftimeType)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
