from __future__ import annotations

import scrapy
from scrapy.exceptions import CloseSpider

from . import item_seen


class WatchlistSpider(scrapy.Spider):
    name = "watchlist"
    custom_settings = {
        "ITEM_PIPELINES": {
            "lb_scrapers.pipelines.WatchlistPipeline": 300,
        },
    }

    def __init__(self, username: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if username is None:
            raise ValueError("username must be set.")
        self.username = username
        self.start_urls = [f"https://letterboxd.com/{username}/watchlist"]

    def parse(self, response):
        for link in response.xpath('//li[@class="poster-container"]/div'):
            link_url = link.attrib["data-target-link"]
            item = {
                "username": self.username,
                "film_slug": link_url.removeprefix("/film/").removesuffix("/"),
            }

            if item_seen(item, "watchlist"):
                msg = "watchlist item seen before"
                raise CloseSpider(msg)

            yield item

        next_page = response.css('a.next::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
