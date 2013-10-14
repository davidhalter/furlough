"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from datetime import datetime

from django.test import TestCase

from . import models
from . import views

models.WEEKEND_TYPE = None  # disable the weekend type calculation


class TestModels(TestCase):
    fixtures = ['darth.yaml']

    def test_vacation_periods(self):
        def get_vacation_period():
            vacation_periods = person.vacation_periods_active()
            assert len(vacation_periods) == 1
            return vacation_periods[0]

        person = models.Person.objects.get(pk=1)
        vacations = person.offtimes().filter(type__type_choice=models.OfftimeType.VACATION)
        assert vacations
        # A whole year should make a benefit of ``models.VACATION_PER_YEAR``
        v = get_vacation_period()
        self.assertEqual(v.benefit, models.VACATION_PER_YEAR)
        self.assertEqual(v.used, 14)
        assert vacations[0].approved == False
        self.assertEqual(v.unapproved, 14)

        vacations[0].approved = True
        vacations[0].save()
        v = get_vacation_period()
        self.assertEqual(v.used, 14)
        self.assertEqual(v.unapproved, 0)

    def test_multi_vacation_periods(self):
        person = models.Person.objects.get(pk=1)
        start = datetime(2014, 6, 10)
        stop = datetime(2014, 6, 19)
        vacation = models.OfftimeType.objects.get(
                                    type_choice=models.OfftimeType.VACATION)
        offtime = models.Offtime(person=person, type=vacation,
                                 start_date=start, end_date=stop)
        offtime.save()

        vp = person.vacation_periods_active()
        assert len(vp) == 2
        # until June 12th
        self.assertEqual(vp[0].used, 14 + 2)
        self.assertEqual(vp[1].used, 7)

        old, models.WEEKEND_TYPE = models.WEEKEND_TYPE, 'islamic'
        try:
            vp = person.vacation_periods_active()
            self.assertEqual(vp[0].used, 10 + 2)
            self.assertEqual(vp[1].used, 5)
        finally:
            models.WEEKEND_TYPE = old



class TestOfftimeValidation(TestCase):
    fixtures = ['darth.yaml']

    def add_vacation(self, start, end):
        person = models.Person.objects.get(pk=1)
        vacation = models.OfftimeType.objects.get(
                                    type_choice=models.OfftimeType.VACATION)
        offtime = models.Offtime(person=person, type=vacation,
                                 start_date=start, end_date=end)
        offtime.save()
        return offtime

    def test_offtime_form(self):
        # vacation: 2013-09-08 - 2013-09-24
        form_data = {
            'person': 1,
            'type': 1,
            'start_date': datetime(2013, 9, 27),
            'end_date': datetime(2013, 9, 29),
        }
        assert views.OfftimeForm(form_data).is_valid() == True
        form_data['start_date'] = datetime(2013, 9, 20)
        assert views.OfftimeForm(form_data).is_valid() == False
        form_data['start_date'] = datetime(2013, 9, 2)
        assert views.OfftimeForm(form_data).is_valid() == False
        form_data['end_date'] = datetime(2013, 9, 5)
        assert views.OfftimeForm(form_data).is_valid() == True
