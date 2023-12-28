from django import template

register = template.Library()

def page(dict, key_name):
    return dict[str(key_name)]

page = register.filter('page', page)