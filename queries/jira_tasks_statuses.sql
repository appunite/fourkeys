SELECT
  CONCAT(
    team,
    "/",
    REGEXP_EXTRACT(
      -- Extract from link "https://loudius.atlassian.net/rest/api/2/10073"
      -- Project name "loudius"
      JSON_EXTRACT_SCALAR(metadata, '$.issue.self'),
      r'^https?:\/\/(\w+)',
      1
    )
  ) as project,
  JSON_EXTRACT_SCALAR(metadata, '$.issue.key') as issue_id,
  CONCAT(
    -- Extract from format "https://loudius.atlassian.net/rest/api/2/10073"
    -- Root URL "https://loudius.atlassian.net/",
    -- to build "https://loudius.atlassian.net/browse/LD-123" link
    REGEXP_EXTRACT( JSON_EXTRACT_SCALAR(metadata, '$.issue.self'), r'^(https?:\/\/[^\/]*\/)', 1),
    "browse/",
    JSON_EXTRACT_SCALAR(metadata, '$.issue.key')
  ) as link,
  JSON_EXTRACT_SCALAR(metadata, '$.issue.fields.summary') as summary,
  JSON_EXTRACT_SCALAR(metadata, '$.issue.fields.priority.name') as priority,
  JSON_EXTRACT_SCALAR(metadata, '$.issue.fields.description') as description,
  JSON_EXTRACT_SCALAR(metadata, '$.issue.fields.issuetype.name') as type,
  CASE WHEN JSON_EXTRACT_SCALAR(metadata, '$.webhookEvent') = "jira:issue_deleted" THEN "Deleted" else JSON_EXTRACT_SCALAR(metadata, '$.issue.fields.status.name') END as status,
  JSON_EXTRACT_SCALAR(metadata, '$.issue.fields.resolution.name') as resolution,
  TIMESTAMP(JSON_EXTRACT_SCALAR(metadata, '$.issue.fields.created')) as time_task_created,
  time_created
FROM `metrics-keys.four_keys.events_raw`
where
    source = "jira"
  and
    JSON_EXTRACT_SCALAR(metadata, '$.webhookEvent') in ("jira:issue_updated", "jira:issue_created", "jira:issue_deleted")