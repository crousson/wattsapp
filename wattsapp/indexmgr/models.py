# coding: utf-8

from __future__ import unicode_literals

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
            return SiteIndex.objects.filter(site=self).latest('date')
        except SiteIndex.DoesNotExist:
            return None

class SiteDailyProduction(models.Model):
    """ Enregistrement journalier de la production
        de chaque site
    """
    
    id = models.AutoField(primary_key=True)
    site = models.ForeignKey(Site)
    date = models.DateField()
    value = models.PositiveIntegerField()

class SiteIndex(models.Model):
    """ Relevé journalier des index de chaque site.
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
    value = models.PositiveIntegerField()
    source = models.CharField(max_length=1, choices=INDEX_SOURCES)

    def validate(self):

        # R1: la date d'un index ne doit pas être antérieure
        #     à la date de pose du compteur
        if (self.date < self.meter.installed):
            raise Exception('Date antérieure à la pose du compteur')

        # R2: la valeur d'un index entrée manuellement
        #     ne doit pas être inférieure à la valeur du dernier index
        previous = self.site.last_index()
        if (self.source == 'M' and previous and self.value < previous.value):
            raise Exception('Index plus petit que le prédédent')

    def save(self, *args, **kwargs):
        self.validate()
        super(SiteIndex, self).save(*args, **kwargs)

