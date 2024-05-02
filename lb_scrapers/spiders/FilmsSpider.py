from __future__ import annotations

import scrapy


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

        for link in response.xpath('//li[@class="poster-container"]/div'):
            link_url = link.attrib["data-target-link"]
            yield {
                "username": self.username,
                "film_slug": link_url.removeprefix("/film/").removesuffix("/"),
            }

        next_page = response.css('a.next::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
