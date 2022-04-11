from gameboard.models import Player
from django.template.defaulttags import register

def get_user_info(request):
    """
    A helper function which uses the user information in the request to get the Player object (which also contains the
    user object).

    :param request: A html request with user data (specifically username)
    :return: None if no user found, otherwise the Player object.
    """
    try:
        user = request.user
        if user.is_anonymous:
            return None
        else:
            return Player.objects.filter(user__username=user.username).first()
    except KeyError:
        return None


def get_user_info_by_username(username):
    """
    A helper function which uses the user information in the request to get the Player object (which also contains the
    user object).

    :param username: A html request with user data (specifically username)
    :return: None if no user found, otherwise the Player object.
    """
    try:
        return Player.objects.filter(user__username=username).first()
    except KeyError:
        return None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
