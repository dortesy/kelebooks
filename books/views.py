from unicodedata import category
from urllib import response
from django.shortcuts import render
from django.views import generic
from books.models import Author, Book, Category, Year, Reader, Keyword
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.validators import validate_email
from django.conf import settings
from django.http import Http404, JsonResponse
from django.db.models import Q
from slugify import slugify 
from .forms import ContactForm
from django.core.mail import EmailMessage
from django.core import serializers
from django.shortcuts import redirect
import json
import time
import re
from django.contrib.sites.models import Site
from django import forms
from django.contrib.auth.models import User
import requests
from django.contrib.auth import authenticate, login, password_validation, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import HttpResponseRedirect


class IndexView(generic.ListView):
    template_name = 'default/index.html'
    paginate_by = 21
    model = Book
    ordering = ['-date_published']
    context_object_name = 'content' 

    #print(Category.book_set.through.objects.all())
    

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        new_content = {"popular": Book.objects.popular(), "years": Year.objects.order_by('-date').all(), 'authors': Author.objects.order_by('views').all(), 'index': True}
        
        
        context = dict(list(context.items()) + list(new_content.items()))
     
        # paginator = Paginator(Book.objects.all(), 15)  # Show 25 contacts per page.
        # page_number = self.request.GET.get('page')
        # page_obj = paginator.get_page(page_number)
        # content['books'] = page_obj
        
        return context
    
def make_redirect(book, scheme, page_number):
    current_site = Site.objects.get_current()
    return str(scheme) + '://' + str(current_site.domain) + '/book/' + book.slug + '/?page=' + str(page_number) + '#read-book'

class BookView(generic.DetailView):
    model = Book
    template_name = "default/book.html"

 
    def get(self, *args, **kwargs):
        
        try:
            book_object = Book.objects.get(**kwargs)
        except:
            return HttpResponseRedirect("/")
        
        
        self.object = self.get_object()
        
        
        context = self.get_context_data(object=self.object)
        
        
        
        if self.request.user.is_authenticated:
            current_user = Reader.objects.get_or_create(user=self.request.user)[0]
         
            if current_user.books and str(book_object.id) in current_user.books and int(self.request.GET.get('page', 1)) <= 1:
                redirect_page = make_redirect(book_object, self.request.scheme, current_user.books[str(book_object.id)])
                return redirect(redirect_page, perm=False)

        else:
            if 'book' in self.request.session:
                if str(book_object.id) in self.request.session['book'] and int(self.request.GET.get('page', 1)) <= 1:
                    redirect_page = make_redirect(book_object, self.request.scheme, self.request.session['book'][str(book_object.id)])
                    return redirect(redirect_page, perm=False)
        
        return self.render_to_response(context)
        
    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        full_text = self.object.full_text
        
        if self.object.full_text.count('<poem>') > 20:
            PaginatedInstance = re.split('(\</poem>)', full_text)
            paginator = Paginator(PaginatedInstance, 10)
        else:
            PaginatedInstance = re.split('(\</p>)', full_text)
            paginator = Paginator(PaginatedInstance, 50)
        # test = re.finditer(r'(^(?:\S+\s+\n?){1,160}.*?<\/p>)', full_text, re.MULTILINE)
        # for a in test:
        #     print(a)
        
        
        page = self.request.GET.get('page', 1)

        if int(page) > 1:
            if self.request.user.is_authenticated:
                current_user = Reader.objects.get_or_create(user=self.request.user)[0]
                if current_user.books:
                    json_data = current_user.books
                    json_data[str(context['object'].id)] = page
                else:
                    json_data = { str(context['object'].id): page}
                    current_user.books = json_data
                    
                current_user.save()    
            else:
                if 'book' not in self.request.session:
                    self.request.session['book'] = {}
                    
                self.request.session['book'][str(context['object'].id)] = page
                
        if int(page) == 1 and self.request.GET:
            if self.request.user.is_authenticated:
                current_user = Reader.objects.get_or_create(user=self.request.user)[0]
                json_data = current_user.books
                del json_data[str(context['object'].id)]
                current_user.save()
            else:
                del self.request.session['book'][str(context['object'].id)]
                

            
            
        try:
            Paginated = paginator.page(page)
        except PageNotAnInteger:
            Paginated = paginator.page(1)
        except EmptyPage:
            Paginated = paginator.page(paginator.num_pages)

        context['text'] = Paginated
        context['single'] = True
        
        return context
        # paginator = Paginator(self.object.book_set.all(), 20)  # Show 25 contacts per page.
        
    
        
    # def get_paginator_quotes(self):
    #     queryset = self.object.quote_set.all().order_by('-views')
    #     paginator = Paginator(queryset, 51) #paginate_by
    #     page = self.request.GET.get('page')
    #     quotes = paginator.get_page(page)
    #     return quotes



