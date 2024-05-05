import re

import scrapy
from scrapy import Request
from scrapy.http import HtmlResponse


class ExampleSpider(scrapy.Spider):
    name = "example"
    start_urls = ["https://www.equipmentradar.com/en/directory"]

    def __init__(self):

        self.start = 0
        self.pvuuid = ""
        self.csrf_token = ""
        self.cookie_value = ""

    def parse(self, response, *args):

        # get all of the rows
        rows = response.css("div.list-group-item")

        for row in rows:
            # return the extracted urls
            yield {"url": "https://www.equipmentradar.com" + row.css("a.dcard-title::attr(href)").get()}

        # get all the script tags
        script_tags, extracted_value = response.xpath('//script'), None
        if args:
            # if it's a recursive call
            extracted_value, next_btn = args[0], args[1]
            self.start += 1
        else:
            # first time extraction code
            # to get the cookies, pvuuid and other details to call the next pages
            self.start += 1
            cookies = response.headers.getlist('Set-Cookie')

            cookie_name, cookie_value = None, None
            for cookie in cookies:
                cookie_name_value = cookie.decode("utf-8").split(';')[0]
                if not cookie_value:
                    cookie_name, self.cookie_value = cookie_name_value.split('=')

            for script_tag in script_tags:
                # Extract the content of the script tag
                script_content = script_tag.extract()

                # Apply custom parsing logic to extract specific values
                # For example, using regular expressions
                match = re.search(r'"search_id"\s*:\s*"([^"]+)"', script_content)
                csrf_token = re.search(r'"t"\s*:\s*"([^"]+)"', script_content)
                pvuuid = re.search(r'"pvuuid"\s*:\s*(\d+)', script_content)
                if match:
                    extracted_value = match.group(1)
                if pvuuid:
                    self.pvuuid = pvuuid.group(1)
                if pvuuid:
                    self.csrf_token = csrf_token.group(1)

                if extracted_value and self.pvuuid and self.csrf_token:
                    break
            next_btn = response.xpath('//*[@id="show-more-btn"]')

        # if we have next page to extract the data
        if next_btn and extracted_value and self.start < 5:
            # set the headers for the XHR request
            headers = {
                'Cookie': f't={self.cookie_value};',
                'X-CSRFToken': self.csrf_token,
                "Origin": "https://www.equipmentradar.com",
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            }

            # set payload
            payload = f"action=show_more&view=directory&id={extracted_value}&pvuuid={self.pvuuid}&muuid="
            # create Request object
            req = Request(f"{self.start_urls[0]}?page={self.start}",
                          method='POST',
                          headers=headers,
                          body=payload,
                          callback=self.parse_xhr_response)
            # set the Origin explicitly
            req.headers['Origin'] = 'https://www.equipmentradar.com'
            yield req

    def parse_xhr_response(self, response):
        response = response.json()
        # get the html content from the response which is in result key
        results = response.get('results')

        # get the search id for the next page
        search_id = response.get('search_id')
        # get the number of remaining results
        _next = response.get('search_meta', {}).get("remaining", 0)
        # create scrapy response object to pass it to parse function
        response = HtmlResponse(url=self.start_urls[0], body=results, encoding='utf-8')

        yield from self.parse(response, search_id, _next)
