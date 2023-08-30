resource "google_cloud_run_service" "event_handler" {
  name     = "event-handler"
  project  = var.project_id
  location = var.region

  template {
    spec {
      containers {
        image = local.event_handler_container_url
        env {
          name  = "PROJECT_NAME"
          value = var.project_id
        }
        env {
          name = "TEAMS"
          value = "${join(",", var.teams)}"
        }
      }
      service_account_name = google_service_account.fourkeys.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
  depends_on = [
    time_sleep.wait_for_services
  ]
}

resource "google_cloud_run_service_iam_binding" "event_handler_noauth" {
  location   = var.region
  project    = var.project_id
  service    = google_cloud_run_service.event_handler.name
  role       = "roles/run.invoker"
  members    = ["allUsers"]
  depends_on = [google_cloud_run_service.event_handler]
}

resource "google_secret_manager_secret" "event_handler" {
  project   = var.project_id
  secret_id = "event-handler"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
  depends_on = [
    time_sleep.wait_for_services
  ]
}

resource "random_id" "event_handler_random_value" {
  byte_length = "20"
}

resource "google_secret_manager_secret_version" "event_handler" {
  secret      = google_secret_manager_secret.event_handler.id
  secret_data = random_id.event_handler_random_value.hex
  depends_on  = [google_secret_manager_secret.event_handler]
}

resource "google_secret_manager_secret_iam_member" "event_handler" {
  project    = var.project_id
  secret_id  = google_secret_manager_secret.event_handler.id
  role       = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.fourkeys.email}"
  depends_on = [google_secret_manager_secret.event_handler, google_secret_manager_secret_version.event_handler]
}

resource "google_secret_manager_secret" "event_handler_project_secret" {
  for_each = toset(var.teams)
  project   = var.project_id
  secret_id = "event-handler-${each.key}"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
  depends_on = [
    time_sleep.wait_for_services
  ]
}

resource "random_id" "event_handler_project_secret_random_value" {
  for_each = toset(var.teams)
  byte_length = "20"
}

resource "google_secret_manager_secret_version" "event_handler_project_secret" {
  for_each = toset(var.teams)
  secret      = google_secret_manager_secret.event_handler_project_secret[each.key].id
  secret_data = random_id.event_handler_project_secret_random_value[each.key].hex
  depends_on  = [google_secret_manager_secret.event_handler_project_secret]
}

resource "google_secret_manager_secret_iam_member" "event_handler_project_secret" {
  for_each = toset(var.teams)
  project    = var.project_id
  secret_id  = google_secret_manager_secret.event_handler_project_secret[each.key].id
  role       = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.fourkeys.email}"
  depends_on = [google_secret_manager_secret.event_handler_project_secret, google_secret_manager_secret_version.event_handler]
}