class YearView(generic.DetailView):
    model = Year
    template_name = "default/year.html"

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.object.book_set.all(), 15)  # Show 25 contacts per page.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['books'] = page_obj
        return context   
    
    
class KeywordView(generic.DetailView):
    model = Keyword
    template_name = "default/keyword.html"
    
    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.object.book_set.all(), 15)  # Show 25 contacts per page.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['books'] = page_obj
        return context   


class CategoryView(generic.DetailView):
    model = Category
    template_name = "default/category.html"

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.object.book_set.all(), 20)  # Show 25 contacts per page.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['books'] = page_obj
        return context   
    
class AuthorView(generic.DetailView):
    model = Author
    template_name = "default/author.html"
    
    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.object.book_set.all(), 20)  # Show 25 contacts per page.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['books'] = page_obj
        return context    
    
# class QuoteView(generic.DetailView):
#     model = Quote
#     template_name = "default/quote.html"

#     def get_context_data(self, **kwargs):
#         context = super(QuoteView, self).get_context_data(**kwargs)
#         next_quotes = Quote.objects.filter(id__gt=context['object'].id, id__lt=context['object'].id + 6)
#         context['next_quotes'] = next_quotes
#         return context

        
#     def get_object(self):
#         obj = super().get_object()
#         obj.views += 1
#         obj.save()
#         return obj   

# def _filter(filters):
#     filters = []
#     for k, v in n.items():
#         if v:
#             filters.append(Q(**{k: v}))
#     return filters    

class SearchResultsView(generic.ListView):
    model = Book
    template_name = 'default/search_result.html'
    context_object_name = 'content'
 
    
    def get_queryset(self): # новый
        filters = {}
        selected = {}
        if self.request.GET.get('category'):
            category_id = self.request.GET.get('category')
            category = Category.objects.get(pk=category_id)
            filters['categories'] = category
            
            selected['category'] = category.title
            
        if self.request.GET.get('author'):
            author_id = self.request.GET.get('author')
            author = Author.objects.get(pk=author_id)
            filters['author'] = author
            
            selected['author'] = author.first_name + ' ' + author.last_name
            
        if self.request.GET.get('year'):
            year_id = self.request.GET.get('year')
            year = Year.objects.get(pk=year_id)  
            filters['year'] = year
            
            selected['year'] = year.date
        
            
        books = Book.objects.filter(*[Q(**{k: v}) for k, v in filters.items() if v]).all()
        
        
        paginator = Paginator(books, 20)  # Show 25 contacts per page.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        books = page_obj
        
        content = {"books": books, "years": Year.objects.order_by('-date').all(), 'authors': Author.objects.order_by('views').all(), "selected": selected }

        return content
        #return Book.objects.filter(name__icontains='Boston')
    
    
# def search(request, slug):
#     print(slug)
#     query = slug.replace('-', ' ')
#     print(query)
#     print('sasdasdsa')
#     paginator = Paginator(Book.objects.filter(title__icontains=query).all(), 50)  # Show 25 contacts per page.
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     books = page_obj

#     if not books:
#         raise Http404("Такой книги не существует")
#     return render(request, 'default/search_result.html', {'books': books, 'query': query})

def redirect_home(request):
    response = redirect('/')
    return response


def contact(request):
    context = dict(
       form=ContactForm(),
    )


    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ContactForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:

            message = form.cleaned_data['message']

            if form.cleaned_data['your_name']:
                message += '<br>Sender: ' + str(form.cleaned_data['your_name'])

            if form.cleaned_data['email']:
                message += '<br>Email Sender: ' + str(form.cleaned_data['email'])

            msg = EmailMessage(
                form.cleaned_data['subject'],
                message,
                'wallpapersmob@gmail.com',
                ['wallpapersmob@gmail.com'],
            )

            msg.content_subtype = "html"
            msg.send()

            context['response'] = 'Thank you! Your message was successfully sent'

            return render(request, 'default/pages/contact.html', context)

    return render(request, 'default/pages/contact.html', context)


def search_filter(request):
    if request.method != 'POST':
        return redirect('/')
    
    selects = json.loads(request.body)['values']
    
    cat = ''
    author = ''
    year = ''
    
    if 'category' in selects:
        category_id = int(selects['category'])
        cat = Category.objects.get(pk=category_id)
        
    if 'author' in selects:
        author_id = int(selects['author'])
        author = Author.objects.get(pk=author_id)
        
    if 'year' in selects:
        year_id = int(selects['year'])
        year = Year.objects.get(pk=year_id)
      
    if cat and not author and not year:
        books = Book.objects.filter(categories=cat).all()
        
    if not cat and author and not year:  
        books = Book.objects.filter(author=author).all()
        
    if not cat and not author and year:  
        books = Book.objects.filter(year=year).all()          
              
    if cat and author and not year:
        books = Book.objects.filter(categories=cat, author=author).all()
        
    if cat and not author and year:  
        books = Book.objects.filter(categories=cat, year=year).all()       
 
    if not cat and author and year:  
        books = Book.objects.filter(author=author, year=year).all()              
        
    if cat and author and year:  
        books = Book.objects.filter(categories=cat, author=author, year=year).all()     
    
    
    authors = Author.objects.filter(book__in=books).distinct().values_list('pk', flat=True)
    years = Year.objects.filter(book__in=books).distinct().values_list('pk', flat=True)
    cats = Category.objects.filter(book__in=books).distinct().values_list('pk', flat=True)


    print(list(authors))  
    # authors = serializers.serialize('json', authors)
    # years = serializers.serialize('json', years)
    # cats = serializers.serialize('json', cats)
    
    
    return JsonResponse(
        {
            'category': list(cats),
            'author': list(authors),
            'year': list(years),
        }, 
        safe=False)


