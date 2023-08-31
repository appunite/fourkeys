WITH
    StatusChanges AS (
      SELECT
        project,
        issue_id,
        status,
        LAG(status) OVER(PARTITION BY project, issue_id ORDER BY time_created) AS prev_status,
        LAST_VALUE(status) OVER(PARTITION BY project, issue_id ORDER BY time_created) AS last_value,
        time_created
      FROM
        `metrics-keys.four_keys.jira_tasks_statuses`
    ),
    FinishedTasks AS (
      SELECT
        project,
        issue_id,
        MAX(time_created) AS time_resolved
      FROM
        StatusChanges
      WHERE
        status = 'Done'
        AND prev_status != 'Done'
        AND last_value = 'Done'
      GROUP BY
        project,
        issue_id
    ),
    StartedTasks AS (
      SELECT
        project,
        issue_id,
        MIN(time_created) AS time_started
      FROM
        StatusChanges
      WHERE
        status != 'To Do'
        AND prev_status = 'To Do'
      GROUP BY
        project,
        issue_id
    ),
    CreatedTasks AS (
      SELECT
        project,
        issue_id,
        MIN(time_created) AS time_created
      FROM
        `metrics-keys.four_keys.jira_tasks_statuses`
      WHERE
        status = 'To Do'
      GROUP BY
        project,
        issue_id
    ),
    AllTasks AS (
      SELECT project, issue_id, type, link, status
      FROM (
          SELECT
            project,
            issue_id,
            (CASE WHEN type = "bug" AND priority = "Highest" THEN "Incident" ELSE type END) as type,
            link,
            status,
            ROW_NUMBER() OVER (PARTITION BY project, issue_id ORDER BY time_created DESC) AS rn_desc,
          FROM
            `metrics-keys.four_keys.jira_tasks_statuses`
        )
      WHERE
        rn_desc = 1
    )

SELECT
   AllTasks.project,
   AllTasks.issue_id,
   AllTasks.link,
   AllTasks.type = "Bug" OR AllTasks.type = "Incident" as is_bug,
   AllTasks.type,
   CreatedTasks.time_created,
   StartedTasks.time_started,
   FinishedTasks.time_resolved
FROM AllTasks
FULL OUTER JOIN CreatedTasks ON AllTasks.project = CreatedTasks.project AND AllTasks.issue_id = CreatedTasks.issue_id
FULL OUTER JOIN StartedTasks ON AllTasks.project = StartedTasks.project AND AllTasks.issue_id = StartedTasks.issue_id
FULL OUTER JOIN FinishedTasks ON AllTasks.project = FinishedTasks.project AND AllTasks.issue_id = FinishedTasks.issue_id
WHERE
  AllTasks.status != "Deleted"