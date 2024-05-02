# letterbox watchlist comparisons

Tools for comparing watchlists/finished movie lists between multiple (n > 2) letterboxd users.

Currently holds two scrapers (one for /watchlist and one for /films) for users, and some relevant SQL queries.

```sh
scrapy startproject
letterboxd_watchlist_comparison_scrapy
```

## installation

Install dependencies with a python package manager of your choice.
The `run.sh` script expects a virtual environment named `.venv`.

```bash
# via pip
python3 -m venv .venv
.venv/bin/pip install -r ./requirements.txt

# via uv
uv venv
uv pip sync ./requirements.txt
```

## usage

First, scrape info for all your users.
You may run `scrapy crawl` manually, or use `run.sh`.
When using `run.sh`, you may add your wanted usernames to a file `users.txt`; if it exists, `run.sh` will assume one username per line.

```bash
# invoking scrapy manually
scrapy crawl -a username=username watchlist
scrapy crawl -a username=username films

# via wrapper script (can take multiple usernames)
./run.sh username1
./run.sh username1 username2

# with "users.txt"
cat > users <<EOF
username1
username2
EOF

./run.sh
```

## data

Once data is scraped, you can use the included SQL queries to see insights:

```bash
sqlite3 ./movies.sqlite < ./queries/multiple_watchlist.sql

sqlite3 ./movies.sqlite < ./queries/watchlist_no_watched.sql
```
