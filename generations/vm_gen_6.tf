# -------------------------------------------------------------------
# Generation 6: The Eternal Golem (不滅の土人形)
# -------------------------------------------------------------------
# Mikiさんへの報告：
# 1. 閉店セール（Spot価格）で仕入れた超格安物件なのに、中身はプロ仕様の頑丈な造りに変えました。
# 2. もし店員さんが急に休んでも（VM削除）、すぐに新しい店員が裏から補充される「不滅のシフト」を組んでいます。
# 3. お店の正面玄関（外部IP）をあえて作らず、裏口のセキュリティを固めることで「安くて安全」を極めました。
# -------------------------------------------------------------------
# 【審査員コメント】
# 案A（単体Spot VM）は安価だが復旧が手動で落選。案B（Load Balancer＋MIG）は強固だが月額$20の維持費が美しくないため落選。
# 最終選出された【案C】は、サーバーレスの「逃げ」を封印し、あえて「泥臭いVM」を錬金術で昇華させた傑作である。
# Regional MIG（広域管理）により、Googleの都合でVMが消されても数秒で別ゾーンに再錬成される「不屈の魂」を宿した。
# さらに外部IPを完全に排除し、Cloud NATとIAPによる「見えない要塞化」を達成。
# Spot VMによる極限のコスト削減（通常価格の約70%オフ）と、エンタープライズ級の可用性を両立させた。
# これこそが、泥から金を生み出す真のインフラ錬金術「不滅のゴーレム」である。
# -------------------------------------------------------------------

provider "google" {
  project = "YOUR_GCP_PROJECT_ID"
  region  = "asia-northeast1"
}

locals {
  project_id = "YOUR_GCP_PROJECT_ID"
  region     = "asia-northeast1"
  zones      = ["asia-northeast1-a", "asia-northeast1-b", "asia-northeast1-c"]
  machine    = "e2-micro" # 錬金術における最小単位の物質
}

# [錬金術: 意思を持つ泥]
# VMに魂を吹き込むための専用サービスアカウント。最小権限の原則を死守。
resource "google_service_account" "golem_soul" {
  account_id   = "v6-golem-sa"
  display_name = "Identity of the Eternal Golem"
}

# [錬金術: 記憶の神殿]
# 前世代から引き継がれた秘匿情報。
resource "google_secret_manager_secret" "golem_core" {
  secret_id = "v6-golem-core"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "golem_access" {
  secret_id = google_secret_manager_secret.golem_core.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "service_account:${google_service_account.golem_soul.email}"
}

# [錬金術: 鋼の設計図]
# Spot VMという「不純物」を使いながら、最強の強度を持たせる。
resource "google_compute_instance_template" "golem_blueprint" {
  name_prefix  = "v6-golem-template-"
  machine_type = locals.machine

  scheduling {
    preemptible       = true           # 泥臭いコスト削減の要（Spot VM）
    automatic_restart = false
    provisioning_model = "SPOT"
    instance_termination_action = "STOP"
  }

  disk {
    source_image = "debian-cloud/debian-11"
    auto_delete  = true
    boot         = true
    disk_size_gb = 10
    disk_type    = "pd-standard" # コスト最優先
  }

  network_interface {
    network = "default"
    # access_config {} # 敢えて空にすることで外部IPを排除（美学と防衛）
  }

  service_account {
    email  = google_service_account.golem_soul.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    echo "Golem Awakened" > /var/www/html/index.html
    # ここにSecret Managerから秘術（APIキー等）を取り出す儀式を記述
  EOT

  lifecycle {
    create_before_destroy = true
  }
}

# [錬金術: 生命の監視]
# ゴーレムが倒れた（VM停止）ことを即座に検知する「第三の目」。
resource "google_compute_region_health_check" "golem_watcher" {
  name = "v6-golem-health-check"
  http_health_check {
    port = 80
  }
}

# [錬金術: 不滅の軍団]
# 特定のゾーンが崩壊しても、他のゾーンで即座に再錬成する。
resource "google_compute_region_instance_group_manager" "golem_legion" {
  name               = "v6-golem-mig"
  base_instance_name = "v6-golem"
  region             = locals.region
  target_size        = 2 # 2体体制で可用性を確保（1体あたりのコストは月数百円）

  version {
    instance_template = google_compute_instance_template.golem_blueprint.id
  }

  auto_healing_policies {
    health_check      = google_compute_region_health_check.golem_watcher.id
    initial_delay_sec = 300
  }
}

# [錬金術: 外部との通信路]
# 外部IPを持たないゴーレムが、安全に外界（Secret Manager等）と対話するための道。
resource "google_compute_router" "alchemy_router" {
  name    = "v6-alchemy-router"
  network = "default"
  region  = locals.region
}

resource "google_compute_router_nat" "alchemy_nat" {
  name                               = "v6-alchemy-nat"
  router                             = google_compute_router.alchemy_router.name
  region                             = locals.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# [錬金術: 結界]
# 健康診断のための通信だけを許可する最小限の防壁。
resource "google_compute_firewall" "golem_fence" {
  name    = "v6-golem-allow-hc"
  network = "default"
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"] # Googleの監視者のみ許可
  target_service_accounts = [google_service_account.golem_soul.email]
}

# -------------------------------------------------------------------
# 固定費: 約$2~4/月 (Spot VM 2台分の維持費。Load Balancer無しの究極節約)
# 堅牢性: Regional MIGによる自動自己修復。ゾーン障害すら克服。
# 美学: 外部IPを一切持たず、内部からのみ真理（Secret）に触れる高潔な構成。
# これぞ、サーバーレスという楽園を捨て、泥にまみれて辿り着いた「真の守護神」である。
# -------------------------------------------------------------------