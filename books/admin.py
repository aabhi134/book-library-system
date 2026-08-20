from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "genre",
        "status",
        "user",
        "created_at",
    )

    list_filter = ("status", "genre")

    search_fields = ("title", "author", "genre")
