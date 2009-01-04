#! /usr/bin/env python
# -*- coding: utf8 -*-

from django.conf.urls.defaults import *

from user_profile.views import show_profile

urlpatterns = patterns('',
    url(r'^innskraning/$', 'django.contrib.auth.views.login',
            kwargs = {'template_name': 'user_profile/login.html'},  name = 'login'),
    url(r'^utskraning/$', 'django.contrib.auth.views.logout_then_login', name = 'logout'),
    url(r'^breyta-lykilordi/$', 'django.contrib.auth.views.password_change',
            kwargs = {'template_name': 'user_profile/change_password.html' }, name='change_password'),
    url(r'^lykilordinu-var-breytt/$', 'django.contrib.auth.views.password_change_done',
            kwargs = {'template_name': 'user_profile/change_password_success.html' }, name='change_password_success'),
    url(r'^(?P<username>\w+)/$', show_profile, name = 'user'),
)


