from django.shortcuts import render
from django.views.generic import ListView, DetailView, FormView
from . import models
from . import forms 

class SiteListView(ListView):

    template_name = "site_list.html"
    queryset = models.Site.objects.all()

class SiteDetailView(DetailView):

    model = models.Site

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        site = context['object']
        context['productions'] = site.sitedailyproduction_set
        context['indices'] = site.siteindex_set
        return context

class NewSiteFormView(FormView):

    template_name = "new_site.html"
    form_class = forms.NewSiteForm
    success_url = "/sites/"

    def form_valid(self, form):
        form.execute()
        return super(NewSiteFormView, self).form_valid(form)

class ManualIndexRecordFormView(FormView):

    template_name = ""
    form_class = forms.ManualIndexRecordForm
    success_url = ""

class ChangeMeterFormView(FormView):

    template_name = ""
    form_class = forms.ChangeMeterForm
    success_url = ""
