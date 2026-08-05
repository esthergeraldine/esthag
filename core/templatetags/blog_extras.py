from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Remplace ou ajoute des paramètres dans l'URL courante."""
    request = context['request']
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None and value != '':
            params[key] = value
        else:
            params.pop(key, None)
    return params.urlencode()
