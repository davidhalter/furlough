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

    def test_vacation_periods(self):
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
        assert vacations[0].accepted == False
        self.assertEqual(v.unaccepted, 16)

        vacations[0].accepted = True
        vacations[0].save()
        v = get_vacation_period()
        self.assertEqual(v.used, 16)
        self.assertEqual(v.unaccepted, 0)

    def test_multi_vacation_periods(self):
        """
    person = models.ForeignKey(Person)
    type = models.ForeignKey(OfftimeType, on_delete=models.PROTECT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    accepted = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    deleted = models.BooleanField(default=False)
    added_date = models.DateTimeField(auto_now_add=True, blank=True)
        """
        person = models.Person.objects.get(pk=1)
        start = datetime(2014, 6, 10)
        stop = datetime(2014, 6, 17)
        vacation = models.OfftimeType.objects.get(
                                    type_choice=models.OfftimeType.VACATION)
        offtime = models.Offtime(person=person, type=vacation,
                                 start_date=start, end_date=stop)
        offtime.save()

        vp = person.vacation_periods()
        assert len(vp) == 2
        # until June 12th
        self.assertEqual(vp[0].used, 16 + 2)
        self.assertEqual(vp[1].used, 5)



class TestForms(TestCase):
    pass
