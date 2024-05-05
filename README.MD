# Scrap the Website using Scrapy

## Explanation

With this piece of Code we have scraped Website https://www.equipmentradar.com/en/directory ,

This website is created is such a beautiful way that at the first time AJAX call the backend is returning 
cookies, CSRF token and some other keys that they want in headers, payload.

So we have used Python Scrapy to complete this task.

# Setup
    > install python 3.11.x
    > install the requirements.txt file
    > at the root directory of this project run the command: scrapy crawl example -o links.jsonl
    > for now we have made this script to run only for first 5 pages, if you want to scrap all the pages
      then in file tutorial/spiders/example.py remove the 
      and self.start < 5  condition to make it run for all of the pages
    > Then you can see the output in links.jsonl file