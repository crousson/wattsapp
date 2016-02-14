# coding: utf-8

""" Services métiers """

from . import models
from datetime import timedelta

ONE_DAY = timedelta(1)

def recompute_all_indices(site):
    """ Recalcule tous les relevés calculés
        pour le site donné.
        Retourne le nombre de relevés modifiés.
    """

    next = None
    count = 0

    records = (models.SiteDailyProduction.objects
        .filter(site=site,source__in=('M', 'I'))
        .order_by('-date'))

    for record in records:
        if next:
            count += interpolate_index_between(record, next)
        next = record

    return count


def update_computed_indices_from(index):
    """ Calcule les valeurs intermédiaires
        entre le relevé (index) et les relevés manuels
        ou importés précédent et suivant.
    """

    next = index.next()
    if next:
        interpolate_index_between(index, next)

    previous = index.previous()
    if previous:
        interpolate_index_between(previous, index)


def interpolate_index_between(t1, t2):
    """ Calcule les relevés manquants entre le relevé t1
        et le relevé t2, par interpolation linéaire
        des valeurs des index en t1 et t2
        (production journalière uniforme).
        t1 doit être antérieur à t2.
        Retourne le nombre de relevés créés ou modifiés.
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

    existing_records = (models.SiteDailyProduction.objects
        .filter(site=t2.site,date__gte=t1.date,date__lt=t2.date)
        .order_by('-date'))

    for record in existing_records:

        # 1. Create missing records
        while date > record.date:
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

        # 2. Update existing ones
        if record.source == 'C' and date > t1.date:
            record.save(
                    meter_value=meter_value,
                    index=index,
                    production=daily_production,
                )
            count = count + 1

        date = date - ONE_DAY
        meter_value = meter_value - daily_production
        index = index - daily_production

    return count