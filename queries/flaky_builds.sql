WITH PiplineRuns as (
    SELECT
        *,
      CONCAT(
          IFNULL(team, "default"),
          "/",
          JSON_EXTRACT_SCALAR(metadata, '$.project.name')
      ) as project,
      JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.id') as pipeline_id,
      JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.status') as status,
      CONCAT(
        -- https://git.appunite.com/newmedia/gistr-android /-/pipelines/312613/builds
        JSON_EXTRACT_SCALAR(metadata, '$.project.web_url'),
        '/-/pipelines/',
        -- pipeline id
        JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.id')
      ) as pipeline_url,

      ARRAY(
          SELECT
            CONCAT(
            -- https://git.appunite.com/newmedia/gistr-android /-/pipelines/312613/builds
            JSON_EXTRACT_SCALAR(metadata, '$.project.web_url'),
            '/-/jobs/',
            -- job id
            JSON_EXTRACT_SCALAR(builds, '$.id')
          ) as pipeline_url

          FROM UNNEST(JSON_EXTRACT_ARRAY(metadata, "$.builds")) builds
          WHERE JSON_EXTRACT_SCALAR(builds, '$.status') = "failed"
      ) AS failed_jobs,
    FROM
        `metrics-keys.four_keys.events_raw`
    WHERE
      source = "gitlab"
      AND
      event_type = "pipeline"
      AND
      JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.status') in ('success', 'failed')
    ORDER BY
      time_created DESC
),
    PipelineWithPrevious as (
    SELECT
        *,
        LEAD(status) OVER(PARTITION BY project, pipeline_id ORDER BY time_created) AS next_status,
        LEAD(time_created) OVER(PARTITION BY project, pipeline_id ORDER BY time_created) AS next_time_created,
    FROM PiplineRuns
)

SELECT
    project,
    pipeline_id,
    pipeline_url,
    time_created AS time_failure,
    next_time_created as time_fixed,
    failed_jobs,
    DATE_DIFF(next_time_created, time_created, second) as lost_time,
FROM PipelineWithPrevious
WHERE
    status = 'failed'
    AND
    next_status = 'success'