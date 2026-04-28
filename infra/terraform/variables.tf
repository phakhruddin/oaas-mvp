variable "aws_region" {
  default = "us-east-1"
}

variable "project_name" {
  default = "oaas-mvp"
}

variable "api_image" {
  description = "ECR image for API"
}

variable "worker_image" {
  description = "ECR image for worker"
}

variable "cloudwatch_log_group" {
  default = "/aws/oaas"
}
