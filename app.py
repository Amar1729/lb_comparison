#! /usr/bin/env python3

"""Runner for streamlit(?)-based webview."""

import sqlite3
from enum import Enum
from pathlib import Path

import pandas as pd
import streamlit as st


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

    for c in data.columns[1:]:
        data[c] = data[c].fillna("unwatched").map(lambda s: getattr(Emoji, s).value).astype("category")

    return data


def main() -> None:
    st.title("Movie Watch Party: Subset Finder")
    st.write("Finds movies that only a strict subset of us have NOT seen.")
    st.write("Useful for watching movies when not all 5 of us are around(?).")

    st.divider()

    # data = load_data()
    data = load_full_data()
    filters = {
        col: st.checkbox(f"{col}: if checked, this person is NOT here")
        for col in data.columns[1:]
    }

    filtered_data = data.copy()
    for u, f in filters.items():
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
    )


if __name__ == "__main__":
    main()
