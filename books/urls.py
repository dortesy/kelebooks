"""book_quotes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import urls
from django.contrib.sitemaps.views import sitemap
from books.sitemaps import BookSitemap, AuthorSitemap


sitemap_books = {
    'books': BookSitemap,
}

sitemap_authors = {
    'authors': AuthorSitemap,
}
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('page/1/', views.redirect_home, name='home_redirect'),
    path('page/<int:page>/', views.IndexView.as_view(), name='index'),
    path('book/<slug:slug>/', views.BookView.as_view(), name='book'),
    path('book/<slug:slug>/page/<int:page>/', views.BookView.as_view(), name='book_page'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('keyword/<slug:slug>/', views.KeywordView.as_view(), name='keyword'),
    path('author/<slug:slug>/', views.AuthorView.as_view(), name='author'),
    path('year/<slug:slug>/', views.YearView.as_view(), name='year'),
    path('search', views.SearchResultsView.as_view(), name='search_results'),
    path('contact/', views.contact, name="contact"),
    path('privacy-policy/', views.privacy, name="privacy"),
    path('sitemap-books.xml', sitemap, {'sitemaps': sitemap_books}, name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap-authors.xml', sitemap, {'sitemaps': sitemap_authors}, name='django.contrib.sitemaps.views.sitemap'),
    path('search-filter/', views.search_filter, name="search_filter"),
    path('main-search/', views.main_search, name="main_search"),
    path('registration/', views.registration, name="registration"),
    path('account/books', views.my_books, name="my_books"),
    path('account/change-password', views.change_password, name="change_password"),
    path('account/logout', views.profile_logout, name="logout"),
    
    
    path('category/', views.categories, name="categories"),
    path('author/', views.authors, name="authors"),
    path('year/', views.years, name="years"),
]

urls.handler404 = 'books.views.view_404'