from .models import Category, Book


def categories_render(request):
    return_object = {
         'categories': Category.objects.exclude(title__iregex=r'^[a-zA-Z]').order_by('title').all()
    }
    

        
    return return_object
    
    