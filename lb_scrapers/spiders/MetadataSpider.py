from __future__ import annotations

import re
from typing import override

import scrapy

from . import get_movie_links


class MetadataSpider(scrapy.Spider):
    name = "metadata"
    custom_settings = {
        "ITEM_PIPELINES": {
            "lb_scrapers.pipelines.MetadataPipeline": 300,
        },
    }

    @override
    def start_requests(self):
        """Get all movies from DB that have a NULL title/rating value."""
        for url in get_movie_links():
            yield scrapy.Request(url, dont_filter=True)

    @override
    def parse(self, response):
        slug_text = re.search(r"https://letterboxd\.com/film/(.*)/", response.url)
        if not slug_text:
            return None

        slug = slug_text.group(1)
        title = response.css(".headline-1 *::text").get()

        if not title:
            return None

        # TODO: in some cases, might have to update release year as well?
        # in case there's a movie that gets pushed back, maybe
        year = response.css(".releaseyear *::text").get()

        # TODO: ratings change over time, scraping them once is probably not ideal?
        rating = None
        if rating_text_elems := response.xpath("//meta[contains(@name, 'twitter:data2')]"):
            rating_text = rating_text_elems[0].attrib["content"]
            if m := re.match(r"([\d.]*) out of", rating_text):
                # absolutely disgusting because sometimes the float comes in as precision 2?
                rating = round(float(m.group(1)), 2)

        yield {
            "film_slug": slug,
            "title": title,
            "year": year,
            "rating": rating,
        }
