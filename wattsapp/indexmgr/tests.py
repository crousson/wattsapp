# coding: utf-8

from django.core.exceptions import ValidationError
from django.test import TestCase

from . import models
from . import forms
from . import services

from datetime import date

class SiteTestCase(TestCase):

    def setUp(self):
        f = forms.NewSiteForm({
                'name':'Nouveau site',
                'category': 'PV',
                'index': 200,
                'installed': '2016-01-01'
            })
        self.assertTrue(f.is_valid())
        f.execute()

    def test_create_site(self):
        """
        """
        site = models.Site.objects.first()
        self.assertEqual(site.name, 'Nouveau site')
        
        # New meter got associated with new site
        self.assertIsNotNone(site.meter)
        self.assertEqual(site.meter.installation_index, 200)
        
        # Global index starts at 0
        self.assertIsNotNone(site.last_index())
        self.assertEqual(site.last_index().index, 0)

class SiteDailyProductionTestCase(TestCase):

    def setUp(self):
        f = forms.NewSiteForm({
                'name':'Nouveau site',
                'category': 'PV',
                'index': 100,
                'installed': '2016-01-01'
            })
        self.assertTrue(f.is_valid())
        f.execute()
        self.site = models.Site.objects.first()

    def test_r1_valid_date(self):

        # Given an index date after meter installation
        # When I create a new index record
        # Then the new index is recorded
        models.SiteDailyProduction.objects.create(
                site=self.site,
                meter=self.site.meter,
                meter_value=110,
                date=date(2016, 1, 5)
            )

        # Given an index date prior to meter installation
        # When I create a new index record
        # Then I get a validation error
        with self.assertRaises(ValidationError):
            models.SiteDailyProduction.objects.create(
                    site=self.site,
                    meter=self.site.meter,
                    meter_value=110,
                    date=date(2015, 12, 5)
                )        

    def test_r2_monotonic_index(self):
        
        # Given an index value greater than last recorded value
        # When I create a new index record
        # Then the new index is recorded
        models.SiteDailyProduction.objects.create(
                site=self.site,
                meter=self.site.meter,
                meter_value=self.site.last_index().meter_value + 10,
                date=date(2016, 1, 5),
                source='M'
            )

        # Given an index value greater equal to last recorded value
        # When I create a new manual index record
        # Then the new index is recorded
        models.SiteDailyProduction.objects.create(
                site=self.site,
                meter=self.site.meter,
                meter_value=self.site.last_index().meter_value,
                date=date(2016, 1, 5),
                source='M'
            )

        # Given an index value less than last recorded value
        # When I create a new manual index record
        # Then I get a validation error
        with self.assertRaises(ValidationError):
            models.SiteDailyProduction.objects.create(
                    site=self.site,
                    meter=self.site.meter,
                    meter_value=self.site.last_index().meter_value - 10,
                    date=date(2016, 1, 5),
                    source='M'
                )

    def test_r2_monotonic_index_when_meter_changed(self):

        # Given the meter changed
        # and an index value less than the installation index
        meter = models.Meter.objects.create(
                installation_index=200,
                installed=date(2016, 1, 10)
            )
        meter_value = 150
        # When I create a new manual index record
        # Then I get a validation error
        with self.assertRaises(ValidationError):
            models.SiteDailyProduction.objects.create(
                    site=self.site,
                    meter=meter,
                    meter_value=meter_value,
                    date=date(2016, 1, 15),
                    source='M'
                )

        # Given the meter changed and an index value greater than
        # or equal to the installation index
        meter_value = 250
        # When I create a new manual index record
        # Then the new index is recorded
        models.SiteDailyProduction.objects.create(
                site=self.site,
                meter=meter,
                meter_value=meter_value,
                date=date(2016, 1, 15),
                source='M'
            )

class ComputeMissingIndexValuesTestCase(TestCase):

    def setUp(self):

        # 1. Un site est créé le 1 janvier 2016.
        #    L'index global est initialisé à 0
        f = forms.NewSiteForm({
                'name':'Nouveau site',
                'category': 'PV',
                'index': 0,
                'installed': '2016-01-01'
            })
        self.assertTrue(f.is_valid())
        f.execute()
        self.site = models.Site.objects.first()
        self.assertIsNotNone(self.site)
        self.assertEqual(self.site.last_index().index, 0)

        # 2. L'utilisateur saisit un index de 100 à la date du 10 janvier 2016
        f = forms.ManualIndexRecordForm({
                'site_id': self.site.id,
                'index': 100,
                'date': '2016-01-10'
            })
        self.assertTrue(f.is_valid())
        f.execute()

        # 3. Le compteur est changé le 20 janvier 2016
        #    L'index de dépose est 200 et l'index de pose du nouveau compteur est 1000
        f = forms.ChangeMeterForm({
                'site_id': self.site.id,
                'index': 200,
                'new_index': 1000,
                'date': '2016-01-20'
            })
        self.assertTrue(f.is_valid())
        f.execute()

        # 4. L'utilisateur saisit un index de 1100 à la date du 1 février 2016
        f = forms.ManualIndexRecordForm({
                'site_id': self.site.id,
                'index': 1100,
                'date': '2016-02-01'
            })
        self.assertTrue(f.is_valid())
        f.execute()

        # 5. L'utilisateur saisit un index de 1200 à la date du 10 février 2016
        f = forms.ManualIndexRecordForm({
                'site_id': self.site.id,
                'index': 1200,
                'date': '2016-02-10'
            })
        self.assertTrue(f.is_valid())
        f.execute()

    def test_compute_missing_values(self):
        services.compute_missing_index_values(self.site)
        for index in models.SiteDailyProduction.objects.filter(site=self.site).order_by('date'):
            print index.site.id, index.date, index.meter_value, index.index, index.production
        self.assertEquals(
            models.SiteDailyProduction.objects.filter(site=self.site).count(),
            41)

