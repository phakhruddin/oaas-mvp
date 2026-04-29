variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "domain_name" {
  description = "Public domain name, for example example.com."
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID for the domain."
  type        = string
}

variable "primary_dns_name" {
  description = "DNS name for the primary regional endpoint, usually an ALB DNS name."
  type        = string
}

variable "secondary_dns_name" {
  description = "DNS name for the secondary regional endpoint, usually an ALB DNS name."
  type        = string
}

variable "primary_health_check_path" {
  description = "Health check path for primary endpoint."
  type        = string
  default     = "/health"
}

variable "secondary_health_check_path" {
  description = "Health check path for secondary endpoint."
  type        = string
  default     = "/health"
}

resource "aws_route53_health_check" "primary" {
  fqdn              = var.primary_dns_name
  port              = 443
  type              = "HTTPS"
  resource_path     = var.primary_health_check_path
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name    = "${var.project_name}-primary-health-check"
    Service = var.project_name
    Region  = "primary"
  }
}

resource "aws_route53_health_check" "secondary" {
  fqdn              = var.secondary_dns_name
  port              = 443
  type              = "HTTPS"
  resource_path     = var.secondary_health_check_path
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name    = "${var.project_name}-secondary-health-check"
    Service = var.project_name
    Region  = "secondary"
  }
}

resource "aws_route53_record" "primary" {
  zone_id = var.hosted_zone_id
  name    = var.domain_name
  type    = "CNAME"
  ttl     = 60

  set_identifier = "primary"

  failover_routing_policy {
    type = "PRIMARY"
  }

  health_check_id = aws_route53_health_check.primary.id
  records         = [var.primary_dns_name]
}

resource "aws_route53_record" "secondary" {
  zone_id = var.hosted_zone_id
  name    = var.domain_name
  type    = "CNAME"
  ttl     = 60

  set_identifier = "secondary"

  failover_routing_policy {
    type = "SECONDARY"
  }

  health_check_id = aws_route53_health_check.secondary.id
  records         = [var.secondary_dns_name]
}

output "primary_health_check_id" {
  value = aws_route53_health_check.primary.id
}

output "secondary_health_check_id" {
  value = aws_route53_health_check.secondary.id
}
