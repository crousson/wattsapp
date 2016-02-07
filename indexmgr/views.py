# coding: utf-8

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, FormView
from . import models
from . import forms

def index(request):
    return redirect("/sites/")

class SiteListView(ListView):
    """ Liste des sites """

    template_name = "site_list.html"
    queryset = models.Site.objects.all()

class SiteDetailView(DetailView):
    """ Relevé de production d'un site """

    model = models.Site
    template_name = "site.html"

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        site = context['object']
        context['productions'] = site.sitedailyproduction_set.all().order_by('-date')
        return context

class NewSiteFormView(FormView):
    """ Formulaire de création d'un nouveau site """

    template_name = "new_site.html"
    form_class = forms.NewSiteForm

    def form_valid(self, form):
        self.site = form.execute()
        return super(NewSiteFormView, self).form_valid(form)

    def get_success_url(self):
        return "/site/%s" % self.site.id

class ManualIndexRecordFormView(FormView):
    """ Formulaire de saisie d'un relevé manuel """

    template_name = "site_add_index.html"
    form_class = forms.ManualIndexRecordForm

    def get_context_data(self, **kwargs):
        context = super(ManualIndexRecordFormView, self).get_context_data(**kwargs)
        context['form'].initial['site_id'] = self.kwargs['pk']
        context['site_id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        form.execute()
        return super(ManualIndexRecordFormView, self).form_valid(form)

    def get_success_url(self):
        return "/site/%s" % self.kwargs['pk']

class ChangeMeterFormView(FormView):
    """ Formulaire de déclaration d'un changement de compteur """

    template_name = "site_change_meter.html"
    form_class = forms.ChangeMeterForm

    def get_context_data(self, **kwargs):
        context = super(ChangeMeterFormView, self).get_context_data(**kwargs)
        context['form'].initial['site_id'] = self.kwargs['pk']
        context['site_id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        form.execute()
        return super(ChangeMeterFormView, self).form_valid(form)

    def get_success_url(self):
        return "/site/%s" % self.kwargs['pk']
