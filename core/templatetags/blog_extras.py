from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Remplace ou ajoute des paramètres dans l'URL courante."""
    request = context.get('request')
    if not request:
        return ''
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None and value != '':
            params[key] = value
        else:
            params.pop(key, None)
    return params.urlencode()


@register.inclusion_tag('pagination.html', takes_context=True)
def pagination(context, paginator, page_obj, querystring=''):
    """Composant de pagination réutilisable."""
    return {
        'paginator': paginator,
        'page_obj': page_obj,
        'querystring': querystring,
        'request': context.get('request'),
    }
