from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def template_ipdb(context):
    import ipdb; ipdb.set_trace()