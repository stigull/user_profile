from django.contrib import admin
from django.conf import settings
from django.db.models.loading import get_model
from django.contrib.auth.models import User

class ProfileController(object):
        
    def register(self, user_admin,form):
        from user_profile.admin import UserProfileInline
        UserProfileInline.form = form
        admin.site.unregister(User)
        admin.site.register(User, user_admin) 

    def get_profile_model(self):
        appname, modelname = settings.AUTH_PROFILE_MODULE.split(".")
        return get_model(appname, modelname)

controller = ProfileController() 
