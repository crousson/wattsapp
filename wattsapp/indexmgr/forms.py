# coding: utf-8

from django import forms
from django.db import transaction
from models import *

class NewSiteForm(forms.Form):

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
        meter.save()

        site = Site.objects.create(
                name=name,
                category=category,
                installed=installed,
                meter=meter,
            )
        site.save()

        index_record = SiteIndex.objects.create(
                site=site,
                date=installed,
                meter=meter,
                meter_value=index,
                value=0,
                source='M',
            )
        index_record.save()

class ChangeMeterForm(forms.Form):

    index = forms.IntegerField(min_value=0)
    new_index = forms.IntegerField(min_value=0)
    date = forms.DateInput()

    @transaction.atomic
    def execute(self):

        site = None # TODO get from url
        index = self.cleaned_data['index']
        new_index = self.cleaned_data['new_index']
        date = self.cleaned_data['date']
        
        index_record = SiteIndex.objects.create(
                site=site,
                date=date,
                meter=site.meter,
                meter_value=index,
                value=None,
                source='M',
            )
        index.save()

        site.meter.disposed = date
        site.meter.save()

        meter = Meter.objects.create(
                installed=date,
                installation_index=new_index,
            )
        meter.save()

        site.meter = meter
        site.save()

class ManualIndexRecordForm(forms.Form):

    index = forms.IntegerField(min_value=0)
    date = forms.DateInput()

    def execute(self):

        site = None
        index = self.cleaned_data['index']
        date = self.cleaned_data['date']
        
        index_record = SiteIndex.objects.create(
                site=site,
                date=date,
                meter=site.meter,
                meter_value=index,
                value=None,
                source='M',
            )
        index.save()