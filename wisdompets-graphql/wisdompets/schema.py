import graphene

# importing the query and mutation classes from the pets app
from pets.schema import Query as PetsQuery
from pets.schema import Mutation as PetsMutation


# this query class combines the test field and the real pets queries
class Query(PetsQuery, graphene.ObjectType):
    # keeping a simple test field so I can quickly confirm the API is alive
    hello = graphene.String(description="Basic test field to confirm GraphQL is working")

    def resolve_hello(root, info):
        return "Wisdom Pets GraphQL API is working"


# this mutation class exposes all the CRUD operations for owners, pets, and vaccines
class Mutation(PetsMutation, graphene.ObjectType):
    # I am not adding anything extra here yet, but it is ready if I need it later
    pass


# auto_camelcase=False means my field names stay the same as in Python (snake_case)
schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
