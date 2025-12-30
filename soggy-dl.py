#! /usr/bin/env python3
# import mechanize
import brotlicffi
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

# for argv
import sys

def getPage(url):
  headers={'Accept-Encoding': 'deflate, gzip, zstd'}
  response = requests.get(url, headers=headers);
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

# like isspace(), but also counts '-' and '_' as space characters
def isseparator(my_string):
  if my_string.isspace():
    return True
  else:
    retval=True
    for c in my_string:
      if c.isspace() or c == '-' or c == '_':
        retval = retval and True
      else:
        return False
    return retval

def grab_comic(soup):
  comic=soup.find(id="comic")
  children=comic.findChildren("img", recursive=True)
  url=children[0]['src']
  if url:
    posted_on=soup.select('.post-date')[0].contents[0]
    postdate=datetime.strptime(posted_on, "%B %d, %Y")
    epoch=get_epoch(postdate)
    # number=
    filename=url.rpartition('/')[2]

    # Some of this comic's filenames don't seem to follow the
    # 'chapter number' rule (like epoch 1, chapters 217 to 222, which use
    # names like '5cNJ56B' and 'ih6WxnB'. Seems rather imgur-like...
    # Anyway, on account of this, we need to try to verify numbers from
    # page titles if isdigit() returns False on the first part of the
    # file's 'basename.'
    #
    # Confusingly, some basenames also have quirks, like epoch 0's chapter
    # 158, which has a filename of '158-1.png'. Or even stranger, like
    # epoch 0's chapter 70 ('070-e1495602194445').
    #
    # My compromise is to allow for files starting with a 1-3 digit decimal
    # number, then a dash, then anything else. If a filename does not match
    # that format, then we try to extract the chapter number from the page
    # title, and append the original filename after the chapter number
    # that we just extracted from the page title.
    
    # remove file extension
    filebasename=filename.rpartition('.')[0]

    # find first number in the page title (if any)
    title_text=soup.find('title')
    title_text=title_text
    if title_text and title_text.text.startswith('#'):
      title_chapter_number=re.search(r'\d+', str(title_text.text))
    else:
      title_chapter_number=None

    # if match found, extract the number we located
    if title_chapter_number:
      title_chapter_number=title_chapter_number.group()

    # we assume that chapter numbers are under three digits for now... might
    # need to change in future
    # if (not title_chapter_number.isdigit()) or (len(title_chapter_number) > 3):
    # prepend to filename
    if title_chapter_number:
      filename = title_chapter_number + '_' + filename
    

    filename=str(epoch).zfill(2) + '.' + filename
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
    print(url)
    document = getPage( url )
    soup = BeautifulSoup(document, 'html.parser')
    grab_comic(soup)
    url=soup.select('.comic-nav-previous')[0]['href']
    i+=1
