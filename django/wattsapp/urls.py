# coding: utf-8
"""wattsapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from indexmgr import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^admin/', admin.site.urls),
    url(r'^sites/$', views.SiteListView.as_view(), name="Liste des sites"),
    url(r'^sites/create$', views.NewSiteFormView.as_view(), name=u"Création d'un nouveau site"),
    url(r'^site/(?P<pk>\d+)$', views.SiteDetailView.as_view(), name=u"Relevé de production"),
    url(r'^site/(?P<pk>\d+)/add_index$', views.ManualIndexRecordFormView.as_view(), name=u"Enregistrer un relevé manuel"),
    url(r'^site/(?P<pk>\d+)/change_meter$', views.ChangeMeterFormView.as_view(), name=u"Changer le compteur"),
]