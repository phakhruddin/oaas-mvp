terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "network" {
  source = "./modules/network"

  project_name = var.project_name
}

module "queue" {
  source = "./modules/queue"

  project_name = var.project_name
}

module "ecs" {
  source = "./modules/ecs"

  project_name      = var.project_name
  vpc_id            = module.network.vpc_id
  subnet_ids        = module.network.private_subnet_ids
  api_image         = var.api_image
  worker_image      = var.worker_image
  sqs_queue_url     = module.queue.queue_url
  sqs_dlq_url       = module.queue.dlq_url
  cloudwatch_log_group = var.cloudwatch_log_group
}

module "api_gateway" {
  source = "./modules/api-gateway"

  project_name     = var.project_name
  ecs_service_name = module.ecs.api_service_name
}
