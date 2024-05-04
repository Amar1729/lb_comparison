# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from __future__ import annotations

import sqlite3
from pathlib import Path

# useful for handling different item types with a single interface
from typing_extensions import TypedDict


class ItemType(TypedDict):
    username: str
    film_slug: str


class MetadataType(TypedDict):
    film_slug: str
    title: str
    year: int
    rating: float


def _init_db(cur: sqlite3.Cursor) -> None:

    _ = cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
     """)

    # NOTE: this is local DB id, not the IMDB/TMDB/letterboxd id.
    _ = cur.execute("""
        CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY,
            -- metadata only parsed later, separately from user info scraping
            title TEXT,
            rating REAL,
            year INTEGER,
            -- "slug" uniquely identifies the film's URL
            slug TEXT NOT NULL UNIQUE
        )
     """)

    _ = cur.execute("""
        CREATE TABLE IF NOT EXISTS join_watchlist(
            user_id INTEGER,
            movie_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            PRIMARY KEY (user_id, movie_id)
        )
     """)

    _ = cur.execute("""
        CREATE TABLE IF NOT EXISTS join_finished(
            user_id INTEGER,
            movie_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            PRIMARY KEY (user_id, movie_id)
        )
     """)


def insert_item(cur: sqlite3.Cursor, item: ItemType) -> tuple[int, int]:

    _ = cur.execute(
        "INSERT OR IGNORE INTO users (name) VALUES (?)",
        (
            item["username"],
        ),
    )

    _ = cur.execute(
        "INSERT OR IGNORE INTO movies (slug) VALUES (?)",
        (
            item["film_slug"],
        ),
    )

    user_id = cur.execute(
        "SELECT id FROM users WHERE name = (?)",
        (item["username"],),
    ).fetchone()[0]

    movie_id = cur.execute(
        "SELECT id FROM movies WHERE slug = (?)",
        (item["film_slug"],),
    ).fetchone()[0]

    return user_id, movie_id


class WatchlistPipeline:
    def __init__(self, *args, **kwargs) -> None:
        # TODO: connection URL should probably be in settings.py
        self.pth = Path(__file__).absolute().parent.parent / "movies.sqlite"
        self.con = sqlite3.connect(str(self.pth))
        self.cur = self.con.cursor()

        _init_db(self.cur)

    def open_spider(self, spider) -> None:
        self.con = sqlite3.connect(str(self.pth))
        self.cur = self.con.cursor()

    def close_spider(self, spider) -> None:
        self.con.close()

    def process_item(self, item: ItemType, spider):
        user_id, movie_id = insert_item(self.cur, item)

        # the watchlist pipeline only will add relationship to the join_watchlist table
        _ = self.cur.execute(
            "INSERT OR IGNORE INTO join_watchlist(user_id, movie_id) VALUES (?, ?)",
            (user_id, movie_id),
        )

        self.con.commit()
        return item


class FilmsPipeline:
    def __init__(self) -> None:
        self.pth = Path(__file__).absolute().parent.parent / "movies.sqlite"
        self.con = sqlite3.connect(str(self.pth))
        self.cur = self.con.cursor()

        _init_db(self.cur)

    def open_spider(self, spider) -> None:
        self.con = sqlite3.connect(str(self.pth))
        self.cur = self.con.cursor()

    def close_spider(self, spider) -> None:
        self.con.close()

    def process_item(self, item: ItemType, spider) -> ItemType:
        user_id, movie_id = insert_item(self.cur, item)

        # the film pipeline only will add relationship to the join_finished table
        _ = self.cur.execute(
            "INSERT OR IGNORE INTO join_finished(user_id, movie_id) VALUES (?, ?)",
            (user_id, movie_id),
        )

        self.con.commit()
        return item


class MetadataPipeline:
    def __init__(self) -> None:
        self.pth = Path(__file__).absolute().parent.parent / "movies.sqlite"
        self.con = sqlite3.connect(str(self.pth))
        self.cur = self.con.cursor()

        _init_db(self.cur)

    def open_spider(self, spider) -> None:
        self.con = sqlite3.connect(str(self.pth))
        self.cur = self.con.cursor()

    def close_spider(self, spider) -> None:
        self.con.close()

    def process_item(self, item: MetadataType, spider) -> MetadataType:

        _ = self.cur.execute(
            "UPDATE movies SET title = ?, rating = ?, year = ? WHERE slug = ?",
            (item["title"], item["rating"], item["year"], item["film_slug"]),
        )

        self.con.commit()
        return item
