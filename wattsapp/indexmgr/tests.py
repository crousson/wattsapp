# coding: utf-8

from django.core.exceptions import ValidationError
from django.test import TestCase

from . import models
from . import forms
from . import services

from datetime import date

class BaseSiteTestCase(TestCase):

    def setUp(self):
        f = forms.NewSiteForm({
                'name':'Nouveau site',
                'category': 'PV',
                'index': 200,
                'installed': '2016-01-01'
            })
        self.assertTrue(f.is_valid())
        f.execute()
        self.site = models.Site.objects.first()

    def create_record_index(self, meter_value, index_date, source='M'):
        return models.SiteDailyProduction.objects.create(
                site=self.site,
                date=index_date,
                meter=self.site.meter,
                meter_value=meter_value,
                production=None,
                source=source,
            )

    def last_index(self):
        return models.SiteDailyProduction.objects.filter(site=self.site).latest('date')

class SiteTestCase(BaseSiteTestCase):

    def test_create_site(self):

        site = self.site
        self.assertEqual(site.name, 'Nouveau site')
        
        # New meter got associated with new site
        self.assertIsNotNone(site.meter, "New meter must be created with new site")
        self.assertEqual(site.meter.installation_index, 200)
        
        index = self.last_index()
        self.assertIsNotNone(index, "Initial index must be recorded with new site")
        self.assertEqual(index.index, 0, "Global index must start at 0")

class SiteDailyProductionTestCase(BaseSiteTestCase):

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
        # When I create a new manual index record
        # Then the new index is recorded
        models.SiteDailyProduction.objects.create(
                site=self.site,
                meter=self.site.meter,
                meter_value=self.last_index().meter_value + 10,
                date=date(2016, 1, 5),
                source='M'
            )

        # Given an index value equal to last recorded value
        # When I create a new manual index record
        # Then the new index is recorded
        models.SiteDailyProduction.objects.create(
                site=self.site,
                meter=self.site.meter,
                meter_value=self.last_index().meter_value,
                date=date(2016, 1, 6),
                source='M'
            )

        # Given an index value less than last recorded value
        # When I create a new manual index record
        # Then I get a validation error
        with self.assertRaises(ValidationError):
            models.SiteDailyProduction.objects.create(
                    site=self.site,
                    meter=self.site.meter,
                    meter_value=self.last_index().meter_value - 10,
                    date=date(2016, 1, 5),
                    source='M'
                )

        # Given a date prior to last recorded index
        # When I create a new manual index record for that date
        # Then I get a validation error
        with self.assertRaises(ValidationError):
            models.SiteDailyProduction.objects.create(
                    site=self.site,
                    meter=self.site.meter,
                    meter_value=self.last_index().meter_value + 10,
                    date=date(2016, 1, 3),
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

class ManualIndexRecordTestCase(BaseSiteTestCase):
    
    def test_record_manual_index(self):
        before_count = models.SiteDailyProduction.objects.filter(site=self.site).count()
        f = forms.ManualIndexRecordForm({
                'site_id': self.site.id,
                'index': 300,
                'date': '2016-01-10'
            })
        self.assertTrue(f.is_valid())
        f.execute()
        self.assertEqual(
            models.SiteDailyProduction.objects.filter(site=self.site).count(),
            before_count+9)


class ChangeMeterTestCase(BaseSiteTestCase):
    
    def test_changer_meter(self):
        before_count = models.Meter.objects.count()
        before_meter_id = self.site.meter.id
        f = forms.ChangeMeterForm({
                'site_id': self.site.id,
                'index': 200,
                'new_index': 1000,
                'date': '2016-01-20'
            })
        self.assertTrue(f.is_valid())
        f.execute()
        self.site.refresh_from_db()
        self.assertEqual(models.Meter.objects.count(), before_count+1)
        self.assertNotEqual(before_meter_id, self.site.meter.id)
        self.assertEqual(self.site.meter.installation_index, 1000)

class ServiceTestCase(BaseSiteTestCase):

    def setUp(self):

        super(ServiceTestCase, self).setUp()
        self.t1 = self.create_record_index(300, date(2016,1,10))
        self.t2 = self.create_record_index(500, date(2016,1,20))

    def test_interpolate_index_between(self):
        """ Given two consecutive index records t1 and t2 10 days apart
            When I compute intermediate records from t1 to t2
            Then 9 (= 10 - 1) computed records are created
                 and t2 daily production is updated accordingly
        """
        before_count = models.SiteDailyProduction.objects.count()
        new_records = services.interpolate_index_between(self.t1, self.t2)
        self.assertEqual(new_records, 9)
        self.assertEqual(models.SiteDailyProduction.objects.count(), before_count+new_records)
        self.t2.refresh_from_db()
        self.assertEqual(self.t2.production, 20)
        p = models.SiteDailyProduction.objects.filter(
            site=self.t2.site,
            date__lt=self.t2.date).order_by('-date').first()
        self.assertEqual(p.source, 'C')

    def test_interpolate_index_between_nonconsecutive(self):
        """ Given two index records t0 and t2 not consecutive to each other
            When I compute intermediate records from t0 to t2
            Then I get an error
        """
        t0 = self.t1.previous()
        with self.assertRaises(AssertionError):
            services.interpolate_index_between(t0, self.t2)

    def test_compute_missing_index_values(self):
        """  Given an index record t1 9 days after the previous record
             When I compute intermediate records before t1
             Then 8 new computed records are created
        """
        before_count = models.SiteDailyProduction.objects.count()
        services.compute_missing_index_values(self.t1)
        self.assertEqual(models.SiteDailyProduction.objects.count(), before_count+8)
        self.t1.refresh_from_db()
        self.assertEqual(self.t1.production, 11)
        

class CompleteScenarioTestCase(BaseSiteTestCase):

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
        self.assertEqual(self.last_index().index, 0)

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

    def test_for_intermediate_index_records(self):

        self.assertEquals(
            models.SiteDailyProduction.objects.filter(site=self.site).count(),
            41,
            "Il doit y avoir un enregistrement par jour")

        previous = None

        for index in models.SiteDailyProduction.objects.filter(site=self.site).order_by('date'):
            if previous:
                self.assertTrue(
                    index.index >= previous.index,
                    "L'index global doit être monotone")
            previous = index

