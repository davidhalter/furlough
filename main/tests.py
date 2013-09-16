"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from datetime import datetime

from django.test import TestCase

from . import models


class TestModels(TestCase):
    fixtures = ['darth.yaml']

    def test_vacation_period(self):
        def get_vacation_period():
            vacation_periods = person.vacation_periods()
            assert len(vacation_periods) == 1
            return vacation_periods[0]

        person = models.Person.objects.get(pk=1)
        vacations = person.offtimes().filter(type__type_choice=models.OfftimeType.VACATION)
        assert vacations
        # A whole year should make a benefit of 20 days.
        v = get_vacation_period()
        assert v.benefit == models.VACATION_PER_YEAR
        self.assertEqual(v.used, 16)
        self.assertEqual(v.unaccepted, 16)


class TestForms(TestCase):
    pass
