def app_language(request):
    return {
        "app_language": getattr(request, "app_language", "cs"),
    }
