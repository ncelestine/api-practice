# API Programming Practice

Four projects from my API programming studies: consuming a third-party REST API, building REST APIs with Django REST Framework, and building the same data API in GraphQL. For my larger API projects, see **Volunteer Service API** (JWT and object-level permissions) and **Django JWT Auth API** (authentication, roles and testing).

| Folder | Tech | What it shows |
|---|---|---|
| [`github-analyzer`](github-analyzer) | Python, `requests`, GitHub REST API | Calling an external API with retries, timeouts and error handling |
| [`drf-books-api`](drf-books-api) | Django REST Framework | The same CRUD API written two ways: function-based and class-based views |
| [`wisdompets-rest-api`](wisdompets-rest-api) | Django REST Framework | A pet adoption API with nested resources, filtering and computed fields |
| [`wisdompets-graphql`](wisdompets-graphql) | Django, Graphene | The pet adoption data as a GraphQL API with queries and mutations |

Install everything once from the repository root:

```bash
python -m venv venv
# Windows: venv\Scripts\activate    macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

---

## GitHub Analyzer

A command-line tool that fetches a user's public repositories from the GitHub REST API (`/users/{username}/repos`) and reports:

- every repository name
- total repositories, total stars and average stars
- a breakdown of repositories by language
- the **top 3** most-starred and the **top 5** most recently updated repositories

It retries failed requests up to 3 times, uses a 10-second timeout, and handles rate limits (403) and unknown users. A GitHub token is optional; when set, it's read from an environment variable rather than stored in the code.

```bash
python github-analyzer/github_analyzer.py
# Optional, for a higher rate limit:  set GITHUB_TOKEN=<your token>  (Windows)  /  export GITHUB_TOKEN=...
```

## DRF Books API

A book catalogue CRUD API written twice for comparison:

| Style | Endpoints |
|---|---|
| Class-based (DRF generics) | `GET/POST /api/books/`, `GET/PUT/PATCH/DELETE /api/books/<id>/` |
| Function-based (`@api_view`) | `GET/POST /api/books-fbv/`, `GET/PUT/DELETE /api/books-fbv/<id>/` |

```bash
cd drf-books-api
python manage.py migrate
python manage.py runserver
```

## WisdomPets REST API

A pet adoption API with **owners**, **pets** and **vaccines**:

- Nested serializers: owners include their pets, and pets include their vaccines
- A computed `available_pets_count` field on each owner
- Filtering with `/api/pets/?is_adopted=false`
- Nested routes such as `POST /api/owners/<id>/pets/` and `GET /api/pets/<id>/vaccines/`
- `select_related` / `prefetch_related` to avoid the N+1 query problem

```bash
cd wisdompets-rest-api
python manage.py migrate
python manage.py loaddata sample_data
python manage.py runserver      # browse http://127.0.0.1:8000/api/
```

## WisdomPets GraphQL API

The same data model exposed through **GraphQL** with Graphene-Django:

- Queries: `all_owners`, `owner(id)`, `all_pets`, `pets_for_adoption`, `pet(id)`, `vaccines_for_pet(pet_id)`, `vaccine(id)`
- Mutations: create, update and delete owners and pets, plus `mark_pet_adopted`
- A custom resolver for `available_pets_count`
- Clear error messages with `GraphQLError`

```bash
cd wisdompets-graphql
python manage.py migrate
python manage.py loaddata sample_data
python manage.py runserver      # GraphiQL at http://127.0.0.1:8000/graphql/
```

Example query:

```graphql
{
  all_owners {
    name
    available_pets_count
    pets { name is_adopted vaccines { name date_given } }
  }
}
```

All sample data is fictional. The WisdomPets data model follows a common Django course example.
