from django.contrib.sitemaps import Sitemap
from books.models import Book, Author

class BookSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    
    def items(self):
        return Book.objects.all()[0:49999]

    def lastmod(self, obj):
        return obj.date_published
    
class AuthorSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    
    def items(self):
        return Author.objects.all()[0:49999]

    def lastmod(self, obj):
        return obj.date_published

