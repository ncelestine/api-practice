from django.contrib import admin
from .models import Owner, Pet, Vaccine

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone_number")
    search_fields = ("name", "email")

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    # TEMP: removed is_adopted from list_display and list_filter to allow migration to run
    list_display = ("id", "name", "species", "breed", "age", "owner")
    list_filter = ("species", "owner")
    search_fields = ("name", "breed", "owner__name")

@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date_given", "pet")
    list_filter = ("date_given", "name")
    search_fields = ("name", "pet__name")
