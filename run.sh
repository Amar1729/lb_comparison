#! /usr/bin/env bash

SCRIPT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)

source "${SCRIPT_DIR}"/.venv/bin/activate
USER_FILE="${SCRIPT_DIR}/users.txt"

users=()

if [[ $# -eq 0 ]]; then
    while read -r line || [[ -n $line ]]; do
        users+=("$line")
    done < "${USER_FILE}"
else
    users=($@)
fi

for user in ${users[@]}; do
    scrapy crawl -a username="$user" watchlist

    scrapy crawl -a username="$user" films
    sleep 2
done
