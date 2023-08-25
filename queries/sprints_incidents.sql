SELECT
    TIMESTAMP_TRUNC(time_resolved, DAY) as day,
    IF(COUNT(DISTINCT issue_id) = 0,0, SUM(IF(is_bug, 1, 0)) / COUNT(DISTINCT issue_id)) as bugs_in_sprint
FROM `four_keys.tasks`
WHERE time_resolved IS NOT NULL
-- AND __timeFilter(time_resolved)
GROUP BY day