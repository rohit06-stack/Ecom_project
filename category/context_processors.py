from .models import Category

def menu_links(request):
    Links = Category.objects.all()
    return dict(links=Links)