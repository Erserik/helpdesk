from django import template

register = template.Library()

@register.filter(name='has_role')
def has_role(user, roles):
    """Check if the user's role is in the provided list of roles."""
    roles_list = roles.split(',')
    return user.role in roles_list
