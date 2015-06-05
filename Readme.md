#Hacker News crawler for  _who's hiring?_ thread

Only top level posts are saved, comments / replies are removed.

A file is used to store id of posts already seen, so that only new posting are added each time.

An optional email with the number of new posting once the crawling is done.

Note: SMPT server need to be set before usage.

Usage:

    python3 hn_crawler.py thread_id

It is also possible to send an email with the result of the crawl (multiple receivers are also supported)

    python3 hn_crawler.py thread_id -receivers you@email.com friend@email.com

The sender of the email can be changed (otherwise the first of the receivers will be used)

    python3 hn_crawler.py thread_id -receivers you@email.com friend@email.com -sender me@email.com

The output file is named `month_year.html`. To change that use the option

    -output name myName
