from django import template

from fencers.i18n import tr_text

register = template.Library()


@register.simple_tag(takes_context=True)
def tr(context, text):
    request = context.get("request")
    lang = getattr(request, "app_language", "cs") if request else "cs"
    return tr_text(text, lang)
