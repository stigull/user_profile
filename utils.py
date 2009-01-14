#! /usr/bin/env python
# -*- coding: utf8 -*-
import os

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from emailer.forms import EmailWrappedObjectForm, ObjectToSendWrapper

class DisplayImageLocation(object):
    def __init__(self, url, path):
        self.url = url
        self.path = path

class DisplayImageLocationFactory(object):
    def __init__(self, filename, size, utils):
        self.filename = filename
        self.size = size
        self.utils = utils

    def get_display_image_location(self):
        return DisplayImageLocation(url = self.utils.get_url_to_image(self.size, self.filename),
                                   path = self.utils.get_path_to_image(self.size, self.filename))

class DisplayImageUtils(object):
    def __init__(self, media_root, media_url, display_images_folder):
        self.media_root = media_root
        self.media_url = media_url
        self.display_images_folder = display_images_folder

    def get_directory(self, size):
        """
        Gets the display images directory without the media url or root

        Usage:  directory = utils.get_directory(size)
        Pre:    size is the specified size
        Post:   directory is the display images directory without the media url or root
        """
        return os.path.join(self.display_images_folder, size)

    def get_path_to_image(self, size, filename):
        """
        Returns a path on the filesystem to a appropriately sized image with the specified filename
        """
        return os.path.join(self.media_root, self.get_directory(size), filename)

    def get_url_to_image(self, size, filename):
        """
        Returns a url to a appropriately sized image with filename
        """
        return os.path.join(self.media_url, self.get_directory(size), filename)

class ResetPasswordWrapper(ObjectToSendWrapper):

    def get_email_subject(self):
        return u"Nýtt lykilorð - New password"

    def get_email_template(self):
        return u"user_profile/emails/reset_password.txt"

    def get_email_context(self):
        return {'user': self.instance, 'new_password': self.new_password }

    def get_email_recipients(self):
        return [self.instance.email,]

    def process_pre_email(self):
        self.new_password = User.objects.make_random_password()
        self.instance.set_password(self.new_password)
        self.instance.save()

def reset_password_link(user):
    form = EmailWrappedObjectForm(initial = {'appname': 'auth',
                                                'modelname': 'User',
                                                'instance_id': user.id,
                                                'wrapped_appname': 'user_profile.utils',
                                                'wrapped_classname': 'ResetPasswordWrapper'})
    return form.render(u'Frumstilla lykilorð',u'Frumstilla lykilorð')
reset_password_link.short_description = _(u"Frumstilla lykilorð")
reset_password_link.allow_tags = True

def reset_password(user):
    """
    Usage:  reset_password(user)
    After:  A new random password has been generated for user and is now his new password
            If user has an email the new password has been sent to him
            else the new password has been sent to the administrators
    """
    password = User.objects.make_random_password()
    user.set_password(password)

    if user.first_name != '':
        first_name = user.first_name
    else:
        first_name = user.username
    message = render_to_string('emails/new_password_email.html', {'user': user,
                                                                    'first_name': first_name,
                                                                    'password' : password })

    subject = u"Nýtt lykilorð - New password"
    if user.email is not None and user.email != '':
        try:
            user.email_user(subject = subject,
                        message = message)
        except:
            #TODO: Logga eða láta einhvern vita
            pass
    else:
        for name, email in settings.ADMINS:
            send_mail(subject = subject,
                    message = message,
                    from_email = settings.DEFAULT_FROM_EMAIL)

