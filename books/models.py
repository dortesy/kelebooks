from django.db import models, transaction
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.models import User
from star_ratings.models import Rating
import os
# Create your models here.

class PopularManager(models.Manager):
    
    @transaction.atomic
    def popular(self):
        return self.all().order_by('-views')[:12]
 

        
    

def get_image_path(self, filename):
    return os.path.join('files/covers/', filename)

class Author(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    views = models.IntegerField(default=0)
    date_published = models.DateTimeField('Publishing date')
    
    def get_absolute_url(self):
        return reverse('author', kwargs={'slug':self.slug})
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name
           
class Category(models.Model):
    title = models.CharField(max_length=350)   
    slug = models.SlugField(max_length=350, unique=True)       
    views = models.IntegerField(default=0)
    def __str__(self):
        return self.title
         
         
class Keyword(models.Model):
    title = models.CharField(max_length=350)   
    slug = models.SlugField(max_length=350, unique=True)      
    views = models.IntegerField(default=0) 
    def __str__(self):
        return self.title

class Year(models.Model):
    date = models.IntegerField(unique=True)   
    slug = models.SlugField(max_length=350, unique=True)      
    views = models.IntegerField(default=0) 
    
    def __str__(self):
        return str(self.date)

class Book(models.Model):
    title = models.CharField(max_length=350)
    author = models.ForeignKey(Author, on_delete=models.CASCADE) 
    date_published = models.DateTimeField('Publishing date')
    year = models.ManyToManyField(Year, blank=True)
    annotation = models.TextField(blank=True)
    slug = models.SlugField(max_length=350, unique=True)
    views = models.IntegerField(default=0)
    book_name = models.CharField(max_length=350, blank=True)
    publisher = models.CharField(max_length=350, blank=True)
    publisher_city = models.CharField(max_length=150, blank=True)
    publisher_year = models.CharField(max_length=150, blank=True)
    isbn = models.CharField(max_length=350, blank=True)
    link_url = models.CharField(max_length=350, blank=True)
    lang = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to=get_image_path, height_field=None, width_field=None, max_length=100, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    keywords = models.ManyToManyField(Keyword, blank=True)
    objects = PopularManager()
    full_text = models.TextField(blank=True)
    book_id = models.CharField(max_length=350, default=0, blank=True)
    ratings = GenericRelation(Rating, related_query_name='books')
    
    def get_absolute_url(self):
        return reverse('book', kwargs={'slug':self.slug})
    
    def image_url(self):
        return  '/' + str(self.src)
    
    def __str__(self):
        return self.title



class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    books = models.JSONField(null=True, blank=True)
    
    
# class Quote(models.Model):
#     text = models.TextField()
#     views = models.IntegerField(default=0)
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     relative_id = models.IntegerField(default=0, blank=True)
#     date_published = models.DateTimeField('Publishing date')
#     objects = PopularManager()
    
#     def get_absolute_url(self):
#         return reverse('quote', kwargs={'pk':self.pk})
    
#     def __str__(self):
#         return self.text[0:150] + '...'