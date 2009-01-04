#! /usr/bin/env python
# -*- coding: utf8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings

from user_profile.settings import controller

def show_profile(request, username):
    user = get_object_or_404(controller.get_profile_model(), user__username = username)

    profile_base = getattr(settings, 'PROFILE_BASE', 'user_profile/user_profile_base.html')
    extends_from = getattr(settings, 'EXTENDS_FROM', 'base.html')
    context = {'profile': user, 'extends_from': extends_from }
    return render_to_response(profile_base, context, context_instance = RequestContext(request))