"""
Helpers

Helpers are functions which help our other queries to perform properly.
"""
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.core.cache import cache


def clear_cache(group):
    """
    Clears all the cached item for a group, forcing a recalculation on the next use.

    :param group: The group to clear cache data for.
    :return: None
    """
    cache.delete('trophies-{}'.format(group.id))


def get_cache(group, name):
    """
    Gets a cache value for a group.

    :param group: The group to get cache data for
    :param name: The keyword used for the cache data.
    :return: Depends on what was cached, but defaults to None
    """
    if name == 'trophies':
        return cache.get('trophies-{}'.format(group.id))
    else:
        return None


def get_heavy_game_list():
    """
    Simply returns a list of pre-defined "heavy" games which take more to win, or last longer than normal games.
    TODO make this a parameter to a group? Or a flag on a game?

    :return:
    """
    return ['Scythe', 'Twilight Imperium', 'Eclipse', 'Court of the Dead', 'Twilight Struggle']


def average_ranks(rounds, return_zero_as_null=False):
    if len(rounds) == 0:
        return 'null' if return_zero_as_null else None
    else:
        return round(sum(rounds) / len(rounds), 1)


def generate_dates(date_string="all"):
    """
    Generates a pair of datetime objects, which represent a time range to search the database over. There are a few
    options:
        - A year, eg. "2020"
        - A month in the format "[month short name]-[year]", eg. "jan-2018" or "Jul-2020"
        - Within the last 30 days, "recent"
        - All time ranges, "all"
    The default option is "all".

    :param date_string: The string to parse that holds the intended time range.
    :return: A pair of datetime objects bracketing the range of interest.
    """
    # Attempt to convert this to an int
    try:
        date_int = int(date_string)
    except ValueError:
        date_int = None

    if date_int:
        # This is a year, so return the range of the year
        return datetime.strptime("{}-1-1".format(date_string), '%Y-%m-%d'), datetime.strptime("{}-12-31".format(date_string), '%Y-%m-%d')
    elif "-" in date_string:
        # This is a month in a year
        return datetime.strptime(date_string, '%b-%Y'), datetime.strptime(date_string, '%b-%Y') + relativedelta(months=1)
    elif date_string == "recent":
        # Just the last 30 days
        return datetime.now() - timedelta(days=30), datetime.now()
    elif date_string == "recent_year":
        # Just the last 30 days
        return datetime.now() - timedelta(days=366), datetime.now()
    else: # date_string == "all":
        # Get time since start of the epoch
        return datetime.strptime("1970-1-1", '%Y-%m-%d'), datetime.now()
