#Hacker News crawler for  _who's hiring?_ thread

Saves only top level posts, comments / replies are removed.

Uses a file to store seen id, so that only new posting are added each time.

Sends an email with the number of new posting once the crawling is done.

Usage:

    python3 hn_crawler.py you@email.com

It is also possible to send to more than one receiver

    python3 hn_crawler.py you@email.com friend@email.com

The sender of the email can be changed (otherwise the first address will be used)

    python3 hn_crawler.py you@email.com friend@email.com -sender me@email.com

Is it also possible to add the flag

    -NoEmail

to create only the file withohut sending the email, and

    -output name

to rename the output file (defaults to `month_year.html`)


