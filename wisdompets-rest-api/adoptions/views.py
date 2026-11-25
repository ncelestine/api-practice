from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response

from .models import Owner, Pet, Vaccine
from .serializers import (
    OwnerSerializer,
    PetSerializer,
    VaccineSerializer,
)

# ======
# Owners
# ======

class OwnerListCreateView(generics.ListCreateAPIView):
    """
    GET /api/owners/  -> list all owners (nested pets + available_pets_count)
    POST /api/owners/ -> create a new owner
    """
    queryset = Owner.objects.all().order_by("id")
    serializer_class = OwnerSerializer


class OwnerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/owners/{id}/
    PUT    /api/owners/{id}/
    DELETE /api/owners/{id}/
    """
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    lookup_field = "id"  # I want the path to use {id} instead of {pk}


# ====
# Pets
# ====

class PetListView(generics.ListAPIView):
    """
    GET /api/pets/                  -> all pets
    GET /api/pets/?is_adopted=false -> pets still up for adoption
    """
    serializer_class = PetSerializer

    def get_queryset(self):
        # I prefetch related stuff to avoid N+1 issues when listing
        qs = Pet.objects.select_related("owner").prefetch_related("vaccines").order_by("id")
        flag = self.request.query_params.get("is_adopted")
        if flag is not None:
            val = str(flag).strip().lower()
            if val in ("true", "1", "yes"):
                qs = qs.filter(is_adopted=True)
            elif val in ("false", "0", "no"):
                qs = qs.filter(is_adopted=False)
        return qs


class PetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/pets/{id}/   -> includes nested vaccines
    PUT    /api/pets/{id}/
    PATCH  /api/pets/{id}/   -> can toggle is_adopted
    DELETE /api/pets/{id}/
    """
    queryset = Pet.objects.select_related("owner").prefetch_related("vaccines")
    serializer_class = PetSerializer
    lookup_field = "id"


class OwnerPetListCreateView(generics.ListCreateAPIView):
    """
    POST /api/owners/{owner_id}/pets/ -> create a new pet under that owner
    GET  /api/owners/{owner_id}/pets/ -> (nice to have) list pets for that owner
    """
    serializer_class = PetSerializer

    def get_queryset(self):
        return Pet.objects.filter(owner_id=self.kwargs["owner_id"]).order_by("id")

    def perform_create(self, serializer):
        owner = get_object_or_404(Owner, id=self.kwargs["owner_id"])
        # I attach the owner automatically so the client doesn’t have to send owner id in the body
        serializer.save(owner=owner)


# ========
# Vaccines
# ========

class PetVaccineListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/pets/{pet_id}/vaccines/ -> list all vaccines for a pet
    POST /api/pets/{pet_id}/vaccines/ -> create a vaccine for that pet
    """
    serializer_class = VaccineSerializer

    def get_queryset(self):
        return Vaccine.objects.filter(pet_id=self.kwargs["pet_id"]).order_by("id")

    def perform_create(self, serializer):
        pet = get_object_or_404(Pet, id=self.kwargs["pet_id"])
        serializer.save(pet=pet)


class VaccineDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/vaccines/{id}/
    PUT    /api/vaccines/{id}/
    PATCH  /api/vaccines/{id}/
    DELETE /api/vaccines/{id}/
    """
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer
    lookup_field = "id"

# === API Root ===
# adoptions/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.urls import reverse

@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "owners": request.build_absolute_uri(reverse("owner-list-create")),
        "pets": request.build_absolute_uri(reverse("pet-list")),
        "templates": {
            "create_pet_for_owner": "/api/owners/<owner_id>/pets/",
            "vaccines_for_pet": "/api/pets/<pet_id>/vaccines/",
            "vaccine_detail": "/api/vaccines/<id>/"
        }
    })
