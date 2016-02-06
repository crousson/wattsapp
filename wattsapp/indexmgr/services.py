# coding: utf-8

from . import models
from datetime import timedelta

ONE_DAY = timedelta(1)

def compute_all_index_values(site):
    
    next = None
    for pivot in site.sitedailyproduction_set.filter(source__in=('M','I')).order_by('-date'):
        if next:
            interpolate_index_between(site, pivot, next)
        next = pivot

def compute_index_values_around(site, pivot):

    next = pivot.next()
    if next:
        interpolate_index_between(site, pivot, next)

    previous = pivot.previous()
    if previous:
        interpolate_index_between(site, previous, pivot)

def interpolate_index_between(site, t1, t2):

    if t1.date >= t2.date:
        return
    
    days = (t2.date - t1.date).days
    daily_production = (t2.index - t1.index) / days
    # daily_production = 10
    computed_records = (models.SiteDailyProduction.objects
        .filter(site=site, source='C', date__gt=t1.date, date__lt=t2.date)
        .order_by('-date'))

    date = t2.date - ONE_DAY
    meter_value = t2.meter_value - daily_production
    index = t2.index - daily_production

    t2.production = daily_production
    t2.save()

    for record in computed_records:
        while date > t1.date and date > record.date:
            # TODO check record does not already exist ?
            models.SiteDailyProduction.objects.create(
                    site=site,
                    date=date,
                    meter=t2.meter,
                    meter_value=meter_value,
                    index=index,
                    production=daily_production,
                    source='C',
                )
            date = date - ONE_DAY
            meter_value = meter_value - daily_production
            index = index - daily_production
        record.meter_value = meter_value
        record.production = daily_production
        record.index = index
        record.save()
        date = date - ONE_DAY
        meter_value = meter_value - daily_production
        index = index - daily_production

    while date > t1.date:
        # TODO check record does not already exist ?
        models.SiteDailyProduction.objects.create(
                site=site,
                date=date,
                meter=t2.meter,
                meter_value=meter_value,
                index=index,
                production=daily_production,
                source='C',
            )
        date = date - ONE_DAY
        meter_value = meter_value - daily_production
        index = index - daily_production