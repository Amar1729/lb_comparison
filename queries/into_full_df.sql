SELECT
    CASE
        WHEN finished.slug IS NOT NULL THEN finished.slug
        WHEN watchlist.slug IS NOT NULL THEN watchlist.slug
    END slug,
    CASE
        WHEN finished.title IS NOT NULL THEN finished.title
        WHEN watchlist.title IS NOT NULL THEN watchlist.title
    END title,
    CASE
        WHEN finished.rating IS NOT NULL THEN finished.rating
        WHEN watchlist.rating IS NOT NULL THEN watchlist.rating
    END rating,
    CASE
        WHEN finished.year IS NOT NULL THEN finished.year
        WHEN watchlist.year IS NOT NULL THEN watchlist.year
    END year,
    CASE
        WHEN watchlist.amar1729 = True THEN 'watchlist'
        WHEN finished.amar1729 = True THEN 'watched'
    END amar1729,
    CASE
        WHEN watchlist.nicole_kaff = True THEN 'watchlist'
        WHEN finished.nicole_kaff = True THEN 'watched'
    END nicole_kaff,
    CASE
        WHEN watchlist.urbacha = True THEN 'watchlist'
        WHEN finished.urbacha = True THEN 'watched'
    END urbacha,
    CASE
        WHEN watchlist.gina_404 = True THEN 'watchlist'
        WHEN finished.gina_404 = True THEN 'watched'
    END gina_404,
    CASE
        WHEN watchlist.svinson = True THEN 'watchlist'
        WHEN finished.svinson = True THEN 'watched'
    END svinson
FROM
(
    SELECT
      slug,
      title,
      rating,
      year,
      SUM(CASE WHEN name = 'amar1729' THEN True END) amar1729,
      SUM(CASE WHEN name = 'nicole_kaff' THEN True END) nicole_kaff,
      SUM(CASE WHEN name = 'urbacha' THEN True END) urbacha,
      SUM(CASE WHEN name = 'gina_404' THEN True END) gina_404,
      SUM(CASE WHEN name = 'svinson' THEN True END) svinson
    FROM
    (
      SELECT
        slug, name, title, rating, year
      FROM movies
      JOIN join_watchlist
        ON join_watchlist.movie_id = movies.id
      JOIN users
        ON user_id = users.id
    )
    GROUP BY slug
) watchlist
FULL OUTER JOIN
(
    SELECT
      slug,
      title,
      rating,
      year,
      SUM(CASE WHEN name = 'amar1729' THEN True END) amar1729,
      SUM(CASE WHEN name = 'nicole_kaff' THEN True END) nicole_kaff,
      SUM(CASE WHEN name = 'urbacha' THEN True END) urbacha,
      SUM(CASE WHEN name = 'gina_404' THEN True END) gina_404,
      SUM(CASE WHEN name = 'svinson' THEN True END) svinson
    FROM
    (
      SELECT
        slug, name, title, rating, year
      FROM movies
      JOIN join_finished
        ON join_finished.movie_id = movies.id
      JOIN users
        ON user_id = users.id
    )
    GROUP BY slug
) finished
ON watchlist.slug = finished.slug
