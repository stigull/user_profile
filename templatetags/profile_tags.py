#! /usr/bin/env python
# -*- coding: utf8 -*-

from django import template
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

register = template.Library()

def login_or_logout_form(context, next):
    """
    Usage:  {% login_or_logout_form next %}
    After:  Depending on whether the browsing user is logged in or not a login or logout
            form has been displayed
            After a successful login the user is redirected to the url next
    """
    user = context['user']
    request = context['request']
    login_url = reverse('login')

    if request.path == login_url:
        return {'on_login_page': True }

    if next == login_url:
        next = reverse('index')

    if not user.is_authenticated():
        form = AuthenticationForm(auto_id = "login-form-%s")
        form.fields['username'].widget.attrs['tabindex'] = 1
        form.fields['password'].widget.attrs['tabindex'] = 2
        form.id = "login-form"
        return {'login' : True, 'form' : form , 'next': next}
    else:
        return {'login': False }
register.inclusion_tag('user_profile/login_logout.html', takes_context = True)(login_or_logout_form)

def user_area(context):
    """
    Usage: {% user_area %}
    After:  Displays the user area if the user is logged in
    """
    user = context['user']
    return {'user': user }
register.inclusion_tag('user_profile/user_area.html', takes_context = True)(user_area)




