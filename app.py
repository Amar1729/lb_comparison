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

    st.write('Select the "mia" box for friends who are missing :cry:')
    st.write('Select the "rewatches" button for those who are present, but don\'t mind rewatches.')

    usernames = data.columns[USER_COL_START:USER_COL_START+5]

    selection_df = st.data_editor(
        pd.DataFrame(
            {
                "mia": [False for _ in usernames],
                "rewatches": [False for _ in usernames],
            },
            index=data.columns[USER_COL_START:USER_COL_START+5],
        ),
        column_config={
            "_index": st.column_config.TextColumn(disabled=True),
        },
    )

    filtered_data = data.copy()
    for u in usernames:
        f = selection_df.loc[u, "mia"]
        r = selection_df.loc[u, "rewatches"]
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
            "rating": st.column_config.NumberColumn(format="%.2f"),
            "title": st.column_config.LinkColumn(
                "Title", display_text=r"https://letterboxd\.com/film/.*/?fake=(.*)",
            ),
        },
    )


if __name__ == "__main__":
    main()
