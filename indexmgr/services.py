# coding: utf-8

""" Couche de services métiers """

from . import models
from datetime import timedelta

ONE_DAY = timedelta(1)

def compute_missing_index_values(index):
    """ Calcule les valeurs manquantes
        entre le relevé (index) et le relevé manuel
        ou importé précédent.
    """

    # next = pivot.next()
    # if next:
    #     interpolate_index_between(site, index, next)

    previous = index.previous()
    if previous:
        interpolate_index_between(previous, index)

def interpolate_index_between(t1, t2):
    """ Calcule les relevés manquants entre le relevé t1
        et le relevé t2, par interpolation linéaire
        des valeurs des index en t1 et t2
        (production journalière uniforme).
        t1 doit être antérieur à t2.
    """

    if t1.date >= t2.date:
        t1, t2 = t2, t1

    assert(t2.previous().id == t1.id)
    
    days = (t2.date - t1.date).days
    daily_production = (t2.index - t1.index) / days
    # daily_production = 10

    date = t2.date - ONE_DAY
    meter_value = t2.meter_value - daily_production
    index = t2.index - daily_production

    t2.production = daily_production
    t2.save()
    count = 0

    while date > t1.date:
        # TODO check record does not already exist ?
        models.SiteDailyProduction.objects.create(
                site=t2.site,
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
        count = count + 1

    return count