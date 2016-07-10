#! /usr/bin/env python
# -*- coding: utf8 -*-

import os
from random import choice
from datetime import date
from calendar import monthrange
from PIL import Image

from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.is_.is_postalcodes import IS_POSTALCODES
from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings

from user_profile.settings import controller
from user_profile.utils import DisplayImageLocationFactory, DisplayImageUtils

DISPLAY_IMAGES_FOLDER = getattr(settings, "DISPLAY_IMAGES_FOLDER", "")
DISPLAY_IMAGE_SIZE = getattr(settings, "DISPLAY_IMAGE_SIZE", {'small': (50, 56) ,
                                                              'medium': (75, 84),
                                                              'large': (150,168) })
DISPLAY_IMAGE_DEFAULT = getattr(settings, "DISPLAY_IMAGE_DEFAULT", "engin-mynd.jpg")

UTILS = DisplayImageUtils(media_root = settings.MEDIA_ROOT,
                            media_url = settings.MEDIA_URL,
                            display_images_folder = DISPLAY_IMAGES_FOLDER)


class NoKennitala(Exception):
    pass

class Website(models.Model):
    url = models.URLField(_(u'Slóð'), default ='http://', unique = True)
    name = models.CharField(_(u'Nafn'), max_length=30)

    def __unicode__(self):
        return u"%s - %s" % (self.url, self.name)

    class Meta:
        verbose_name = _(u"Heimasíða")
        verbose_name_plural = _(u"Heimasíður")

class DisplayImage(models.Model):
    """

    Data invariant:
        user is the user
        display_image is the path to the image

        small, medium and large are dictionaries containing the keys 'url' and 'path'
            and each pointing to a appropriate version of display_image

    """
    user = models.ForeignKey(User, related_name="display_images")
    display_image = models.ImageField(upload_to=DISPLAY_IMAGES_FOLDER)

    def __unicode__(self):
        return u"Mynd %s af %s" % (self.display_image.name, self.user.username)

    class Meta:
        verbose_name = _(u"Mynd af nemanda")
        verbose_name_plural = _(u"Myndir af nemendum")

    def save(self):
        super(DisplayImage, self).save()
        image_file = self.display_image
        head, filename = os.path.split(image_file.name)

        image = Image.open(image_file)
        for size in DISPLAY_IMAGE_SIZE.keys():
            self._save_image(filename, image.copy(), size)

    def _save_image(self, filename, image, size):
        image.thumbnail(DISPLAY_IMAGE_SIZE[size])

        directory = os.path.join(settings.MEDIA_ROOT, UTILS.get_directory(size))

        if not os.path.exists(directory):
            os.mkdir(directory, 0777)
            os.chmod(directory, 0777) #0777 means that everyone can read, write and execute

        filepath = UTILS.get_path_to_image(size, filename)
        image.save(filepath)
        return image

    def delete(self):
        head, filename = os.path.split(self.display_image.name)
        for size in DISPLAY_IMAGE_SIZE.keys():
            try:
                os.remove(UTILS.get_path_to_image(size, filename))
            except OSError:
                #TODO: Notify
                pass
        super(DisplayImage, self).delete()

    def __getattr__(self, name):
        if name in DISPLAY_IMAGE_SIZE.keys():
            head, filename = os.path.split(self.display_image.name)
            factory = DisplayImageLocationFactory(filename = filename,
                                                    size = name,
                                                    utils = UTILS)
            return factory.get_display_image_location()
        else:
            return super(DisplayImage, self).__getattr__(name)


