from api.models import CommentLabel
from django import template

register = template.Library()

@register.filter(name='is_type_checked')
def is_type_checked(comment_label, type):
    field = CommentLabel.type_mapping[type]

    if getattr(comment_label, field):
        """Removes all values of arg from the given string"""
        return "checked"
    else:
        return ""
