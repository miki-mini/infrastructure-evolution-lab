# -------------------------------------------------------------------
# Generation 1: The Immortal Phoenix (不死鳥の自動再誕)
# -------------------------------------------------------------------

provider "google" {
  project = "YOUR_GCP_PROJECT_ID"
  region  = "asia-northeast1"
}

# 1. インスタンスの設計図（テンプレート）
# スポットVMを適用し、コストを最大91%削減
resource "google_compute_region_instance_template" "phoenix_template" {
  name_prefix  = "v1-phoenix-template-"
  machine_type = "e2-micro" # 性能を最適化しつつ低コストへ

  scheduling {
    preemptible                 = true
    automatic_restart           = false
    provisioning_model          = "SPOT"
    instance_termination_action = "STOP"
  }

  disk {
    source_image = "debian-cloud/debian-11"
    auto_delete  = true
    boot         = true
  }

  network_interface {
    network = "default"
    # 外部IP（access_config）を削除し、無駄なIP課金を排除
  }

  lifecycle {
    create_before_destroy = true
  }
}

# 2. 死を検知するためのヘルスチェック
resource "google_compute_health_check" "phoenix_health_check" {
  name               = "v1-phoenix-hc"
  check_interval_sec = 10
  timeout_sec        = 5

  tcp_health_check {
    port = "22" # SSHポートの生存を確認
  }
}

# 3. MIG（身代わり製造機）
# インスタンスが爆発してもリージョン内のどこかに即座に再生成
resource "google_compute_region_instance_group_manager" "phoenix_mig" {
  name               = "v1-phoenix-mig"
  base_instance_name = "phoenix"
  region             = "asia-northeast1"
  target_size        = 1

  version {
    instance_template = google_compute_region_instance_template.phoenix_template.id
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.phoenix_health_check.id
    initial_delay_sec = 300
  }
}

# 4. オートスケーラー
# 最大3台までのガードレールを設置
resource "google_compute_region_autoscaler" "phoenix_autoscaler" {
  name   = "v1-phoenix-autoscaler"
  region = "asia-northeast1"
  target = google_compute_region_instance_group_manager.phoenix_mig.id

  autoscaling_policy {
    max_replicas    = 3
    min_replicas    = 1
    cooldown_period = 60

    cpu_utilization {
      target = 0.6
    }
  }
}