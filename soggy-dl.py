#! /usr/bin/env python3
# import mechanize
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

# for argv
import sys

def getPage(url):
  response = requests.get(url);
  return response.text

#################################

def add_flag(flag_dict, flag_name, flag_val):
  flag_dict.update({ str(flag_name).lower() : flag_val })

def parse_flag( arg, maybe_more_flags=True):
  if not(maybe_more_flags):
    return False
  elif arg == '--':
    return True
  elif arg.startswith("--"):
    flag = arg.rpartition('--')[2].rpartition('=')
    if flag[0] == '' and flag[1] == '':
      flag=(flag[2], '=', True)
    return flag
  return False

def get_flag(flag_dict, name, default_value=None):
  if type(flag_dict) is None:
    return default_value
  name=name.lower()
  value=flag_dict.get(name)
  if value is None:
    return default_value
  else:
    return value

#################################

def save_image(url, filename, title=None):
  if title:
    if title.startswith('#'):
      # avoid duplicate chapter number
      # note that there are comics (like "New Years 2017-2018") that do not
      # start with a '#', so we don't touch those.
      title=title.partition(' ')[2]
    filename=filename.rpartition('.')
    filebase=filename[0]
    fileext=filename[2]
    filename = filebase + ' - ' + title + '.' + fileext
  print(filename)
  image_request = requests.get(url, allow_redirects=True)
  with open(filename, 'wb') as file:
    file.write(image_request.content)

  
# this comic restarts its numbering at one. Y U DO THIS!?!
# last "original epoch" comic was February 14, 2019. First "new epoch #1" comic
# (not putting it past them to do it again) was February 21, 2019.
def get_epoch(date):
  if(date < datetime(2019, 2, 20 ,0, 0)):
    return 0
  else:
    return 1

def grab_comic(soup):
  comic=soup.find(id="comic")
  children=comic.findChildren("img", recursive=True)
  url=children[0]['src']
  if url:
    posted_on=soup.select('.post-date')[0].contents[0]
    postdate=datetime.strptime(posted_on, "%B %d, %Y")
    epoch=get_epoch(postdate)
    # number=
    filename=str(epoch).zfill(2) + '.' + url.rpartition('/')[2]
    title=soup.title.string.rpartition(' – SoggyCardboard')[0]
    save_image(url, filename, title)
    
  
##################################
i = 1
# process flags
flags = { }
while i < len(sys.argv):
  maybe_more_flags = True
  parseval = parse_flag( sys.argv[i], maybe_more_flags)
  if maybe_more_flags == True:
    if parseval == True:
      maybe_more_flags = False
    elif type(parseval) is tuple:
      if parseval[0] == '' and parseval[1] == '':
        parseval = (parseval[2], '=', True)
      add_flag(flags, parseval[0], parseval[2])
  i+=1

i=1
urls=[ ]
while i < len(sys.argv):
  if sys.argv[i].startswith("--") and sys.argv[i] != "--":
    i+=1
  elif sys.argv[i] == "--":
    i+=1
    break
  else:
    break
  # i contains first url to process now

j=len(sys.argv) - 1
# push onto our stack (list) in reverse order so that it operates efficiently
# starting with the first provided url on the command line at the top
while j >= i:
  urls.append(sys.argv[j])
  j-=1

many=int(get_flag(flags, 'many', '1'))
print("Going to traverse up to " + str(many) + " pages.")
print("URLs: " + str(urls))

while len(urls) > 0:
  url=urls.pop()
  i=0
  while i < many and url:
    document = getPage( url )
    soup = BeautifulSoup(document, 'html.parser')
    grab_comic(soup)
    url=soup.select('.comic-nav-previous')[0]['href']
    i+=1
