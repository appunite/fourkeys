SELECT
  CONCAT(
      IFNULL(team, "default"),
      "/",
      JSON_EXTRACT_SCALAR(metadata, '$.project.name')
  ) as project,
  JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.ref') as ref,
  JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.id') as pipeline_id,
  CONCAT(
    -- https://git.appunite.com/newmedia/gistr-android /-/pipelines/312613/builds
    JSON_EXTRACT_SCALAR(metadata, '$.project.web_url'),
    '/-/pipelines/',
    -- pipeline id
    JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.id')
  ) as pipeline_url,
  time_created,
  (JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.status') = 'success') as is_success,
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
  AND
    JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.source') = "push"
--    AND
--    JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.ref') in ('develop', 'main', 'master')
ORDER BY
  time_created DESC