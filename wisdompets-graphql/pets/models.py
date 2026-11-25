from django.db import models

# Owner model represents the person who is responsible for one or more pets
class Owner(models.Model):
    name = models.CharField(max_length=100)         # basic name field
    email = models.EmailField()                     # using EmailField to keep emails valid
    phone_number = models.CharField(max_length=20)  # keeping this as text to allow dashes etc.
    address = models.CharField(max_length=255)      # simple text field for home address

    def __str__(self):
        # makes the admin and shell output a bit easier to read
        return self.name


# Pet model represents an animal that can be adopted
class Pet(models.Model):
    # simple choices for the species type (could be expanded later if needed)
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"

    SPECIES_CHOICES = [
        (DOG, "Dog"),
        (CAT, "Cat"),
        (OTHER, "Other"),
    ]

    name = models.CharField(max_length=100)               # pet's name
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)  # restricts to a few options
    breed = models.CharField(max_length=100, blank=True)  # some pets may not have a known breed
    age = models.IntegerField()                           # storing age as a simple number
    is_adopted = models.BooleanField(default=False)       # False means still available for adoption

    # relationships
    owner = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        related_name="pets",     # lets me do owner.pets.all() in queries
    )

    def __str__(self):
        # show both name and species to quickly identify the pet
        return f"{self.name} ({self.species})"


# Vaccine model represents a vaccine that was given to a specific pet
class Vaccine(models.Model):
    name = models.CharField(max_length=100)    # name of the vaccine
    date_given = models.DateField()           # when it was given

    # each vaccine record belongs to exactly one pet
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name="vaccines",  # allows pet.vaccines.all() later on
    )

    def __str__(self):
        # just a small helper for admin and shell
        return f"{self.name} for {self.pet.name}"
