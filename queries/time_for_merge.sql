WITH
  StatusChangesPrev as (
    SELECT
      CONCAT(
          IFNULL(team, "default"),
          "/",
          JSON_EXTRACT_SCALAR(metadata, '$.project.name')
      ) as project,
      JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.id') as pr_id,
      JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.url') as link,
      (
        CASE
        WHEN JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.work_in_progress') = "true"
        THEN "Work In Progress"
        ELSE JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.state')
        END
      ) as status,
      ARRAY(
        SELECT task
        FROM
            UNNEST(
                REGEXP_EXTRACT_ALL(CONCAT(
                    IFNULL(JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.title'), ""),
                    " ",
                    IFNULL(JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.description'), "")
                )
            , r'([A-Z]{2,15}-[0-9]{1,7})')) AS task
        group by task
      ) as tasks,
      JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.title') as title,
      JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.description') as description,
      time_created,
      FROM `four_keys.events_raw`
      where source = "gitlab"
      AND event_type = "merge_request"
  ),
  StatusChanges AS (
      SELECT
        *,
        LAG(status) OVER(PARTITION BY project, pr_id ORDER BY time_created) AS prev_status,
        LAST_VALUE(status) OVER(PARTITION BY project, pr_id ORDER BY time_created) AS last_value,
        ROW_NUMBER() OVER (PARTITION BY project, pr_id ORDER BY time_created DESC) AS rn_desc,
      FROM
        StatusChangesPrev
    ),
  AllPullRequests AS (
      SELECT *
      FROM StatusChanges
      WHERE
        rn_desc = 1
    ),
    MergeTime AS (
      SELECT
        project,
        pr_id,
        MAX(time_created) AS time_resolved
      FROM
        StatusChanges
      WHERE
        status = 'merged'
        AND prev_status is not NULL
        AND prev_status != 'merged'
      GROUP BY
        project,
        pr_id
    ),
    CratedTime AS (
      SELECT
        project,
        pr_id,
        MIN(time_created) AS time_created
      FROM
        StatusChanges
      WHERE
        status = 'opened'
        AND (prev_status is NULL OR prev_status != 'opened')
      GROUP BY
        project,
        pr_id
    )


SELECT
   AllPullRequests.project,
   AllPullRequests.pr_id,
   AllPullRequests.link,
   AllPullRequests.status as last_status,
   CratedTime.time_created,
   CASE WHEN AllPullRequests.status = "merged" THEN MergeTime.time_resolved END as time_resolved,
   DATE_DIFF(time_resolved, CratedTime.time_created, second) as lead_time_seconds,
FROM AllPullRequests
FULL OUTER JOIN CratedTime ON AllPullRequests.project = CratedTime.project AND AllPullRequests.pr_id = CratedTime.pr_id
FULL OUTER JOIN MergeTime ON AllPullRequests.project = MergeTime.project AND AllPullRequests.pr_id = MergeTime.pr_id
