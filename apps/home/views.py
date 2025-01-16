from django.shortcuts import render


def home_view(request):
    context = {
        "title": "Jor Bakhair API",  # Main title
        "description": "A simple API for seamless communication!",  # Paragraph content
        "doc_url": "/api/schema/docs/",
    }
    return render(request, "index.html", context)
