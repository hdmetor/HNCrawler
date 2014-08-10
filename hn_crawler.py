from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from datetime import datetime as dt
import smtplib

file_loc = 'news.txt'
your_email = 'something'
root = "http://news.ycombinator.com/item?id="
id = "8120070"


def cool_job(text):
    small_text = text.lower()
    locations = ['SF', 'San Francisco','bay', 'bay area' 'LA', 'Los Angeles', 'Venice', 'Santa Monica', 'nyc', 'ny']
    subjects = [
                'data', 'Big Data', 'database'
                'Mathematics', 'Math',
                'finance', 'financial',
                'game', 'videogame',
                'algo', 'algoritmic',
                'machine learning', 'learning', 'deep learning']
    languages = ['python', 'go', 'mathematica', 'c++']
    conds = [string.lower() for string in locations + subjects + languages]
    return any([cond in small_text for cond in conds ])

def create_file (list):
    with open('jobs.html', 'a') as fp:
        for id in list:
            if str(infos[id]['text']) == '':
                return
            code = '<p><a href=' + root + id  + '>'+ '<h2>' + infos[id]['user'] + '</h2>' +'</a></p>' + '<p>' + str(infos[id]['text']) + '</p>'
            fp.write(code)

def send_mail(list):
    if list == []:
        return
    sender = 'hn@gmail.com'
    receivers = ['lucabelli985@gmail.com']

    message = """From: HN bot <bot@me.com>
To: yourself <"""+ your_email +""">
Subject: New jobs form HackerNews

There are """ + str(len(list)) + """ new job posting.
"""

    #for text in list:
    #    message += '\n' + text

    try:
        smtpObj = smtplib.SMTP('smtp.rcn.com')
        smtpObj.sendmail(sender, receivers, message)
        print ("Successfully sent email")
    except SMTPException:
        print ("Error: unable to send email")



request = Request(root  + id, headers={'User-Agent': 'Mozilla/5.0'})
htmltext = urlopen(request).read()

soup = BeautifulSoup(htmltext)

posting_id = []

posts = soup.findAll('td')[4].findAll('tr')

old_postings = [line.strip() for line in open("news.txt", 'r')]

infos = {}

for post in posts[4:]:
    #print('post is ',post)
    if post.img != None and post.img.get('width') == '0':
        links = post.findAll('a')
        if links == []:
        #it is a deleted post
            pass
        #print(post)
        else:
            index = links[0].get('href').index('&')
            id = links[0].get('href')[9:index]
        #print(links)
        ##print('\n\n')
        #print(post)
        #print('\n\n')
            user = links[1].get('href')[8:]
            posting_text = post.find('span', {'class':'comment'})
            posting_id.append(id)
            infos[id] = {
                            'text' : posting_text,
                            'user' : user}


new_posting = list(set(posting_id)- set(old_postings))

if new_posting != []:
    with open(file_loc, 'a+') as fp:
        for id in new_posting:
            fp.write(id + '\n')
send_mail(new_posting)
create_file(new_posting)
