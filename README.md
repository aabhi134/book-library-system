# Book Library System

A Django-based Book Library System developed for the Codex Club Coordinator Selection.

## Features

The project implements all five required features:

1. Authentication
   - User registration
   - Login
   - Logout

2. Add / Edit / Delete Books
   - Add books to the personal library
   - Edit existing books
   - Delete books

3. Search & Filter
   - Search books by title or author
   - Filter by genre
   - Filter by reading status

4. AI Book Summary
   - Generates an AI-powered summary using Google Gemini

5. Reading Status
   - To Read
   - Reading
   - Completed

## Technology Stack

- Python
- Django
- SQLite
- HTML
- CSS
- Google Gemini API

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd book-library-system

Create and activate a virtual environment: .\venv\Scripts\Activate.ps1

Install dependencies: pip install -r requirements.txt

Create a .env file and add: GEMINI_API_KEY=your_api_key_here

Run migrations: python manage.py migrate

Start the development server: python manage.py runserver
