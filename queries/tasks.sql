SELECT
    project,
    issue_id,
    link,
    is_bug,
    type,
    time_created,
    time_started,
    time_resolved,
    CASE WHEN time_resolved IS NOT NULL AND time_created IS NOT NULL THEN DATE_DIFF(time_resolved, time_created, minute) / 60.0 END as lead_time_hours,
    CASE WHEN time_resolved IS NOT NULL AND time_started IS NOT NULL THEN DATE_DIFF(time_resolved, time_started, minute) / 60.0 END as cycle_time_hours,
    CASE WHEN time_resolved IS NOT NULL AND time_created IS NOT NULL THEN DATE_DIFF(time_resolved, time_created, second) END as lead_time_seconds,
    CASE WHEN time_resolved IS NOT NULL AND time_started IS NOT NULL THEN DATE_DIFF(time_resolved, time_started, second) END as cycle_time_seconds,
FROM
    `metrics-keys.four_keys.tasks_jira`