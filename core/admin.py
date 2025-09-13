from django.contrib import admin
from .models import Estate, Block, Apartment, Amenity, Furnishing, UserProfile

admin.site.register(Estate)
admin.site.register(Block)
admin.site.register(Apartment)
admin.site.register(Amenity)
admin.site.register(Furnishing)
admin.site.register(UserProfile)