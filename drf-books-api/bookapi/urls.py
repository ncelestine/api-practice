from django.urls import path
from . import views
from .views import BookList, BookDetail

urlpatterns = [
    # Final (CBV) endpoints
    path("books/", BookList.as_view(), name="book-list"),
    path("books/<int:pk>/", BookDetail.as_view(), name="book-detail"),

    # FBV endpoints (kept for comparison with the class-based versions)
    path("books-fbv/", views.book_list, name="book-list-fbv"),
    path("books-fbv/<int:pk>/", views.book_detail, name="book-detail-fbv"),
]
