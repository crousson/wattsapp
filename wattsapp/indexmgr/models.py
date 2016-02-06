# coding: utf-8

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models

class Meter(models.Model):
    """ Compteur physique
    """

    id = models.AutoField(primary_key=True)
    installed = models.DateField()
    installation_index = models.PositiveIntegerField()
    disposed = models.DateField(null=True)

class Site(models.Model):
    """ Site de production,
        représentant un système d'énergie renouvelable
    """

    SITE_CATEGORIES = [
        ('PV', 'Photovoltaïque'),
        ('WP', 'Parc éolien'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    lon = models.FloatField(null=True)
    lat = models.FloatField(null=True)
    category = models.CharField(max_length=2, choices=SITE_CATEGORIES)
    installed = models.DateField()
    meter = models.ForeignKey(Meter)

    def last_index(self):
        try:
            return SiteDailyProduction.objects.filter(site=self).latest('date')
        except SiteDailyProduction.DoesNotExist:
            return None

class SiteDailyProduction(models.Model):
    """ Enregistrement journalier de la production
        de chaque site

        Le relevé peut être alimenté :
        1. manuellement
        2. par un import de données
        3. par un calcul aux dates manquantes
           entre deux relevés existants
    """

    INDEX_SOURCES = [
        ('M', 'Entrée manuelle'),
        ('I', 'Entrée importée'),
        ('C', 'Entrée calculée'),
    ]

    id = models.AutoField(primary_key=True)
    site = models.ForeignKey(Site)
    date = models.DateField()
    meter = models.ForeignKey(Meter)
    meter_value = models.PositiveIntegerField()
    index = models.PositiveIntegerField()
    source = models.CharField(max_length=1, choices=INDEX_SOURCES)
    production = models.PositiveIntegerField(null=True)

    def compute_new_index(self):
        previous = self.site.last_index()
        if previous is None:
            self.index = 0
        else:
            if self.meter.id == previous.meter.id:
                self.index = previous.index + (self.meter_value - previous.meter_value)
            else:
                self.index = previous.index + (self.meter_value - self.meter.installation_index)
        return self.index

    def validate(self):

        # R1: la date d'un index ne doit pas être antérieure
        #     à la date de pose du compteur
        if (self.date < self.meter.installed):
            raise ValidationError("Date antérieure à la pose du compteur")

        # R2: la valeur d'un index entrée manuellement
        #     ne doit pas être inférieure à la valeur du dernier index
        previous = self.site.last_index()
        if previous and self.source == 'M':
            if self.meter.id == previous.meter.id:
                if self.meter_value < previous.meter_value:
                    raise ValidationError("Index plus petit que le prédédent")
            else:
                if self.meter_value < self.meter.installation_index:
                    raise ValidationError("Index plus petit que l'index d'installation du compteur")

    def save(self, *args, **kwargs):
        self.validate()
        self.compute_new_index()
        super(SiteDailyProduction, self).save(*args, **kwargs)

