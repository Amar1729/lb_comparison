from scrapy.item import Item, Field


class LetterboxdWatchlistComparisonScrapyItem(Item):
    """Item returned by watchlist spider."""

    username = Field()
    film_slug = Field()


class FilmsItem(Item):
    """Item returned by films spider."""

    username = Field()
    film_slug = Field()
