# coding: utf-8

""" Actions et logique du domaine """

from django import forms
from django.db import transaction
from models import *
from . import services

class ManualIndexValidator(object):
    """ Mixin pour valider un nouveau relevé

        L'objet doit fournir les champs suivants
        qui sont utilisés pour créer le relevé :
        - site_id (IntegerField)
        - index (IntegerField)
        - date (DateField)

        Voir le modèle models.SiteDailyProduction
    """

    def clean(self):

        super(ManualIndexValidator, self).clean()

        site_id = self.cleaned_data.get('site_id')
        site = Site.objects.get(id=site_id)
        index = self.cleaned_data.get('index')
        date = self.cleaned_data.get('date')
        if index is not None and date:
            self.validateIndex(site, date, index)

    def validateIndex(self, site, date, meter_value):
        """ Valide la date et la valeur d'index
            par rapport aux autres relevés existants.

            params:
            - site : objet Site concerné par le relevé
            - date : date du relevé
            - meter_value : valeur d'index lue sur le compteur
        """

        index_record = SiteDailyProduction(
                site=site,
                date=date,
                meter=site.meter,
                meter_value=meter_value,
                production=None,
                source='M',
            )
        index_record.validate()

class ManualIndexLogger(object):
    """ Mixin pour enregistrer un nouveau relevé """

    def logIndex(self, site, date, meter_value):
        """ Enregistre un nouveau relevé.

            params:
            - site : objet Site concerné par le relevé
            - date : date du relevé
            - meter_value : valeur d'index lue sur le compteur
        """

        record = SiteDailyProduction.objects.create(
                site=site,
                date=date,
                meter=site.meter,
                meter_value=meter_value,
                production=None,
                source='M',
            )
        # index_record.save()
        services.update_computed_indices_from(record)

class NewSiteForm(ManualIndexLogger, forms.Form):
    """ Création d'un nouveau site :
        - déclare un nouveau site
        - en lui associant un compteur et son index de pose
        - enregistre un relevé de mise en service,
          avec un index global initialisé à 0
    """

    name = forms.CharField(max_length=100)
    category = forms.ChoiceField(choices=Site.SITE_CATEGORIES)
    installed = forms.DateField()
    index = forms.IntegerField(min_value=0)
    
    @transaction.atomic
    def execute(self):
        """ Retourne le site créé. """
        
        name = self.cleaned_data['name']
        category = self.cleaned_data['category']
        installed = self.cleaned_data['installed']
        index = self.cleaned_data['index']

        meter = Meter.objects.create(
                installed=installed,
                installation_index=index,
            )
        # meter.save()

        site = Site.objects.create(
                name=name,
                category=category,
                installed=installed,
                meter=meter,
            )
        # site.save()

        self.logIndex(site, installed, index)

        return site

class ChangeMeterForm(ManualIndexValidator, ManualIndexLogger, forms.Form):
    """ Changement de compteur
        - enregistre un relevé avec l'index de dépose du compteur
        - associe à un nouveau compteur au site, avec son index de pose
    """

    site_id = forms.IntegerField(widget=forms.HiddenInput, required=True)
    index = forms.IntegerField(min_value=0, required=True)
    new_index = forms.IntegerField(min_value=0, required=True)
    date = forms.DateField(widget=forms.DateInput, required=True)

    @transaction.atomic
    def execute(self):
        """ Retourne le site modifié. """

        site_id = self.cleaned_data['site_id']
        site = Site.objects.get(id=site_id)
        index = self.cleaned_data['index']
        new_index = self.cleaned_data['new_index']
        date = self.cleaned_data['date']
        
        self.logIndex(site, date, index)

        site.meter.disposed = date
        # site.meter.save()

        meter = Meter.objects.create(
                installed=date,
                installation_index=new_index,
            )
        # meter.save()

        site.meter = meter
        site.save()

        return site

class ManualIndexRecordForm(ManualIndexValidator, ManualIndexLogger, forms.Form):
    """ Enregistrement d'un nouveau relevé manuel """

    site_id = forms.IntegerField(widget=forms.HiddenInput)
    index = forms.IntegerField(min_value=0)
    date = forms.DateField(widget=forms.DateInput)

    @transaction.atomic
    def execute(self):
        """ Retourne le nouvel index enregistré """

        site_id = self.cleaned_data['site_id']
        site = Site.objects.get(id=site_id)
        index = self.cleaned_data['index']
        date = self.cleaned_data['date']
        
        self.logIndex(site, date, index)

        return index