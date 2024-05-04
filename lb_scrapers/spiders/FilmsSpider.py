from __future__ import annotations

import scrapy
from scrapy.exceptions import CloseSpider

from . import item_seen


class FilmsSpider(scrapy.Spider):
    name = "films"
    custom_settings = {
        "ITEM_PIPELINES": {
            "lb_scrapers.pipelines.FilmsPipeline": 300,
        },
    }

    def __init__(self, username: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if username is None:
            raise ValueError("username must be set.")
        self.username = username
        self.start_urls = [f"https://letterboxd.com/{username}/films"]

    def parse(self, response):
        # this seems like it might be a very intensive parse
        # make sure to not re-run this too many times?
        # (alternatively, should i just scrape film watch status from each film on shared watchlist?)

        any_item_seen = False

        for link in response.xpath('//li[@class="poster-container"]/div'):
            link_url = link.attrib["data-target-link"]
            item = {
                "username": self.username,
                "film_slug": link_url.removeprefix("/film/").removesuffix("/"),
            }

            if item_seen(item, "finished"):
                any_item_seen = True

            yield item

        # TODO: this checking actually won't work if someone backdates film watches...
        # (provide a --full flag or something similar?)
        # stop the spider if we've seen anything on this page so far.
        # (links come in in a weird order)
        if any_item_seen:
            msg = "film item seen before"
            raise CloseSpider(msg)

        next_page = response.css('a.next::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
