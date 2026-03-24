# -------------------------------------------------------------------
# Generation 2: The Eternal Chimera (永劫の合成獣 - 究極のコスト効率と弾力性)
# -------------------------------------------------------------------

provider "google" {
  project = "YOUR_GCP_PROJECT_ID"
  region  = "asia-northeast1"
}

# [錬金術: 虚無の回廊] 外部IPを排除しつつ外部通信を可能にする最小構成の通信路
resource "google_compute_network" "chimera_vpc" {
  name                    = "v2-chimera-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "chimera_subnet" {
  name          = "v2-chimera-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.chimera_vpc.id
  region        = "asia-northeast1"
}

resource "google_compute_router" "router" {
  name    = "v2-chimera-router"
  region  = google_compute_subnetwork.chimera_subnet.region
  network = google_compute_network.chimera_vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "v2-chimera-nat"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# [錬金術: 魂の鋳型] 高速起動のためにOSをContainer-Optimized OSへ転換
resource "google_compute_region_instance_template" "chimera_template" {
  name_prefix  = "v2-chimera-template-"
  machine_type = "e2-micro"

  scheduling {
    preemptible                 = true
    automatic_restart           = false
    provisioning_model          = "SPOT"
    instance_termination_action = "STOP"
  }

  disk {
    source_image = "cos-cloud/cos-stable"
    disk_type    = "pd-standard" # コスト最優先の標準ディスク
    disk_size_gb = 10
    auto_delete  = true
    boot         = true
  }

  network_interface {
    network    = google_compute_network.chimera_vpc.id
    subnetwork = google_compute_subnetwork.chimera_subnet.id
    # access_config（外部IP）を完全に封印
  }

  metadata = {
    google-logging-enabled = "true"
    startup-script        = "echo 'Reborn from ashes' > /tmp/birth.log"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# [錬金術: 真理の眼] 不死を監視する高感度センサー
resource "google_compute_region_health_check" "chimera_health_check" {
  name               = "v2-chimera-hc"
  check_interval_sec = 5
  timeout_sec        = 3

  tcp_health_check {
    port = "22"
  }
}

# [錬金術: 賢者の石] リージョン全域に魂を分散させる身代わり製造機
resource "google_compute_region_instance_group_manager" "chimera_mig" {
  name               = "v2-chimera-mig"
  base_instance_name = "chimera"
  region             = "asia-northeast1"

  version {
    instance_template = google_compute_region_instance_template.chimera_template.id
  }

  auto_healing_policies {
    health_check      = google_compute_region_health_check.chimera_health_check.id
    initial_delay_sec = 60 # 高速起動OSにより待機時間を大幅短縮
  }

  # リージョン内の複数ゾーンに自動分散し、1ゾーンの崩壊に耐える
  distribution_policy_zones = ["asia-northeast1-a", "asia-northeast1-b", "asia-northeast1-c"]

  update_policy {
    type                  = "PROACTIVE"
    minimal_action        = "REPLACE"
    max_surge_fixed       = 1
    max_unavailable_fixed = 1
  }
}

# [錬金術: 禁忌の増殖制御] 魔力の暴走を防ぐガードレール
resource "google_compute_region_autoscaler" "chimera_autoscaler" {
  name   = "v2-chimera-autoscaler"
  region = "asia-northeast1"
  target = google_compute_region_instance_group_manager.chimera_mig.id

  autoscaling_policy {
    max_replicas    = 3 # 絶対遵守の魔力上限
    min_replicas    = 1
    cooldown_period = 30

    cpu_utilization {
      target = 0.7 # 限界までリソースを絞り出し、無駄を削ぎ落とす
    }
  }
}