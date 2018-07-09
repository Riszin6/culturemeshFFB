#
# Contains utilities used by more than one blueprint
#

import pytz

from culturemesh.constants import BLANK_PROFILE_IMG_URL
from culturemesh.constants import USER_IMG_URL_FMT
from culturemesh.client import Client
from datetime import datetime, timezone

from utils import parse_date
from utils import get_month_abbr

utc=pytz.UTC

def get_network_title(network):
  """Returns the title of a network given a network
  JSON as a dict"""

  cur_country = network['country_cur']
  cur_region = network['region_cur']
  cur_city = network['city_cur']

  orig_country = network['country_origin']
  orig_region = network['region_origin']
  orig_city = network['city_origin']

  cur_location = ', '.join(
    [l for l in [cur_city, cur_region, cur_country] if l]
  )

  orig_location = ', '.join(
    [l for l in [orig_city, orig_region, orig_country] if l]
  )

  if network['network_class'] == '_l':

    # Language network
    language = network['language_origin']
    return "%s speakers in %s" % (language, cur_location)

  elif network['network_class'] == 'cc' \
    or network['network_class'] == 'rc' \
    or network['network_class'] == 'co':
    # City network (cc), region network (rc), or
    # country network (co).
    # Title-wise, we treat them all the same.

    return 'From %s in %s' % (orig_location, cur_location)

  else:
    return "Unknown"

def get_upcoming_events_by_user(client, user_id, count):
  """Return up to 'count' events that are in the user's
  networks and which are upcoming, sorted by how close they
  are to today"""

  upcoming_events = []
  networks = client.get_user_networks(user_id, 200)
  for network in networks:
    events = client.get_network_events(network['id'], 10)
    upcoming_events += events

  upcoming_events = [
    e for e in upcoming_events \
      if parse_date(e['event_date']) \
        >= utc.localize(datetime.now())
  ]

  upcoming_events = sorted(
    upcoming_events, key=lambda x: parse_date(x['event_date'])
  )

  return upcoming_events[:min(len(upcoming_events), count)]

def get_upcoming_events_by_network(client, network_id, count):
  """Return up to 'count' events that are in a
  network and which are upcoming, sorted by how close they
  are to today"""

  upcoming_events = client.get_network_events(network_id, 200)
  upcoming_events = [
    e for e in upcoming_events \
      if parse_date(e['event_date']) \
        >= utc.localize(datetime.now())
  ]
  upcoming_events = sorted(
    upcoming_events, key=lambda x: parse_date(x['event_date'])
  )

  return upcoming_events[:min(len(upcoming_events), count)]


def get_event_location(event):
  """Returns a string for where this event
  is taking place (i.e. New York City, New York).

  This does not return the address of an event, but
  its location.
  """
  city = event['city']
  region = event['region']
  country = event['country']

  location = ', '.join([l for l \
    in [city, region, country] if l])

  return location


def get_user_image_url(user):
  """Returns the URL of a user's profile image
  given a user JSON as a dict
  """

  if user['img_link'] is None:
    return BLANK_PROFILE_IMG
  else:
    return USER_IMG_URL_FMT % user['img_link']

def get_short_network_join_date(network):
  """Returns a short version of the user's Join
  date to a network:

  Mon day, Year
  """

  if 'join_date' not in network:
    return "unknown"
  else:
    date = parse_date(network['join_date'])
    short_month = get_month_abbr(date)
    year = date.year
    day = date.day
    return "%s %s, %s" % (str(short_month), str(day), str(year))

def get_time_ago(past_time):
  """Get a datetime object or a int() Epoch timestamp and return a
  pretty string like 'an hour ago', 'Yesterday', '3 months ago',
  'just now', etc

  Thanks: Stack Overflow id 1551382
  """

  now = datetime.now(timezone.utc)
  if type(past_time) is int:
    diff = now - datetime.fromtimestamp(past_time)
  elif isinstance(past_time, datetime):
    diff = now - past_time
  elif not past_time:
    diff = now - now
  elif isinstance(past_time, str):
    past_time = parse_date(past_time)
    diff = now - past_time
  else:
    return "unknown time ago"

  second_diff = diff.seconds
  day_diff = diff.days

  if day_diff < 0:
    return ''

  if day_diff == 0:
    if second_diff < 10:
      return "just now"
    if second_diff < 60:
      return str(second_diff) + " second(s) ago"
    if second_diff < 120:
      return "a minute ago"
    if second_diff < 3600:
      return str(round(second_diff / 60)) + " minute(s) ago"
    if second_diff < 7200:
      return "an hour ago"
    if second_diff < 86400:
      return str(round(second_diff / 3600)) + " hour(s) ago"
  if day_diff == 1:
    return "Yesterday"
  if day_diff < 7:
    return str(day_diff) + " day(s) ago"
  if day_diff < 31:
    return str(round(day_diff / 7)) + " week(s) ago"
  if day_diff < 365:
    return str(round(day_diff /30)) + " month(s) ago"
  return str(round(day_diff / 365)) + " year(s) ago"
