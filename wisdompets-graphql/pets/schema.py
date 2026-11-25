import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError  # lets me return clean errors in the API

from .models import Owner, Pet, Vaccine



# This type maps the Vaccine model to a GraphQL type
class VaccineType(DjangoObjectType):
    class Meta:
        model = Vaccine
        # listing fields I want to expose in the API
        fields = ("id", "name", "date_given", "pet")


# This type maps the Pet model to a GraphQL type
class PetType(DjangoObjectType):
    class Meta:
        model = Pet
        # including vaccines so I can see them when I query a pet
        fields = ("id", "name", "species", "breed", "age", "is_adopted", "owner", "vaccines")


# This type maps the Owner model to a GraphQL type and adds a custom field
class OwnerType(DjangoObjectType):
    # custom field that is not stored in the database
    available_pets_count = graphene.Int(
        description="Number of this owner's pets that are still available for adoption"
    )

    class Meta:
        model = Owner
        # exposing the pets and the custom field on the owner type
        fields = ("id", "name", "email", "phone_number", "address", "pets", "available_pets_count")

    # resolver for the custom field: only count pets where is_adopted is False
    def resolve_available_pets_count(self, info):
        return self.pets.filter(is_adopted=False).count()


# This class holds all of the read-only queries for the Wisdom Pets API
class Query(graphene.ObjectType):
    # Owners
    all_owners = graphene.List(
        OwnerType,
        description="Retrieve all owners, including their pets"
    )
    owner = graphene.Field(
        OwnerType,
        id=graphene.Int(required=True),
        description="Retrieve a single owner by ID, including pets and available_pets_count",
    )

    # Pets
    all_pets = graphene.List(
        PetType,
        description="Retrieve all pets"
    )
    pets_for_adoption = graphene.List(
        PetType,
        description="Retrieve pets that are up for adoption (is_adopted = False)"
    )
    pet = graphene.Field(
        PetType,
        id=graphene.Int(required=True),
        description="Retrieve a single pet by ID, including vaccination details",
    )

    # Vaccines
    vaccines_for_pet = graphene.List(
        VaccineType,
        pet_id=graphene.Int(required=True),
        description="Retrieve all vaccines for a specific pet",
    )
    vaccine = graphene.Field(
        VaccineType,
        id=graphene.Int(required=True),
        description="Retrieve details of a specific vaccine by ID",
    )

    # ---- Resolvers ----

    # returns all owners
    def resolve_all_owners(root, info):
        return Owner.objects.all()

    # returns a single owner or None if it does not exist
    def resolve_owner(root, info, id):
        return Owner.objects.filter(id=id).first()

    # returns every pet in the system
    def resolve_all_pets(root, info):
        return Pet.objects.all()

    # only return pets that are still available for adoption
    def resolve_pets_for_adoption(root, info):
        return Pet.objects.filter(is_adopted=False)

    # returns a single pet or None if it does not exist
    def resolve_pet(root, info, id):
        # using select_related to avoid extra queries for owner
        return Pet.objects.select_related("owner").filter(id=id).first()

    # returns all vaccines for a given pet id
    def resolve_vaccines_for_pet(root, info, pet_id):
        return Vaccine.objects.filter(pet_id=pet_id)

    # returns a single vaccine by id or None if it does not exist
    def resolve_vaccine(root, info, id):
        return Vaccine.objects.filter(id=id).first()

# ---- Owner mutations ----

class CreateOwner(graphene.Mutation):
    # what this mutation returns
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        address = graphene.String(required=True)

    owner = graphene.Field(OwnerType)

    def mutate(self, info, name, email, phone_number, address):
        # basic create for the Owner model
        owner = Owner.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            address=address,
        )
        return CreateOwner(owner=owner)


