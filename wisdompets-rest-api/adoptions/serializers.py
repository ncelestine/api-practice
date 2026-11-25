from rest_framework import serializers
from .models import Owner, Pet, Vaccine

# I made a small inline serializer for vaccines so I can embed them inside a Pet response.
# Keeping it light so the nested payload is easy to read in the API.
class VaccineInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = ["id", "name", "date_given"]  #skips the 'pet' field when nesting


# This is a tiny Pet serializer used inside the Owner output.
# I’m not dumping every field here to keep the owner’s payload concise.
class PetMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ["id", "name", "species", "is_adopted"]


# Full Pet serializer for top-level pet endpoints.
# When I fetch a single pet, I want to see vaccine history nested under it.
class PetSerializer(serializers.ModelSerializer):
    vaccines = VaccineInlineSerializer(many=True, read_only=True)

    class Meta:
        model = Pet
        fields = [
            "id", "name", "species", "breed", "age",
            "owner", "is_adopted", "vaccines"
        ]


# Top-level Vaccine serializer (used for vaccine detail endpoints or create/update).
class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = ["id", "name", "date_given", "pet"]


# Owner serializer shows:
# 1) the owner's basic info
# 2) a nested list of their pets (read-only)
# 3) a computed field for how many pets are still up for adoption
class OwnerSerializer(serializers.ModelSerializer):
    pets = PetMiniSerializer(many=True, read_only=True)
    available_pets_count = serializers.SerializerMethodField()

    class Meta:
        model = Owner
        fields = [
            "id", "name", "email", "phone_number", "address",
            "pets", "available_pets_count"
        ]

    # I used a method field so I can compute this count cleanly.
    def get_available_pets_count(self, owner: Owner) -> int:
        # Count only the pets for this owner that are not adopted
        return owner.pets.filter(is_adopted=False).count()
