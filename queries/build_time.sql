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
      JSON_EXTRACT_SCALAR(build, '$.id') as build_id,
      JSON_EXTRACT_SCALAR(build, '$.stage') as build_stage,
      JSON_EXTRACT_SCALAR(build, '$.name') as build_name,
      TIMESTAMP(JSON_EXTRACT_SCALAR(build, '$.started_at')) as build_time_started,
      TIMESTAMP(JSON_EXTRACT_SCALAR(build, '$.finished_at')) as build_time_finished,
      CAST(JSON_EXTRACT_SCALAR(build, '$.duration') as FLOAT64) as build_duration_seconds,
      CAST(JSON_EXTRACT_SCALAR(build, '$.queued_duration') as FLOAT64) as build_queued_duration_seconds,
      CONCAT(
        -- https://git.appunite.com/newmedia/gistr-android /-/pipelines/312613/builds
        JSON_EXTRACT_SCALAR(metadata, '$.project.web_url'),
        '/-/jobs/',
        -- job id
        JSON_EXTRACT_SCALAR(build, '$.id')
      ) as build_url,
FROM `four_keys.events_raw`
CROSS JOIN UNNEST(JSON_EXTRACT_ARRAY(metadata, '$.builds')) AS build
WHERE
    source = "gitlab"
    AND event_type = "pipeline"
    AND JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.status') = "success"