from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.urls import re_path
from django.template.response import TemplateResponse
from django.contrib.sites.models import Site
from books.models import Author, Book, Category, Year
from .forms import GetBooksForm
from .getbooks import add_books
from django.contrib.auth.models import User

class MyAdminSite(admin.AdminSite):
    site_title = 'Читать книги онлайн'
    site_header = 'Книги онлайн'

    def get_books_view(self, request):
        if not request.user.has_perm('auth.view_user'):
            raise PermissionDenied()
        form = GetBooksForm()
        context = dict(
            self.each_context(request),
            form=form,
        )

        if request.method == 'POST':
            
            # create a form instance and populate it with data from the request:
            form = GetBooksForm(request.POST, request.FILES)
            files = request.FILES.getlist('files')
            # check whether it 's valid:
            if form.is_valid():
                #keywords = form.cleaned_data['keywords'].splitlines()
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                duplicates, added_books = add_books(files)
                context.update({'duplicates': duplicates, 'added_books': added_books})
                return TemplateResponse(request, "admin/get_books.html", context)

        return TemplateResponse(request, "admin/get_books.html", context)

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        app_list += [
            {
                "name": "Добавить книги",
                "app_label": "get-books",
                "models": [
                    {
                        "name": "Добавить книги",
                        "object_name": "getbooks",
                        "admin_url": "get-books",
                        "view_only": False,

                    }
                ],
            }
        ]
        return app_list

    def get_urls(self):

        urls = super(MyAdminSite, self).get_urls()
        custom_urls = [
             re_path('get-books', self.get_books_view, name="get_books"),
        ]
        return custom_urls +  urls 
    
    
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'views', 'author')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'slug']

    def author(self,obj):
        return obj.author.first_name + obj.author.last_name

class YearAdmin(admin.ModelAdmin):
    list_display = ('date', 'slug', 'views')
    search_fields = ['date', 'slug']


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('author', 'slug', 'views')
    search_fields = ['first_name', 'last_name', 'slug']

    def author(self,obj):
        return obj.first_name +' ' + obj.last_name
    
    
        
mysite = MyAdminSite()
admin.site = mysite
    
# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Category)
admin.site.register(Site)
admin.site.register(Year, YearAdmin)
admin.site.register(User)