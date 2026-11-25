from django.db import models

# === Owner ===
class Owner(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=50)
    address = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.email})"


# === Pet ===
class Pet(models.Model):
    SPECIES_CHOICES = [
        ("dog", "Dog"),
        ("cat", "Cat"),
        ("bird", "Bird"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=100)
    species = models.CharField(max_length=30, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=30, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    # every pet must have an owner
    owner = models.ForeignKey("adoptions.Owner",
        related_name="pets",
        on_delete=models.CASCADE
    )

    is_adopted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.species})"


# === Vaccine ===
class Vaccine(models.Model):
    name = models.CharField(max_length=50)
    # date_given and pet are required
    date_given = models.DateField()
    pet = models.ForeignKey("adoptions.Pet",
        related_name="vaccines",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name} for {self.pet.name} on {self.date_given}"
