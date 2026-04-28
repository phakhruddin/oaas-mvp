resource "aws_sqs_queue" "main" {
  name = "${var.project_name}-queue"
}

resource "aws_sqs_queue" "dlq" {
  name = "${var.project_name}-dlq"
}

output "queue_url" {
  value = aws_sqs_queue.main.id
}

output "dlq_url" {
  value = aws_sqs_queue.dlq.id
}
