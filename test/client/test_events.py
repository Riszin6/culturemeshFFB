#
# Tests client/events.py
# 

from nose.tools import assert_true
from culturemesh.client import Client

def test_get_event():
  """
  Tests we can get a single event.
  """
  c = Client(mock=True)

  event1 = c.get_event(2)
  event2 = c.get_event(0)

  print(event1)

  assert_true(event1 is not None and \
     event1['title'] == "Reverse-engineered 6thgeneration neural-net")
  assert_true(event2 == None)

def test_event_attendance():
  """
  Tests the basic event
  attendance API call. 
  """
  c = Client(mock=True)

  list1 = c.get_event_registration_list(1)
  list2 = c.get_event_registration_list(2)

  print(list1)

  assert_true(list1 and list1[0]['id_guest'] == 1)
  assert_true(len(list2) == 2)