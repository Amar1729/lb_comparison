from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Generator

T_ALLOWED = Literal["finished", "watchlist"]


def get_movie_links() -> Generator[str, None, None]:
    pth = Path(__file__).absolute().parent.parent.parent / "movies.sqlite"
    if not pth.exists():
        raise RuntimeError
    con = sqlite3.connect(str(pth))
    cur = con.cursor()

    results: list[str] = list(cur.execute("SELECT slug FROM movies WHERE title IS NULL"))
    con.close()

    for slug in results:
        yield f"https://letterboxd.com/film/{slug[0]}/"


def item_seen(item: dict[str, str], link_type: T_ALLOWED) -> bool:
    pth = Path(__file__).absolute().parent.parent.parent / "movies.sqlite"
    if not pth.exists():
        return False
    con = sqlite3.connect(str(pth))
    cur = con.cursor()

    # TODO: possibly turn user_id / movie_id queries into INSERTs?

    user_id = cur.execute(
        "SELECT id FROM users WHERE name = ?",
        (item["username"],),
    ).fetchone()

    if not user_id:
        return False

    movie_id = cur.execute(
        "SELECT id FROM movies WHERE slug = ?",
        (item["film_slug"],),
    ).fetchone()

    if not movie_id:
        return False

    if link_type == "watchlist":
        link = cur.execute(
            "SELECT user_id, movie_id FROM join_watchlist WHERE user_id = ? AND movie_id = ?",
            (user_id[0], movie_id[0]),
        ).fetchone()
    elif link_type == "finished":
        link = cur.execute(
            "SELECT user_id, movie_id FROM join_finished WHERE user_id = ? AND movie_id = ?",
            (user_id[0], movie_id[0]),
        ).fetchone()
    else:
        raise ValueError

    if not link:
        return False

    return True
