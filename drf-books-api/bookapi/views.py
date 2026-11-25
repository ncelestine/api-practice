from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics

from .models import Book
from .serializers import BookSerializer

# -----------------------------
# Function-Based Views (FBV)
# -----------------------------

@api_view(["GET", "POST"])
def book_list(request):
    """List all books or create a new one."""
    if request.method == "GET":
        qs = Book.objects.all().order_by("-created_at")
        serializer = BookSerializer(qs, many=True)
        return Response(serializer.data)

    # POST
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def book_detail(request, pk: int):
    """Retrieve, update, or delete a single book."""
    book = get_object_or_404(Book, pk=pk)

    if request.method == "GET":
        return Response(BookSerializer(book).data)

    if request.method == "PUT":
        serializer = BookSerializer(book, data=request.data)  # full update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)  # 200 OK
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    book.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------
# Class-Based Views (CBV)
# -----------------------------

class BookList(generics.ListCreateAPIView):
    """List + create using DRF generics."""
    queryset = Book.objects.all().order_by("-created_at")
    serializer_class = BookSerializer


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve + update + delete using DRF generics."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
