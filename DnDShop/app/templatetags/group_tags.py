# app/templatetags/group_tags.py
from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Возвращает True, если пользователь принадлежит к группе с именем group_name.
    Безопасен для анонимных пользователей.
    """
    if not user or not hasattr(user, 'groups'):
        return False
    return user.groups.filter(name=group_name).exists()
