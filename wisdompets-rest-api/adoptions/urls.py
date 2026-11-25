from django.urls import path
from .views import (
    OwnerListCreateView, OwnerDetailView,
    PetListView, PetDetailView, OwnerPetListCreateView,
    PetVaccineListCreateView, VaccineDetailView,
    api_root,
)

urlpatterns = [
    path("", api_root, name="api-root"),

    # Owners
    path("owners/", OwnerListCreateView.as_view(), name="owner-list-create"),
    path("owners/<int:id>/", OwnerDetailView.as_view(), name="owner-detail"),

    # Pets
    path("pets/", PetListView.as_view(), name="pet-list"),
    path("pets/<int:id>/", PetDetailView.as_view(), name="pet-detail"),

    # Create/list pets for a specific owner
    path("owners/<int:owner_id>/pets/", OwnerPetListCreateView.as_view(), name="owner-pet-list-create"),

    # Vaccines (per-pet and by id)
    path("pets/<int:pet_id>/vaccines/", PetVaccineListCreateView.as_view(), name="pet-vaccine-list-create"),
    path("vaccines/<int:id>/", VaccineDetailView.as_view(), name="vaccine-detail"),
]

