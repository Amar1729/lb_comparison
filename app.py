#! /usr/bin/env python3

"""Runner for streamlit(?)-based webview."""

import sqlite3
from enum import Enum
from pathlib import Path

import pandas as pd
import streamlit as st

USER_COL_START = 4


class Emoji(Enum):
    watched = "✅"
    watchlist = "👀"
    unwatched = "❌"


def load_full_data() -> pd.DataFrame:
    """Load finished (along with watchlist) data into a dataframe."""
    con = sqlite3.connect("movies.sqlite")

    with Path("./queries/into_full_df.sql").open() as sql_f:
        sql_query = sql_f.read()

    data = pd.read_sql_query(sql_query, con)

    # TODO: i should figure out if i can make this a multi-index or something
    # figuring out column offsets for only username columns is annoying
    for c in data.columns[USER_COL_START:]:
        data[c] = data[c].fillna("unwatched").map(lambda s: getattr(Emoji, s).value).astype("category")

    data["count"] = data.apply(
        lambda row: sum(
            row[col] == Emoji.watchlist.value
            for col in data.columns[USER_COL_START:]
        ),
        axis=1,
    )

    # absolutely disgusting construction:
    # streamlit's column_config.LinkColumn can not currently take a URL and use a different
    # column value as the text, the text has to be static or parsed from the URL.
    # You can also use pandas' Styler.format, but streamlit docs note that may be removed
    # in the future(?). So, the only safe way seems to be to construct a URL with a parameter
    # that LB doesn't care about, then parse that from the URL to get our title during page load.
    data["slug"] = data["slug"].apply(
        lambda s: f"https://letterboxd.com/film/{s}/",
    )
    data["title"] = data.apply(
        lambda row: f"{row.slug}?fake={row.title}",
        axis=1,
    )

    return data


def main() -> None:
    st.title("Movie Watch Party: Subset Finder")
    st.write("Finds movies that only a strict subset of us have NOT seen.")
    st.write("Useful for watching movies when not all 5 of us are around(?).")

    st.divider()

    data = load_full_data()

    filters = {}
    rewatches = {}

    # TODO: format these on the page to be not ridiculous
    for username in data.columns[USER_COL_START:USER_COL_START+5]:
        filters[username] = st.checkbox(f"{username}: if checked, this person is NOT here")
        rewatches[username] = st.checkbox(f"→ {username}: (doesn't mind rewatches)")

    filtered_data = data.copy()
    for u in filters:
        f = filters[u]
        r = rewatches[u]
        if r:
            # this person doesn't mind rewatching, so ignore their watch status
            continue
        if not f:
            filtered_data = filtered_data[filtered_data[u].isin(
                {Emoji.unwatched.value, Emoji.watchlist.value},
            )]
        else:
            filtered_data = filtered_data[filtered_data[u] == Emoji.watched.value]

    st.write("Movies: ", len(filtered_data))
    st.dataframe(
        filtered_data,
        hide_index=True,
        column_config={
            "year": st.column_config.NumberColumn("year", format="%d"),
            "slug": None,
            "title": st.column_config.LinkColumn(
                "Title", display_text=r"https://letterboxd\.com/film/.*/?fake=(.*)",
            ),
        },
    )


if __name__ == "__main__":
    main()
