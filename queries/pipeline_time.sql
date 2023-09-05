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
      TIMESTAMP(JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.created_at')) as time_created,
      TIMESTAMP(JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.finished_at')) as time_finished,
      CAST(JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.duration') as FLOAT64) as duration_seconds,
FROM `four_keys.events_raw`
WHERE
    source = "gitlab"
    AND event_type = "pipeline"
    AND JSON_EXTRACT_SCALAR(metadata, '$.object_attributes.status') = "success"