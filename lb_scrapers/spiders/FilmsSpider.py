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

        # LB sorts username/films by release date, so we technically have to scrape everything...
        # self.start_urls = [f"https://letterboxd.com/{username}/films"]
        # also uses robots.txt to prevent scraping of username/films/by/date, so we can't do that
        # (unless we say not to obey robots.txt)
        # (sort by "when added > newest first")
        self.start_urls = [f"https://letterboxd.com/{username}/films/by/date/"]

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

        # This will only work for /by/date, see comment for start_urls.
        if any_item_seen:
            msg = "film item seen before"
            raise CloseSpider(msg)

        next_page = response.css('a.next::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
