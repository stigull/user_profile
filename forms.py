#! /usr/bin/env python
# -*- coding: utf8 -*-

import os
from PIL import Image

import django.forms as forms
from django.contrib import admin
from django.contrib.localflavor.is_.forms import ISIdNumberField, ISPhoneNumberField, ISPostalCodeSelect
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.conf import settings

from user_profile.models import UserProfile
from user_profile.models import DISPLAY_IMAGE_SIZE

WIDTH, HEIGHT = DISPLAY_IMAGE_SIZE['large']

RATIO_TEXT = _(u"Hlutfallið milli hliða verður að vera %(width)d/%(height)d = %(ratio).2f" % {'width': WIDTH, 
                                                                                    'height': HEIGHT, 
                                                                                    'ratio': float(WIDTH) / HEIGHT})

class AdminImageFieldWidget(admin.widgets.AdminFileWidget):

    def render(self, name, value, attrs=None):
        img_html = ''
        if value:
            head, filename = os.path.split(str(value))
            path = os.path.join(settings.MEDIA_URL, head, "small", filename)
            img_html = '<img src="%s" alt="%s"/>' % (path, value)
        return mark_safe("%s%s" % (img_html, super(AdminImageFieldWidget, self).render(name, value, attrs)))


class DisplayImageForm(forms.ModelForm):
    display_image = forms.ImageField(label = _(u"Mynd af nemanda"), 
                                        help_text = RATIO_TEXT, widget = AdminImageFieldWidget)
      
    def clean_display_image(self):
        try:
            file = self.cleaned_data['display_image']
        except KeyError:
            pass
        else:
            image = Image.open(file)
            if WIDTH * image.size[1] !=  HEIGHT * image.size[0]:
                raise forms.ValidationError(RATIO_TEXT)
        return file
                
 
class UserProfileForm(forms.ModelForm):
    kennitala = ISIdNumberField(label = 'Kennitala', required = False)
    postalcode = forms.CharField(label = 'Póstnúmer og borg', 
                                    required = False, 
                                    widget = ISPostalCodeSelect())
    phone = ISPhoneNumberField(label = 'Símanúmer', required = False)
    gsm = ISPhoneNumberField(label = 'Farsímanúmer', required = False)
    
    class Meta:
        model = UserProfile
        
        