class UserProfile(models.Model):
    """
    UserProfile geymir nánari upplýsingar um notanda síðunnar

    Fastayrðing gagna:
        user vísar á User hlut, sem er notandi
        kennitala er kennitala notandans
        middlenames eru millinöfn notandans ef einhver eru, annars tómt

        gender er kyn notandans 'M' eða 'F'
        address er heimilsfang notandans ef það er skráð
        postalcode er Postalcode hlutur, sem stendur fyrir póstnúmer og borg

        phone er heimilissími notandans
        gsm er farsími notandans

        homepages eru þær heimasíður sem tengjast notandanum

    """
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = ( ( MALE, u'Karlkyn'),
                        ( FEMALE, u'Kvenkyn'))

    user = models.ForeignKey(User, unique=True)
    kennitala = models.CharField('Kennitala', max_length=11, blank = True)
    middlenames = models.CharField('Millinöfn', max_length = 30, blank = True)

    gender = models.CharField('Kyn', choices = GENDER_CHOICES, max_length = 1, blank = True)
    address = models.CharField('Heimilisfang', max_length=255, blank=True)
    postalcode = models.CharField('Póstnúmer',max_length=3, blank=True)

    phone = models.CharField('Sími',max_length=7, blank=True)
    gsm = models.CharField('GSM', max_length=7, blank=True)

    homepages = models.ManyToManyField(Website, verbose_name='Heimasíður', blank=True)

    class Meta:
        abstract = True
        ordering = ['user__first_name', 'middlenames', 'user__last_name' ]

    def __unicode__(self):
        return self.get_short_fullname()

    def get_absolute_url(self):
        return ('user', (), {'username' : self.user.username })
    get_absolute_url = models.permalink(get_absolute_url)

    def display_image(self, random = True):
        """
        Usage:  display_image = user.get_profile.display_image([random = True])
        Before: random is a boolean
        After:  display_image is a DisplayImage object
        """
        display_image_ids = self.user.display_images.values_list("id", flat = True)
        if display_image_ids:
            return self.user.display_images.get(id = choice(display_image_ids))
        else:
            return DisplayImage(user = User(), display_image = DISPLAY_IMAGE_DEFAULT)

    def has_kennitala(self):
        """
        Usage:  has_kennitala = user.get_profile().has_kennitala()
        After:  has_kennitala is True if and only if the user has the kennitala attribute
        """
        return self.kennitala != u''

    def get_kennitala(self):
        if len(self.kennitala) == 10:
            return "%s-%s" % (self.kennitala[0:6], self.kennitala[6:])
        else:
            return self.kennitala

    def has_homepages(self):
        """
        Usage:  has_homepages = user.get_profile().has_homepages()
        After:  has_homepages is True if and only if the user has some home pages
        """
        return self.homepages.all().count() > 0

    def get_welcome_note(self):
        """
        Notkun:     welcomeNote = user.get_profile().get_welcome_note()
        Eftir:      welcomeNote eru vingjarnleg skilaboð sem bjóða notandann velkominn
        """
        if self.is_male():
            return "Velkominn %s" % self.user.first_name
        else:
            return u"Velkomin %s" % self.user.first_name

    def get_logged_in_note(self):
        """
        Notkun:     loggedInNote = user.get_profile().get_logged_in_note()
        Eftir:      loggedInNote eru skilaboð sem segja til um hvaða notandi er innskráður
        """
        if self.is_male():
            return u"Þú ert innskráður sem %s (%s)" % (self.get_short_fullname(), self.user.username)
        else:
            return u"Þú ert innskráð sem %s (%s)" % (self.get_short_fullname(), self.user.username )

    def get_short_fullname(self):
        """
        Notkun:     shortFullname = user.get_profile().short_fullname
        Eftir:      shortFullname er fullt nafn notandans með styttum millinöfnum
        """
        if self.user.first_name != u'' and self.user.last_name != u'':
            if self.middlenames:
                #Notandinn hefur millnöfn
                mnShort = ["%s." % middlename[0] for middlename in self.middlenames.split(" ")]
                middlenames = " ".join(mnShort)
                return u"%s %s %s" % (self.user.first_name, middlenames, self.user.last_name)
            else:
                return u"%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return self.user.username
    short_fullname = property(get_short_fullname)


    def get_fullname(self):
        """
        Notkun:     fullname = user.get_profile().fullname
        Eftir:      fullname er fullt nafn notandans
        """
        if self.user.first_name != u'' and self.user.last_name != u'':
            if self.middlenames:
                return u"%s %s %s" % (self.user.first_name, self.middlenames, self.user.last_name)
            else:
                return u"%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return self.user.username
    fullname = property(get_fullname)

    def get_postalcode_and_city(self):
        """
        Notkun:     postalcodeAndCity = profile.postalcode_and_city
        Eftir:      postalcodeAndCity er strengur á forminu 'póstnúmer Borg'
        """
        postalcodes = dict(IS_POSTALCODES)
        try:
            return postalcodes[self.postalcode]
        except KeyError:
            return ''
    postalcode_and_city = property(get_postalcode_and_city)

    def get_city(self):
        """
        Usage:  city = profile.city
        After:  city is the home city of the user
        """
        return " ".join(self.postalcode_and_city.split(" ")[1:])
    city = property(get_city)


    def is_male(self):
        """
        Notkun:    is_male = user.get_profile().is_male()
        Eftir:     is_male er satt þ.þ.a.a. notandinn sé karlmaður
        """
        if self.gender == '':
            return True
        else:
            return self.gender == UserProfile.MALE

    def get_bdate(self):
        """
        Usage:  bdate = user.get_profile.get_bdate()
        After:  bdate is a date object representing the user's birthday
                if the profile has the information
                else bdate is None
        """
        if self.kennitala != "":
            kennitala = self.kennitala.replace("-", "")
            if int(kennitala[-1]) is 9:
                byear = '19' + kennitala[4:6]
            else:
                byear = '20' + kennitala[4:6]
            return date(int(byear), int(kennitala[2:4]), int(kennitala[0:2]))
        else:
            raise NoKennitala()

    def get_age_in_years(self, today = None):
        """
        Usage:  years = user.get_profile().get_age_in_years([today = None])
        After:  years is the age of the user in years
        """
        if today is None:
            today = date.today()
        return self.get_age(today)[0]

    def get_age(self, today = None):
        """
        Usage:  (years, months, days) = user.get_profile().get_age([today = None])
        Before: today defaults to date.today()
        After:  (years, months, days) is the age of the person born on date_of_birth in years, months and days
        """
        if today is None:
            today = date.today()

        try:
            bdate = self.get_bdate()
        except NoKennitala:
            return (None, None, None)
        else:
            return calculate_age(bdate, today)

    def get_age_suffix(self):
        """
        Usage:  suffix = user.get_profile().get_age_suffix()
        After:  suffix is a localized and genderized age suffix
        """
        if self.is_male():
            return _(u"gamall")
        else:
            return _(u"gömul")

    def get_closest_bday(self, today = None):
        """
        Usage:  closest_bday = user.get_profile().get_closest_bday([today = None]):
        After:  closest_bday is either the last birthday or the next birthday of the user
                depending on which birthday is closer to today
        """
        if today is None:
            today = date.today()

        try:
            birthdate = fix_leap(self.get_bdate())
        except NoKennitala:
            return None

        bday_last_year = date(today.year - 1, birthdate.month, birthdate.day)
        bday_this_year = date(today.year, birthdate.month, birthdate.day)
        bday_next_year = date(today.year + 1, birthdate.month, birthdate.day)

        tdeltas = {}
        tdeltas[abs(today - bday_last_year)] = bday_last_year
        tdeltas[abs(today - bday_this_year)] =  bday_this_year
        tdeltas[abs(today - bday_next_year)]= bday_next_year

        return tdeltas[min(tdeltas.keys())]

    def get_closest_bday_info(self, today = None):
        """
        Usage: future, months, days, prefix =

        """
        if today is None:
            today = date.today()

        closest_bday = self.get_closest_bday(today)

        if closest_bday is not None:
            if today == closest_bday:
                return (None, 0, 0, ugettext(u"á afmæli"))

            future = today < closest_bday #True if closest_bday comes after today
            if not future:
                #closest_bday er á undan today
                temp = today
                today = closest_bday
                closest_bday = temp
            #today < closest_bday

            years, months, days = calculate_age(today, closest_bday)
            if future:
                prefix = ugettext(u"á afmæli")
            else:
                prefix = ugettext(u"átti síðast afmæli")
            return (not future, months, days, prefix)
        else:
            return (None, 0, 0, '')


