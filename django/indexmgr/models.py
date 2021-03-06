# coding: utf-8

""" Modèle de données """

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models

class Meter(models.Model):
    """ Compteur physique """

    id = models.AutoField(primary_key=True)
    installed = models.DateField(
        help_text="Date d'installation du compteur")
    installation_index = models.PositiveIntegerField(
        help_text="Index de pose du compteur")
    disposed = models.DateField(null=True,
        help_text="Date de dépose du compteur")

class Site(models.Model):
    """ Site de production,
        représentant un système d'énergie renouvelable
    """

    SITE_CATEGORIES = [
        ('PV', 'Photovoltaïque'),
        ('WP', 'Parc éolien'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,
        help_text="Nom du site")
    # Coordonnées géographiques WGS84
    lon = models.FloatField(null=True, help_text="Longitude")
    lat = models.FloatField(null=True, help_text="Latitude")
    category = models.CharField(max_length=2, choices=SITE_CATEGORIES,
        help_text="Type d'installation")
    installed = models.DateField(help_text="Date de mise en service")
    meter = models.ForeignKey(Meter,
        help_text="Compteur associé au site")

    def last_index(self):
        return SiteDailyProduction.objects.filter(site=self).latest('date')

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
    site = models.ForeignKey(Site, help_text="Site de production")
    date = models.DateField(help_text="Date du relevé")
    meter = models.ForeignKey(Meter, help_text="Compteur en service au moment du relevé")
    meter_value = models.PositiveIntegerField(help_text="Index lu sur le compteur")
    index = models.PositiveIntegerField(help_text="Index 'global'")
    source = models.CharField(max_length=1, choices=INDEX_SOURCES,
        help_text="Origine de la valeur : manuelle, importée dans le système, calculée")
    production = models.PositiveIntegerField(null=True,
        help_text="Production du jour du relevé")

    def previous(self):
        """ Retourne le relevé manuel ou importé
            le plus récent avant celui-ci
        """
        try:
            return (SiteDailyProduction.objects
                .filter(site=self.site, date__lt=self.date, source__in=('I', 'M'))
                .latest('date'))
        except SiteDailyProduction.DoesNotExist:
            return None

    def next(self):
        """ Retourne le relevé manuel ou importé
            le plus ancien après celui-ci
        """
        try:
            return (SiteDailyProduction.objects
                .filter(site=self.site, date__gt=self.date, source__in=('I', 'M'))
                .order_by('date')
                .first())
        except SiteDailyProduction.DoesNotExist:
            return None

    def latest(self):
        """ Retourne le dernier relevé
            par ordre chronologique
        """
        try:
            return (SiteDailyProduction.objects
                .filter(site=self.site)
                .latest('date'))
        except SiteDailyProduction.DoesNotExist:
            return None

    def compute_new_index(self):
        """ Calcule la valeur de l'index global
            à partir du delta entre les index lus sur le compteur,
            uniquement pour les nouveaux relevés (non encore enregistré).
            Sinon, retourne la valuer de l'index global enregistré.
        """

        previous = self.previous()
        if previous is None:
            self.index = 0
            self.production = 0
        else:
            if self.meter.id == previous.meter.id:
                self.index = previous.index + (self.meter_value - previous.meter_value)
            else:
                self.index = previous.index + (self.meter_value - self.meter.installation_index)
        return self.index

    def validate(self):
        """ Vérification des règles métiers :
            - R1.1: la date d'un index ne doit pas être antérieure
                    à la date de pose du compteur
            - R1.2: la valeur d'un index
                    ne doit pas être inférieure à l'index d'installation du compteur
            - R2.1: la valeur d'un index entrée manuellement
                    ne doit pas être inférieure à la valeur de l'index précédent
            - R2.2: la valeur d'un index entrée manuellement
                    ne doit pas être supérieure à la valeur de l'index suivant
        """

        self.compute_new_index()

        # R1.1: la date d'un index ne doit pas être antérieure
        #       à la date de pose du compteur
        if (self.date < self.meter.installed):
            raise ValidationError("Index antérieur à la pose du compteur")

        # R1.2: la valeur d'un index
        #       ne doit pas être inférieure à l'index d'installation du compteur
        if self.meter_value < self.meter.installation_index:
            raise ValidationError("Index plus petit que l'index d'installation du compteur")

        # R2.1: la valeur d'un index entrée manuellement
        #       ne doit pas être inférieure à la valeur de l'index précédent
        previous = self.previous()
        if previous and self.index < previous.index:
            raise ValidationError(
                "Index %(index)d plus petit que l'index précédent %(previous)d",
                params={ 'index': self.index, 'previous': previous.index })

        # R2.2: la valeur d'un index entrée manuellement
        #       ne doit pas être supérieure à la valeur de l'index suivant
        next = self.next()
        if next and self.index > next.index:
            raise ValidationError(
                "Index %(index)d plus grand que l'index suivant %(next)d",
                params={ 'index': self.index, 'next': next.index })

    def save(self, *args, **kwargs):
        self.validate()
        super(SiteDailyProduction, self).save(*args, **kwargs)

