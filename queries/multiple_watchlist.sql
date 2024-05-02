-- movies that are watchlisted by more than one person
select
  id, count(id), slug
from movies
join join_watchlist
  on movies.id = join_watchlist.movie_id
group by movie_id
having count(movie_id) > 1