def fix_leap(date_of_birth):
    """
    Usage:  bday_fixed = fix_leap(bday)
    After:  If bday.day == 29 and bday.month == 2 then bday_fixed == datt(bday.year, 2, 28)
            else bday_fixed == bday
    """
    if date_of_birth.month == 2 and date_of_birth.day == 29:
        #Leap year
        date_of_birth = date(date_of_birth.year, 2, 28)
    return date_of_birth


def calculate_age(date_of_birth, today):
    """
    Usage:  (years, months, days) = calculate_age(date_of_birth, [today = None])
    Before: date_of_birth is a date object and is less than today
    After:  (years, months, days) is the age of the person born on date_of_birth in years, months and days
    """
    def days_previous_month(y, m):
        """
        Usage:  days = days_previous_month(y,m)
        Before: 1 <= m <= 12
        After:  days is the number of days in the month before m
        """
        m -= 1
        if m == 0:
            #Month was January -> The previous month is December in
            #the year before
            y -= 1
            m = 12
        _, days = monthrange(y, m)
        return days

    date_of_birth = fix_leap(date_of_birth)

    y = today.year - date_of_birth.year #0 <= y
    m = today.month - date_of_birth.month
    d = today.day - date_of_birth.day
    while m < 0 or d < 0:
        while m < 0:
            y -= 1
            m = 12 + m

        #m >= 0
        if d < 0:
            m -= 1
            days = days_previous_month(today.year, today.month)
            d = max(0, days - date_of_birth.day) + today.day
    return y, m, d

def save_user(sender, instance, created, raw, **kwargs):
    if created:
        profile = controller.get_profile_model().objects.create(user = instance)

def resize_default_image(sender, created_models, verbosity, interactive, **kwargs):
    head, filename = os.path.split(DISPLAY_IMAGE_DEFAULT)
    try:
        default_image = Image.open(DISPLAY_IMAGE_DEFAULT)
    except IOError:
        #TODO: Notify
        pass
    else:
        for size_name, size in DISPLAY_IMAGE_SIZE.iteritems():
            directory = os.path.join(settings.MEDIA_ROOT, UTILS.get_directory(size_name))
            if not os.path.exists(directory):
                os.mkdir(directory, 0777)
                os.chmod(directory, 0777) #0777 means that everyone can read, write and execute?

            path = UTILS.get_path_to_image(size_name, filename )

            if not os.path.exists(path):
                image = default_image.copy()
                image.thumbnail(size)
                image.save(path)




models.signals.post_save.connect(save_user, sender=User)
models.signals.post_syncdb.connect(resize_default_image)
