-- movies that are on at least one watchlist but NO finished lists

select
  count(join_watchlist.movie_id), slug
from movies
join join_watchlist
  on movies.id = join_watchlist.movie_id
where not exists (
  select 1 from join_finished
  where join_finished.movie_id = movies.id
)
group by join_watchlist.movie_id
order by count(join_watchlist.movie_id) desc
