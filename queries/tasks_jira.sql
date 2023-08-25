WITH
    StatusChanges AS (
      SELECT
        project,
        source,
        issue_id,
        link,
        status,
        time_created,
        type,
        ROW_NUMBER() OVER (PARTITION BY project, issue_id ORDER BY time_created) AS rn_asc,
        ROW_NUMBER() OVER (PARTITION BY project, issue_id ORDER BY time_created DESC) AS rn_desc
      FROM
        `metrics-keys.four_keys.jira_tasks_statuses`
    ),
  TasksStatus AS (
      SELECT
      project,
      source,
      issue_id,
      MIN(CASE WHEN rn_asc = 1 THEN time_created END) AS created_at,
      MIN(CASE WHEN rn_desc = 1 THEN type END) AS type,
      MIN(CASE WHEN rn_desc = 1 THEN link END) AS link,
      MIN(CASE WHEN rn_desc = 1 AND status = "Done" THEN time_created else NULL END) AS finished_at,
      MAX(CASE WHEN rn_desc = 1 THEN status END) AS last_status,
      MIN(CASE WHEN rn_asc = 1 THEN time_created END) AS first_status_time_created,
      MAX(CASE WHEN rn_desc = 1 THEN time_created END) AS last_status_time_created
    FROM
      StatusChanges
    GROUP BY
      project,
      source,
      issue_id
  )

SELECT type = "Bug" as is_bug, source, project, issue_id, link, created_at as time_created, finished_at as time_resolved  from TasksStatus