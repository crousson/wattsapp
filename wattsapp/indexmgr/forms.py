# coding: utf-8

from django import forms
from django.db import transaction
from models import *
from . import services

class ManualIndexLogger(object):

    def logIndex(self, site, date, meter_value):
        index_record = SiteDailyProduction.objects.create(
                site=site,
                date=date,
                meter=site.meter,
                meter_value=meter_value,
                production=None,
                source='M',
            )
        # index_record.save()
        services.compute_index_values_around(site, index_record)

class NewSiteForm(forms.Form, ManualIndexLogger):

    name = forms.CharField(max_length=100)
    category = forms.ChoiceField(choices=Site.SITE_CATEGORIES)
    installed = forms.DateField()
    index = forms.IntegerField(min_value=0)
    
    @transaction.atomic
    def execute(self):
        
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

class ChangeMeterForm(forms.Form, ManualIndexLogger):

    site_id = forms.IntegerField()
    index = forms.IntegerField(min_value=0)
    new_index = forms.IntegerField(min_value=0)
    date = forms.DateField()

    @transaction.atomic
    def execute(self):

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

class ManualIndexRecordForm(forms.Form, ManualIndexLogger):

    site_id = forms.IntegerField()
    index = forms.IntegerField(min_value=0)
    date = forms.DateField()

    def execute(self):

        site_id = self.cleaned_data['site_id']
        site = Site.objects.get(id=site_id)
        index = self.cleaned_data['index']
        date = self.cleaned_data['date']
        
        self.logIndex(site, date, index)