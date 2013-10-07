import re
from datetime import timedelta

from django.db import models
from django.forms import ValidationError
from django.template.defaultfilters import date


VACATION_PER_YEAR = 25

def vacation_days(start_date, end_date):
    return int((end_date - start_date).days/365.0*20)


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
        # somehow this has to be a string, not unicode
        return self.name.encode('utf-8')

    def capabilities(self):
        return Capability.objects.filter(personcapability__person=self)

    def offtimes(self):
        return Offtime.objects.filter(person=self, deleted=False)

    def _vacation_period_dates(self):
        furloughs = \
                self.offtimes().filter(type__type_choice=OfftimeType.FURLOUGH).order_by('start_date')
        if not furloughs:
            return []
        last_date = self.offtimes().latest('end_date').end_date
        dates = zip([f.end_date for f in furloughs],
                    [f.start_date for f in furloughs[1:]] + [None])
        YEAR = 365
        y = timedelta(YEAR)
        result = []
        for first, second in dates:
            temp = second
            if second is None:
                second = last_date
            while first + y < second:
                result.append((first, first + y))
                first += y
            result.append((first, temp or first + y))
        return result

    def vacation_periods(self):
        return [VacationPeriod(self, s,e)
                for s, e in self._vacation_period_dates()]


class VacationPeriod(object):
    def __init__(self, person, start, end):
        self.start = start
        self.end = end
        self.benefit = vacation_days(start, end)
        vacations = person.offtimes().filter(
                            type__type_choice=OfftimeType.VACATION,
                            end_date__gte=start,
                            start_date__lt=end,
                            )
        self.used = 0
        self.unapproved = 0
        for v in vacations:
            days = (v.end_date - v.start_date).days
            # vacation year break stuff
            if v.start_date < start:
                days -= (start - v.start_date).days
            if v.end_date > end:
                days -= (v.end_date - end).days
            if not v.approved:
                self.unapproved += days
            self.used += days


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
    color = ColorField(max_length=7, default='#66B0FF')
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
    approved = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    deleted = models.BooleanField(default=False)
    added_date = models.DateTimeField(auto_now_add=True, blank=True)

    def from_to_str(self):
        return "from %s to %s" % (date(self.start_date), date(self.end_date))

    def __repr__(self):
        return "<%s: %s, %s>" % (self.__class__.__name__, self.type.type,
                                self.from_to_str())
