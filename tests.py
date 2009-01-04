#! /usr/bin/env python
# -*- coding: utf8 -*-

import unittest
from datetime import date

from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse

from mock import Mock 

from user_profile.models import calculate_age, DisplayImage
from user_profile.utils import DisplayImageUtils, DisplayImageLocation, DisplayImageLocationFactory

class TestCalculateAge(unittest.TestCase):
    def test_get_age(self):
        today = date(2008,10,3)
        self.assertEqual(calculate_age(date(1987,10,22), today), (20, 11, 11))
        self.assertEqual(calculate_age(date(1988,2,29), today), (20, 7, 5))
        

class TestDisplayImageUtils(unittest.TestCase):
    def setUp(self):
        self.utils = DisplayImageUtils(media_root = '/var/www/stigull/skrar/',
                                    media_url = '/skrar',
                                    display_images_folder = 'myndir/simaskra/')

    def test_get_directory(self):
        self.assertEqual(self.utils.get_directory('medium'), 'myndir/simaskra/medium')
                                    
    def test_get_path_to_image(self):
        self.assertEqual(self.utils.get_path_to_image('medium', 'jthb2.jpg'),
                            '/var/www/stigull/skrar/myndir/simaskra/medium/jthb2.jpg')

    def test_get_url_to_image(self):
        self.assertEqual(self.utils.get_url_to_image('medium', 'jthb2.jpg'),
                            '/skrar/myndir/simaskra/medium/jthb2.jpg')
        
class DisplayImageLocationTestCase(unittest.TestCase):
    def setUp(self):                
        self.SIZES = ['small', 'medium', 'large']
        utils = DisplayImageUtils(media_root = '/var/www/stigull/skrar/',
                            media_url = '/skrar',
                            display_images_folder = 'myndir/simaskra/')
                            
        self.factories = []                    
        for size in self.SIZES:
            self.factories.append(DisplayImageLocationFactory(filename = "jthb2.jpg", 
                                                                size = size, 
                                                                utils = utils))
   
    def test_get_display_image_location(self):
        expected = [{   'url': '/skrar/myndir/simaskra/small/jthb2.jpg',
                        'path': '/var/www/stigull/skrar/myndir/simaskra/small/jthb2.jpg'},
                    {   'url': '/skrar/myndir/simaskra/medium/jthb2.jpg',
                        'path': '/var/www/stigull/skrar/myndir/simaskra/medium/jthb2.jpg'},
                    {   'url': '/skrar/myndir/simaskra/large/jthb2.jpg',
                        'path': '/var/www/stigull/skrar/myndir/simaskra/large/jthb2.jpg'}
                        ]
        expected_locations = []
        for location in expected:
            expected_locations.append(DisplayImageLocation(url = location['url'],
                                                            path = location['path']))
        
        for factory, expected_location in zip(self.factories, expected_locations):   
            location = factory.get_display_image_location()
            self.assertEqual(location.url, expected_location.url)
            self.assertEqual(location.path, expected_location.path)


class DisplayImageTestCase(unittest.TestCase):
    
    def setUp(self):
        user = User(username = 'jthb2')
        utils = DisplayImageUtils(media_root = '/var/www/stigull/skrar/',
                            media_url = '/skrar',
                            display_images_folder = 'myndir/simaskra/')
        self.display_image = DisplayImage(user = user, 
                    display_image = "/var/www/stigull/skrar/myndir/simaskra/jthb2.jpg")
        
    def test_get_display_image_small(self):
        location = self.display_image.small
        expected_location = DisplayImageLocation(url = '/skrar/myndir/simaskra/small/jthb2.jpg',
                                                        path = '/var/www/stigull/skrar/myndir/simaskra/small/jthb2.jpg')
        self.assertEqual(location.url, expected_location.url)
        self.assertEqual(location.path, expected_location.path)
        