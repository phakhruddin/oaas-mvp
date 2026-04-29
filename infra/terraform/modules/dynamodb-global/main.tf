variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "table_name" {
  description = "DynamoDB table name."
  type        = string
}

variable "hash_key" {
  description = "Partition key name."
  type        = string
  default     = "pk"
}

variable "range_key" {
  description = "Sort key name."
  type        = string
  default     = "sk"
}

variable "replica_regions" {
  description = "Additional AWS regions for DynamoDB Global Table replicas."
  type        = list(string)
  default     = []
}

resource "aws_dynamodb_table" "global" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = var.hash_key
  range_key    = var.range_key

  attribute {
    name = var.hash_key
    type = "S"
  }

  attribute {
    name = var.range_key
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  dynamic "replica" {
    for_each = var.replica_regions

    content {
      region_name = replica.value
    }
  }

  tags = {
    Name    = var.table_name
    Service = var.project_name
  }
}

output "table_name" {
  value = aws_dynamodb_table.global.name
}

output "table_arn" {
  value = aws_dynamodb_table.global.arn
}

output "stream_arn" {
  value = aws_dynamodb_table.global.stream_arn
}
