import re
from itertools import chain
from datetime import timedelta, date

from django.db import models
from django.forms import ValidationError
from django.template.defaultfilters import date as django_date
from south.modelsinspector import add_introspection_rules


# options: 'islamic' (thursday/friday), 'western' (saturday/sunday), None (no weekend)
WEEKEND_TYPE = 'islamic'
VACATION_PER_YEAR = 25


def vacation_days(start_date, end_date):
    # end date is also included
    days = (end_date - start_date + timedelta(1)).days
    return int(round(days/365.0*VACATION_PER_YEAR))


def capability_available_dates(persons, iso_dates=False):
    def clean_duplicates(result):
        # delete entries with the same number of persons
        for i, (k, v) in enumerate(result):
            for j, (k2, v2) in enumerate(result[i+1:], i+1):
                if v != v2:
                    break
                del result[i+1]
    offtimes = list(chain.from_iterable(p.offtimes() for p in persons))
    num_persons = len(persons)
    dates = {o.start_date:num_persons for o in offtimes}
    dates.update({o.end_date:num_persons for o in offtimes})
    dates_lst = sorted(dates)

    x = dates_lst.index
    for offtime in offtimes:
        for _date in dates_lst[x(offtime.start_date):x(offtime.end_date)]:
            dates[_date] -= 1

    if iso_dates:
        result = [(k.isoformat(), v) for k, v in sorted(dates.items())]
    else:
        result = [(k, v) for k, v in sorted(dates.items())]

    clean_duplicates(result)
    return [(None, num_persons)] + result


class ColorField(models.CharField):
    def validate(self, value, model_instance):
        if not re.match('#[\da-f]', value):
            raise ValidationError("Color doesn't have a valid hex code!")
        super(type(self), self).validate(value, model_instance)


add_introspection_rules([], ["^main\.models\.ColorField"])


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
        def add(first, second):
            result.append((first, second))

        result = []
        furloughs = self.offtimes() \
            .filter(type__type_choice=OfftimeType.FURLOUGH).order_by('start_date')
        if not furloughs:
            return []
        last_date = self.offtimes().latest('end_date').end_date
        dates = zip([f.end_date for f in furloughs],
                    [f.start_date for f in furloughs[1:]] + [None])
        YEAR = 365
        y = timedelta(YEAR)
        for first, second in dates:
            temp = second
            if second is None:
                second = last_date
            while first + y < second:
                add(first, first + y)
                first += y
            add(first, temp or first + y)
        return result

    def vacation_periods(self):
        return [VacationPeriod(self, s,e)
                for s, e in self._vacation_period_dates()]

    def vacation_periods_active(self):
        return [v for v in self.vacation_periods() if v.end > date.today()]


class VacationPeriod(object):
    def __init__(self, person, start, end):
        def weekend_days(start, end):
            day = start
            result = 0
            while day < end:
                if WEEKEND_TYPE == 'islamic':
                    if day.weekday() in (3, 4):
                        result += 1
                elif WEEKEND_TYPE == 'western':
                    if day.weekday() in (5, 6):
                        result += 1
                day += timedelta(1)
            return result

        self.start = start.date()
        self.end = (end - timedelta(1)).date()
        self.benefit = vacation_days(start, end)
        vacations = person.offtimes().filter(
                            type__type_choice=OfftimeType.VACATION,
                            end_date__gte=start,
                            start_date__lt=end,
                            )
        self.used = 0
        self.unapproved = 0
        for v in vacations:
            # vacation year break stuff
            if v.end_date < start or v.start_date > end:
                continue
            s = start if v.start_date < start else v.start_date
            e = end if v.end_date > end else v.end_date
            days = (e - s).days - weekend_days(s, e)
            self.used += days
            if not v.approved:
                self.unapproved += days


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
    parent_offtime = models.ForeignKey('self', null=True)

    @property
    def user_end_date(self):
        return (self.end_date - timedelta(1)).date()

    def from_to_str(self):
        return "from %s to %s" % (django_date(self.start_date), django_date(self.user_end_date))

    def __repr__(self):
        return "<%s: %s, %s>" % (self.__class__.__name__, self.type.type,
                                self.from_to_str())
