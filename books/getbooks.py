import imghdr
from FB2 import FictionBook2, Author
from urllib import request
from bs4 import BeautifulSoup
from datetime import datetime
from slugify import slugify
from pathlib import Path
import re
import base64
import os
from PIL import Image
from io import BytesIO

import random
from books.models import Author, Book, Category, Keyword, Year


def open_fb2(file):
    try:
        with open(file, 'r',  encoding='utf-8') as f:
            data = f.read()
    except:
        with open(file, 'r',  encoding='cp1251') as f:
            data = f.read()
            data = data.encode('cp1251')    

    return data


    

def get_meta(bs):
    search_tags = ['date', 'first-name', 'last-name', 'book-title', 'annotation', 'book-name', 'publisher', 'city', 'year', 'isbn', 'src-url', 'lang', 'id']
    book_data = {}


    for tag in search_tags:
        if bs.find(tag):
            book_data[tag] = bs.find(tag).get_text().strip()
            
            if tag == 'publisher':
                if bs.find('publish-info'):
                    if bs.find('publish-info').find(tag):
                        book_data[tag] = bs.find('publish-info').find(tag).get_text()
                    
            if tag == 'lang':
                if bs.find('src-lang'):
                    book_data[tag] = bs.find('src-lang').get_text()                
    
    return book_data



def get_genres(genres):
    genres_from = []
    genres_to = []
    
    with open('genres_from.txt', encoding='utf-8') as file:
        for line in file:
            genres_from.append(line.rstrip())

    with open('genres_to.txt', encoding='utf-8') as file:
        for line in file:
            genres_to.append(line.rstrip())
            
    filtered_genres = []
    
    for genre in genres:
        try:
            index = genres_from.index(genre.text)
            filtered_genres.append(genres_to[index])
        except:
            filtered_genres.append(genre.text)
        
    return filtered_genres

def add_genres(genres):
    categories = []
    
    for genre in genres:
        category_slug = slugify(genre)
        if not Category.objects.filter(slug=category_slug).exists():
            new_category = Category(title=genre, slug=(category_slug))
            new_category.save()
        else:
            new_category = Category.objects.get(slug=category_slug)  
                  
        categories.append(new_category)
        
    return categories   

def add_years(years):
    return_years = []
    
    for year in years:
        year = year[-4:]
        year_slug = slugify(year)
        try:
            int(year)
        except:
            continue
        if not Year.objects.filter(slug=year_slug).exists() and not Year.objects.filter(date=int(year)).exists():
            new_year = Year(date=int(year), slug=year_slug)
            new_year.save()
        else:
            new_year = Year.objects.get(slug=year_slug)  
                  
        return_years.append(new_year)
        
    return return_years   

def add_keywords(keywords):
    keywords_list = []
    
    for keyword in keywords:
        keyword_slug = slugify(keyword)
        if not Keyword.objects.filter(slug=keyword_slug).exists():
            new_keyword = Keyword(title=keyword.title(), slug=(keyword_slug))
            new_keyword.save()
        else:
            new_keyword = Keyword.objects.get(slug=keyword_slug)  
                  
        keywords_list.append(new_keyword)
        
    return keywords_list   

def upload_cover(image, book_id):
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    cover_dir_url = '/files/books/' + str(book_id)
    cover_image = cover_dir_url + '/cover.webp'
    cover_path = str(BASE_DIR) + cover_image
    cover_dir = str(BASE_DIR) + cover_dir_url
    os.makedirs(cover_dir, exist_ok=True)
    
    source_image = Image.open(BytesIO(image))
    source_image.save(cover_path,"webp")
    
    # with open(cover_path, 'wb') as f:
    #     f.write(image)   
        
    return cover_image


def upload_image(image, book_id, image_count):
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    upload_dir_url = '/files/books/' + str(book_id)
    upload_image = upload_dir_url + '/' + str(image_count) + '.webp'
    upload_image_path = str(BASE_DIR) + upload_image
    upload_dir = str(BASE_DIR) + upload_dir_url
    os.makedirs(upload_dir, exist_ok=True)
    
    source_image = Image.open(BytesIO(image))
    source_image.save(upload_image_path, "webp")

        
    return upload_image
  
