from django import template

register = template.Library()


@register.filter
def pkr(value):
    """Format a PKR integer with thousands separators: 150000 -> '150,000'."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    return f'{value:,}'


@register.filter
def pkr_compact(value):
    """Format a PKR integer compactly: 150000 -> '150k', 1200000 -> '1.2m'."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    if value >= 1_000_000:
        text = f'{value / 1_000_000:.1f}'.rstrip('0').rstrip('.')
        return f'{text}m'
    if value >= 1_000:
        return f'{value // 1_000}k'
    return str(value)