def main_search(request):
    if request.method != 'POST':
        return redirect('/')
    query = json.loads(request.body)['query']
    
    if query:
    
        results = list(Book.objects.filter(slug__icontains=slugify(query)).values('slug', 'title', 'author__first_name', 'author__last_name'))[:5]
        return JsonResponse(
            {
                'books': results
            }, 
            safe=False)

        
    
    
    
def check_recaptcha(response): 
    url = 'https://www.google.com/recaptcha/api/siteverify'
    
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': response
    }
    
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=values)
    result = r.json()
    
    if result['success']:
        return True
    
    return False
    
    
def registration(request):
    
    
    if request.method == 'POST':
        email = json.loads(request.body)['email']
        password = json.loads(request.body)['password']
        response = json.loads(request.body)['google']
        registration = json.loads(request.body)['reg']
        
        if not check_recaptcha(response):
            return JsonResponse({'error_text': 'Вы не прошли проверку на робота!'}, safe=False, status=406)
            
        if not registration:
            
            try:
                user = User.objects.get(username=email)
            except:
                user = False
            
            if user:
                if not user.check_password(password):
                    return JsonResponse({'error_text': 'Вы ввели неверный пароль'}, safe=False, status=406)
            else:
                return JsonResponse({'error_text': 'Такого пользователя не существует'}, safe=False, status=406)
            
            user_auth = authenticate(request, username=email, password=password)
            if user_auth is not None:
                login(request, user_auth)
                return JsonResponse({'Login': 'Вы успешно вошли'}, safe=False)
            else:
                return JsonResponse({'error_text': 'Неизвестная ошибка!'}, safe=False, status=406)
                
        try: 
            validate_email(email)
        except forms.ValidationError:   
            return JsonResponse({'error_text': 'Вы ввели неверный email'}, safe=False, status=406)
            
        try: 
            password_validation.validate_password(password) 
        except forms.ValidationError as error:
            return JsonResponse({'error_text': error.messages[0]}, safe=False, status=406)
           
        
           
        if User.objects.filter(email=email):
            return JsonResponse({'error_text': 'Данный email уже зарегистрирован '}, safe=False, status=406)
        
        new_user = User.objects.create_user(email, email, password)
        
        user_auth = authenticate(request, username=email, password=password)
        
        if user_auth is not None:
            login(request, user_auth)
                
        return JsonResponse({'email': 'email'}, safe=False)
    else:
        return redirect('/')
        
                

def privacy(request):
    return render(request, 'default/pages/privacy.html')

def error404(request, exception):
    return render(request, 'default/pages/404.html', status=404)

def my_books(request):
    if request.user.is_authenticated:
        books = {}
        pages = {}
        if hasattr(request.user, 'reader'):
            books = Book.objects.filter(pk__in=request.user.reader.books.keys())
            pages = request.user.reader.books.values()
            
        return render(request, 'default/account/my_books.html', {'my_books': zip(books, pages)})
    
    else:
        return redirect('/')

def change_password(request):
    if request.user.is_authenticated:
            if request.method == 'POST':
                form = PasswordChangeForm(request.user, request.POST)
                if form.is_valid():
                    user = form.save()
                    update_session_auth_hash(request, user)  # Important!
                    messages.success(request, 'Ваш пароль был успешно изменен!')
                    return redirect('change_password')
                else:
                    messages.error(request, 'Исправьте ошибки укзанные сверху, и попробуйте заново')
            else:
                form = PasswordChangeForm(request.user)
            return render(request, 'default/account/change_password.html', {
                'form': form
            })
    else:
        return redirect('/')
    
def profile_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/')
    else:
        return redirect('/')
    
    
def categories(request):
    categories = Category.objects.order_by('views').all()
    return render(request, 'default/pages/categories.html', {'categories': categories})

def authors(request):
    authors = Author.objects.order_by('-views').all()
    return render(request, 'default/pages/authors.html', {'authors': authors})

def years(request):
    years = Year.objects.order_by('-date').all()
    return render(request, 'default/pages/years.html', {'years': years})

def view_404(request, exception=None):
    return HttpResponseRedirect("/")