def add_meta(new_book, book_data):
    
    if 'annotation' in book_data:
        new_book.annotation = book_data['annotation']
                   
    if 'book-name' in book_data:
        new_book.book_name = book_data['book-name']
        
    if 'publisher' in book_data:
        new_book.publisher = book_data['publisher']
        
    if 'city' in book_data:
        new_book.publisher_city = book_data['city']
        
    if 'year' in book_data:
        new_book.publisher_year = book_data['year']
        
    if 'isbn' in book_data:
        new_book.isbn = book_data['isbn']
        
    if 'src-url' in book_data:
        new_book.link_url = book_data['src-url']  
        
    if 'lang' in book_data:
        new_book.lang = book_data['lang']  
            
    if 'id' in book_data:
        new_book.book_id = book_data['id']             
                
    new_book.save()
   
def replace_tags(text_body, tags):
    
    for key, value in tags.items():
        search_tags = text_body.find_all(key)  
        
        for tag in search_tags:
            tag.name = value
            
    return text_body
            

    
def add_books(files):
    
    
    duplicates = []
    added_books = []
    
    for file in files:
        bs = BeautifulSoup(file, "xml")
        
        text_body = bs.find('body')
        
        book_data = get_meta(bs)
        
        
        categories = add_genres(get_genres(bs.find_all('genre')))
        author_slug = slugify(book_data['first-name'] + ' ' + book_data['last-name'])
        
        if not book_data['first-name'] and not book_data['last-name']:
            continue
        
        if not Author.objects.filter(slug=author_slug).exists():
            new_author = Author(first_name=book_data['first-name'], last_name=book_data['last-name'], slug=(author_slug), date_published=datetime.now())
            new_author.save()
        else:
            new_author = Author.objects.get(slug=author_slug)
        
        
        if Book.objects.filter(slug=slugify(author_slug+' '+book_data['book-title'])).exists():
            duplicates.append(book_data['book-title'])
            continue
            
            
            
       
        new_book = Book(author_id=new_author.id, title=book_data['book-title'], slug=slugify(author_slug+' '+book_data['book-title']), date_published=datetime.now())
        new_book.save()
        
        
        if text_body.find_all('image'):
            images = text_body.find_all('image')
            
            image_count = 0
            
            for image in images:
                image_href = image['l:href'].replace('#', '')
                image_src = upload_image(base64.b64decode(bs.find(id=image_href).text), new_book.id, image_count)
                image.replaceWith(BeautifulSoup('<img src="'+image_src+'" />', "html.parser"))
                image_count +=1
                     
                
        tags_to_replace = {'title': 'h2', 'emphasis': 'em', 'empty-line': 'hr', 'subtitle': 'h3', 'cite': 'footer', 'text-author': 'small', 'epigraph': 'blockquote'}      
        
        full_text = replace_tags(text_body, tags_to_replace).decode_contents()
        
        if bs.find('body', {'name="notes"': 'notes'}):
            notes = bs.find('body', {'name="notes"': 'notes'})
            full_text = full_text + notes.decode_contents()
            
        new_book.full_text = full_text
        
        
        new_book.categories.set(categories)
        
        
        #adding year to books
        if book_data['date']:
            book_date = book_data['date']
            if ',' in book_date or '-' in book_date:
                book_date = re.split(r'-|, |,', book_date)
            else:
                book_date = [book_date]
                
            years = add_years(book_date)
            new_book.year.set(years)
            
                
        if bs.find('keywords'):
            keywords = add_keywords(bs.find('keywords').get_text().split(','))
            new_book.keywords.set(keywords)
        
        
        try:
            bs.find('coverpage').find('image')['l:href']
        except:
            continue 
        
        image_id = bs.find('coverpage').find('image')['l:href'].replace('#', '')
        image = bs.find(id=image_id)
        if image:
            new_book.image = upload_cover(base64.b64decode(image.text), new_book.id)

        #always last
        add_meta(new_book, book_data)
        
        added_books.append(new_book.title)
        
    return duplicates, added_books
        
    
    

    