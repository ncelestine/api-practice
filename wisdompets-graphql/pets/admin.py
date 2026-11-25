from django.contrib import admin
from .models import Owner, Pet, Vaccine

# basic admin setup so I can add and edit data from the Django admin site
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number")  # quick view columns
    search_fields = ("name", "email")                 # small quality-of-life thing


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "species", "age", "is_adopted", "owner")
    list_filter = ("species", "is_adopted")           # lets me filter pets easily
    search_fields = ("name", "breed")                 # simple search by name or breed


@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ("name", "date_given", "pet")
    list_filter = ("date_given",)                     # I can filter by date in the admin
