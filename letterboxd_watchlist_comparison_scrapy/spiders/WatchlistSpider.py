from __future__ import annotations

import scrapy


class WatchlistSpider(scrapy.Spider):
    name = "watchlist"
    custom_settings = {
        "ITEM_PIPELINES": {
            "letterboxd_watchlist_comparison_scrapy.pipelines.LetterboxdWatchlistComparisonScrapyPipeline": 300,
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
            yield {
                "username": self.username,
                "film_slug": link_url.removeprefix("/film/").removesuffix("/"),
            }

        next_page = response.css('a.next::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)