class UpdateOwner(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        email = graphene.String()
        phone_number = graphene.String()
        address = graphene.String()

    owner = graphene.Field(OwnerType)

    def mutate(self, info, id, name=None, email=None, phone_number=None, address=None):
        owner = Owner.objects.filter(id=id).first()
        if not owner:
            # simple error so the client knows the id was wrong
            raise GraphQLError("Owner not found")

        # only update fields that were actually provided
        if name is not None:
            owner.name = name
        if email is not None:
            owner.email = email
        if phone_number is not None:
            owner.phone_number = phone_number
        if address is not None:
            owner.address = address

        owner.save()
        return UpdateOwner(owner=owner)


class DeleteOwner(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        owner = Owner.objects.filter(id=id).first()
        if not owner:
            raise GraphQLError("Owner not found")

        owner.delete()
        # pets and vaccines will also be cleaned up because of on_delete=models.CASCADE
        return DeleteOwner(ok=True)


# ---- Pet mutations ----

class CreatePet(graphene.Mutation):
    class Arguments:
        owner_id = graphene.Int(required=True)
        name = graphene.String(required=True)
        species = graphene.String(required=True)
        breed = graphene.String()
        age = graphene.Int(required=True)

    pet = graphene.Field(PetType)

    def mutate(self, info, owner_id, name, species, age, breed=None):
        owner = Owner.objects.filter(id=owner_id).first()
        if not owner:
            raise GraphQLError("Owner not found for the given owner_id")

        pet = Pet.objects.create(
            owner=owner,
            name=name,
            species=species,
            age=age,
            breed=breed or "",
        )
        return CreatePet(pet=pet)


class UpdatePet(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        species = graphene.String()
        breed = graphene.String()
        age = graphene.Int()
        is_adopted = graphene.Boolean()

    pet = graphene.Field(PetType)

    def mutate(self, info, id, name=None, species=None, breed=None, age=None, is_adopted=None):
        pet = Pet.objects.filter(id=id).first()
        if not pet:
            raise GraphQLError("Pet not found")

        if name is not None:
            pet.name = name
        if species is not None:
            pet.species = species
        if breed is not None:
            pet.breed = breed
        if age is not None:
            pet.age = age
        if is_adopted is not None:
            pet.is_adopted = is_adopted

        pet.save()
        return UpdatePet(pet=pet)


class DeletePet(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        pet = Pet.objects.filter(id=id).first()
        if not pet:
            raise GraphQLError("Pet not found")

        pet.delete()
        return DeletePet(ok=True)


class MarkPetAdopted(graphene.Mutation):
    # small helper mutation to flip is_adopted to True
    class Arguments:
        id = graphene.Int(required=True)

    pet = graphene.Field(PetType)

    def mutate(self, info, id):
        pet = Pet.objects.filter(id=id).first()
        if not pet:
            raise GraphQLError("Pet not found")

        pet.is_adopted = True
        pet.save()
        return MarkPetAdopted(pet=pet)


# ---- Vaccine mutations ----

class CreateVaccine(graphene.Mutation):
    class Arguments:
        pet_id = graphene.Int(required=True)
        name = graphene.String(required=True)
        date_given = graphene.Date(required=True)  # expects YYYY-MM-DD

    vaccine = graphene.Field(VaccineType)

    def mutate(self, info, pet_id, name, date_given):
        # validation: only create vaccines for real pets
        pet = Pet.objects.filter(id=pet_id).first()
        if not pet:
            raise GraphQLError("Cannot create vaccine: pet does not exist")

        vaccine = Vaccine.objects.create(
            pet=pet,
            name=name,
            date_given=date_given,
        )
        return CreateVaccine(vaccine=vaccine)


class UpdateVaccine(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        date_given = graphene.Date()

    vaccine = graphene.Field(VaccineType)

    def mutate(self, info, id, name=None, date_given=None):
        vaccine = Vaccine.objects.filter(id=id).first()
        if not vaccine:
            raise GraphQLError("Vaccine not found")

        if name is not None:
            vaccine.name = name
        if date_given is not None:
            vaccine.date_given = date_given

        vaccine.save()
        return UpdateVaccine(vaccine=vaccine)


class DeleteVaccine(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        vaccine = Vaccine.objects.filter(id=id).first()
        if not vaccine:
            raise GraphQLError("Vaccine not found")

        vaccine.delete()
        return DeleteVaccine(ok=True)


# This class collects all of the mutations so the main schema can use them
class Mutation(graphene.ObjectType):
    # owner mutations
    create_owner = CreateOwner.Field()
    update_owner = UpdateOwner.Field()
    delete_owner = DeleteOwner.Field()

    # pet mutations
    create_pet = CreatePet.Field()
    update_pet = UpdatePet.Field()
    delete_pet = DeletePet.Field()
    mark_pet_adopted = MarkPetAdopted.Field()

    # vaccine mutations
    create_vaccine = CreateVaccine.Field()
    update_vaccine = UpdateVaccine.Field()
    delete_vaccine = DeleteVaccine.Field()
