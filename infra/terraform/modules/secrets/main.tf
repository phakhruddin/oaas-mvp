resource "aws_secretsmanager_secret" "slack" {
  name = "${var.project_name}-slack"
}

resource "aws_secretsmanager_secret_version" "slack" {
  secret_id     = aws_secretsmanager_secret.slack.id
  secret_string = jsonencode({
    SLACK_WEBHOOK_URL = var.slack_webhook_url
  })
}

resource "aws_secretsmanager_secret" "api_keys" {
  name = "${var.project_name}-api-keys"
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id     = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    DEFAULT_API_KEY = var.default_api_key
  })
}
