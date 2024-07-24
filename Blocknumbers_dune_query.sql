WITH time_range AS (
  SELECT
    interval_time
  FROM
    UNNEST(SEQUENCE(
      TRY_CAST('2024-04-23 21:00:00' AS TIMESTAMP),
      CAST(TRY_CAST('2024-04-25 00:00:00' AS TIMESTAMP) AS TIMESTAMP),
      INTERVAL '5' MINUTE
    )) AS _u(interval_time)
),
filtered_trades AS (
  SELECT
    block_time,
    blockchain,
    block_number
  FROM
    balancer.trades
  WHERE
    block_time BETWEEN TRY_CAST('2024-04-23 21:00:00' AS TIMESTAMP) AND TRY_CAST('2024-04-25 00:00:00' AS TIMESTAMP)
    AND blockchain IN ('ethereum', 'arbitrum')
),
closest_blocks AS (
  SELECT
    t.interval_time,
    f.blockchain,
    f.block_number,
    f.block_time,
    ABS(
      EXTRACT(HOUR FROM (f.block_time - t.interval_time)) * 3600 +
      EXTRACT(MINUTE FROM (f.block_time - t.interval_time)) * 60 +
      EXTRACT(SECOND FROM (f.block_time - t.interval_time))
    ) AS time_diff
  FROM
    time_range t
  JOIN
    filtered_trades f ON f.block_time BETWEEN t.interval_time - INTERVAL '2' MINUTE - INTERVAL '30' SECOND
                         AND t.interval_time + INTERVAL '2' MINUTE + INTERVAL '30' SECOND
),
min_time_diff AS (
  SELECT
    interval_time,
    blockchain,
    MIN(time_diff) AS min_diff
  FROM
    closest_blocks
  GROUP BY
    interval_time, blockchain
)
SELECT
  c.interval_time,
  c.blockchain,
  MIN(c.block_number) AS block_number
FROM
  closest_blocks c
JOIN
  min_time_diff m ON c.interval_time = m.interval_time
                 AND c.blockchain = m.blockchain
                 AND c.time_diff = m.min_diff
GROUP BY
  c.interval_time, c.blockchain
ORDER BY
  c.blockchain, c.interval_time;