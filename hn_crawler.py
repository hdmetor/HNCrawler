from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from datetime import datetime as dt
import smtplib
import argparse
import datetime
import re

parser = argparse.ArgumentParser()
parser.add_argument("id",help="hackernews id of the post")
parser.add_argument("-receivers",help="email address where updates should be sent to", nargs='+')
parser.add_argument("-sender",help="sender of the email\ndefaults to the first of the receivers")
parser.add_argument("-output",help="name of the output file\n defaults to month+year", default='')


args = parser.parse_args()

# local changes
smtpServer = ""
old_ids = "old_ids.txt"

day = str(datetime.datetime.now().day)
month = str(datetime.datetime.now().month)
year = str(datetime.datetime.now().year)


if args.output != '':
    path = args.output + '.html'
else:
    path = month + '_' + year + '.html'

root = "http://news.ycombinator.com/item?id="
id = args.id

def whole_word(w):
    "returns an object if the word is present, None otherwise"
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def cool_job(text):
    """Given the text of the post, it flags it as interesting or not"""
    # Note: Please use regex, instead of regular 'string in text' python syntax
    small_text = text.lower()
    locations = ['SF', 'San Francisco', 'bay', 'bay area', 'nyc', 'ny']
    subjects = [
                'data', 'Big Data',
                'Mathematics', 'Math',
                'finance', 'financial',
                'game', 'videogame',
                'algo', 'algoritmic',
                'machine learning', 'learning', 'deep learning', 'deeplearning']
    languages = ['python', 'go', 'mathematica', 'c']
    conds = [string.lower() for string in locations + subjects + languages]
    return any([whole_word(cond)(small_text) for cond in conds])

def create_file (ids):
    """Given a list of posting id, write to the file a formatted version of the post"""
    with open(path, 'a') as fp:
        title = '<h1>Date added: '+ day + '/ ' + month + '</h1>'
        fp.write(title)
        for id in ids:
            text = str(infos[id]['text'])
            if not cool_job(text):
                continue
            if text == '':
                return
            code = '<p><a href=' + root + id  + '>'+ '<h2>' + infos[id]['user'] + '</h2>' +'</a></p>' + '<p>' + str(infos[id]['text']) + '</p>'
            fp.write(code)

def send_mail(posts):
    """Given the posts, it send sends an email message to notify about the number of posts.
    Options for the sender / receiver(s) are specified by the command line
    """
    if posts == []:
        return
    receivers = args.receivers
    if args.sender:
        sender = args.sender
    else:
        sender = receivers[0]

    message = """From: HN bot <bot@me.com>
To: yourself <""" + sender + """>
Subject: New jobs form HackerNews

There are """ + str(len(posts)) + """ new job posting.
"""

    try:
        smtpObj = smtplib.SMTP(smtpServer)
        smtpObj.sendmail(sender, receivers, message)
        print ("Successfully sent email")
    except SMTPException:
        print ("Error: unable to send email")



request = Request(root  + id, headers={'User-Agent': 'Mozilla/5.0'})
htmltext = urlopen(request).read()

soup = BeautifulSoup(htmltext, "html.parser")

posting_id = []

posts = soup.findAll('td')[4].findAll('tr')

# This jobs were already considered
try:
    old_postings = [line.strip() for line in open(old_ids, 'r')]
except FileNotFoundError:
    old_postings = []

infos = {}

for post in posts[4:]:
    # select a top post only
    if post.img != None and post.img.get('width') == '0':
        links = post.findAll('a')
        if links == []:
        #it is a deleted post
            pass
        else:
            index = links[0].get('href').index('&')
            id = links[0].get('href')[9:index]
            posting_text = post.find('span', {'class':'comment'})
            if cool_job(str(posting_text)):
                user = links[1].get('href')[8:]
                posting_id.append(id)
                infos[id] = {
                            'text' : posting_text,
                            'user' : user}


new_posting = list(set(posting_id) - set(old_postings))

if args.receivers:
    send_mail(new_posting)
create_file(new_posting)
print("Found ", len(new_posting), " jobs!")
# archive ids for future use
if new_posting != []:
    with open(old_ids, 'a+') as fp:
        for id in new_posting:
            fp.write(id + '\n')
