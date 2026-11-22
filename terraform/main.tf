terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "roboflow-sec-demo"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

# Showcasing Secure GKE Cluster Configuration (For Checkov Static Security Scanning)
resource "google_container_cluster" "secure_inference_cluster" {
  name     = "roboflow-inference-gke"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  # 1. Enable Workload Identity to avoid Pods directly using overly permissive Node Service Accounts
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # 2. Enable VPC Native Networking and Network Policy Isolation
  networking_mode = "VPC_NATIVE"
  ip_allocation_policy {}

  network_policy {
    enabled = true
  }

  # 3. Stop using the insecure legacy ABAC authorization, enforce RBAC
  enable_legacy_abac = false

  # 4. Use private cluster configuration to eliminate public IP exposure risks (via Checkov CKV_GCP_25)
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  # 5. Enable Intranode Visibility to ensure all pod-to-pod traffic is auditable via VPC Flow Logs (via Checkov CKV_GCP_61)
  enable_intranode_visibility = true

}

  