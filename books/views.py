from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Book

import os
import time

from google import genai


# =========================================================
# AUTHENTICATION
# =========================================================

def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not username or not email or not password:
            messages.error(request, "Please fill in all fields.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.success(
            request,
            "Account created successfully!"
        )

        return redirect("dashboard")

    return render(request, "register.html")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(request, "login.html")


def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# =========================================================
# DASHBOARD + SEARCH + FILTER
# =========================================================

@login_required
def dashboard_view(request):

    books = Book.objects.filter(
        user=request.user
    ).order_by("-id")

    search = request.GET.get(
        "search",
        ""
    ).strip()

    genre = request.GET.get(
        "genre",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    # Search by title OR author
    if search:

        books = books.filter(
            title__icontains=search
        ) | books.filter(
            author__icontains=search
        )

    # Filter by genre
    if genre:

        books = books.filter(
            genre__iexact=genre
        )

    # Filter by reading status
    if status:

        books = books.filter(
            status=status
        )

    # Get genres belonging to current user
    genres = (
        Book.objects
        .filter(user=request.user)
        .values_list("genre", flat=True)
        .distinct()
        .order_by("genre")
    )

    return render(
        request,
        "dashboard.html",
        {
            "books": books,
            "genres": genres,
            "search": search,
            "selected_genre": genre,
            "selected_status": status,
        }
    )


# =========================================================
# ADD BOOK
# =========================================================

@login_required
def add_book(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        author = request.POST.get(
            "author",
            ""
        ).strip()

        genre = request.POST.get(
            "genre",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        status = request.POST.get(
            "status",
            "Want to Read"
        )

        if not title or not author:

            messages.error(
                request,
                "Title and author are required."
            )

            return redirect("add_book")

        Book.objects.create(

            user=request.user,

            title=title,

            author=author,

            genre=genre,

            description=description,

            status=status
        )

        messages.success(
            request,
            "Book added successfully!"
        )

        return redirect("dashboard")

    return render(
        request,
        "add_book.html"
    )


# =========================================================
# EDIT BOOK
# =========================================================

@login_required
def edit_book(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id,
        user=request.user
    )

    if request.method == "POST":

        book.title = request.POST.get(
            "title",
            ""
        ).strip()

        book.author = request.POST.get(
            "author",
            ""
        ).strip()

        book.genre = request.POST.get(
            "genre",
            ""
        ).strip()

        book.description = request.POST.get(
            "description",
            ""
        ).strip()

        book.status = request.POST.get(
            "status",
            "Want to Read"
        )

        book.save()

        messages.success(
            request,
            "Book updated successfully!"
        )

        return redirect("dashboard")

    return render(
        request,
        "edit_book.html",
        {
            "book": book
        }
    )


# =========================================================
# DELETE BOOK
# =========================================================

@login_required
def delete_book(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id,
        user=request.user
    )

    if request.method == "POST":

        book.delete()

        messages.success(
            request,
            "Book deleted successfully!"
        )

    return redirect("dashboard")


# =========================================================
# AI BOOK SUMMARY — GEMINI
# =========================================================

@login_required
def generate_summary(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id,
        user=request.user
    )

    if request.method != "POST":

        return redirect("dashboard")

    # -----------------------------------------------------
    # Get API key from .env
    # -----------------------------------------------------

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        messages.error(
            request,
            "Gemini API key is not configured."
        )

        return redirect("dashboard")

    try:

        # -------------------------------------------------
        # Create Gemini client
        # -------------------------------------------------

        client = genai.Client(
            api_key=api_key
        )

        # -------------------------------------------------
        # Prompt
        # -------------------------------------------------

        prompt = f"""
Create a clear, engaging and accurate summary of this book.

Book Title: {book.title}

Author: {book.author}

Genre: {book.genre}

Description:
{book.description}

Instructions:
- Write approximately 100-150 words.
- Make the summary easy to understand.
- Do not invent specific plot details that are not provided.
- Base the summary primarily on the information given above.
"""

        # -------------------------------------------------
        # Gemini request with retry handling
        # -------------------------------------------------

        response = None

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )

                break

            except Exception as e:

                error_text = str(e)

                # Retry temporary Gemini 503 errors
                if "503" in error_text and attempt < 2:

                    time.sleep(
                        2 ** attempt
                    )

                    continue

                raise

        # -------------------------------------------------
        # Make sure Gemini returned something
        # -------------------------------------------------

        if response is None:

            messages.error(
                request,
                "Gemini did not return a response."
            )

            return redirect("dashboard")

        if not response.text:

            messages.error(
                request,
                "Gemini returned an empty summary."
            )

            return redirect("dashboard")

        # -------------------------------------------------
        # Save AI summary
        # -------------------------------------------------

        book.ai_summary = response.text

        book.save()

        messages.success(
            request,
            "AI summary generated successfully!"
        )

    except Exception as e:

        error_text = str(e)

        # Friendly message for temporary Gemini overload
        if "503" in error_text:

            messages.error(
                request,
                "Gemini is temporarily busy. Please try again in a few seconds."
            )

        # Friendly message for invalid API key
        elif "API_KEY_INVALID" in error_text:

            messages.error(
                request,
                "Gemini API key is invalid. Please check your .env file."
            )

        else:

            messages.error(
                request,
                f"AI summary generation failed: {error_text}"
            )

    return redirect("dashboard")