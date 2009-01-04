#! /usr/bin/env python
# -*- coding: utf8 -*-

import os

from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from user_profile.settings import controller
from user_profile.models import Website, DisplayImage
from user_profile.forms import UserProfileForm, DisplayImageForm, AdminImageFieldWidget

UserProfile = controller.get_profile_model()

def display_user_fullname(user):
    """
    Usage:     user_fullname = display_user_fullname(user)
    Post:      user_fullname is the fullname of the user
    """
    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        return u"%s %s" % (user.first_name, user.last_name)
    else:
        return profile.short_fullname
display_user_fullname.short_description = _(u"Fullt nafn")

def display_profile_attribute(attribute, short_description):
    """
    Usage:  attribute_function = display_profile_attribute(attribute)(user)
    After:  attribute_function is a function that returns the attribute of the profile_user
    """
    def display_attribute(user):
        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            return "-"
        else:
            return getattr(profile, attribute)
    display_attribute.short_description = short_description
    return display_attribute

def display_gender(user):
    """
    Usage:  gender = display_gender(user)
    After:  gender is an <img /> tag that humanly displays the gender of user
    """
    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        return ""
    else:
        gender = profile.get_gender_display()
        path = os.path.join(settings.MEDIA_URL, getattr(settings, 'MEDIA_DESIGN_URL', "images/design/"))
        return '<img src="%s%s.png" alt="%s" />' % (path, profile.gender, gender)
display_gender.allow_tags = True
display_gender.short_description = _(u"Kyn")

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 1
    max_num = 1
    fk_name = 'user'

    form = UserProfileForm

class DisplayImageInline(admin.StackedInline):
    model = DisplayImage
    extra = 1

    form = DisplayImageForm


class UserWithProfileAdmin(UserAdmin):
    """
    This will be unfinished until Django allows for inlines to be mixed in
    See ticket #4848
    """
    fieldsets = (
        (None, {'fields': ('username', )}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )   #Because the UserAdmin specifies the fieldsets
    inlines = [UserProfileInline, DisplayImageInline]
    filter_horizontal = ['groups', 'user_permissions']

    list_display = ('username',
                        'email',
                        display_profile_attribute('kennitala', _(u"Kennitala")),
                        display_user_fullname,
                        display_gender,
                        display_profile_attribute('phone', _(u"Símanúmer")),
                        display_profile_attribute('gsm', _(u"Farsímanúmer")),
                        'is_active',
                        'is_staff')
    list_filter = ('is_active','is_staff')
    list_select_related = True
    ordering = ('username', )

    search_fields = ['username', 'email','first_name','last_name',]


admin.site.register(DisplayImage)
admin.site.register(Website)
