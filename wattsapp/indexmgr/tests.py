# coding: utf-8

from django.test import TestCase
from . import models
from . import forms

class SiteTestCase(TestCase):

    def setUp(self):
        f = forms.NewSiteForm({
                'name':'Nouveau site',
                'category': 'PV',
                'index': 0,
                'installed': '2016-01-01'
            })
        self.assertTrue(f.is_valid())
        f.execute()

    def test_create_site(self):
        """
        """
        site = models.Site.objects.first()
        self.assertEqual(site.name, 'Nouveau site')
        self.assertIsNotNone(site.meter)
        self.assertEqual(site.meter.installation_index, 0)
        self.assertIsNotNone(site.last_index())
        self.assertEqual(site.last_index().value, 0)

