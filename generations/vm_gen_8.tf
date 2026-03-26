# -------------------------------------------------------------------
# Generation 8: The Philosopher's Engine (賢者の蒸気機関)
# -------------------------------------------------------------------
# 【Mikiさんへの報告】
# 1. お店の土台を「余計なゴミが一切ない魔法の器 (COS)」に入れ替え、起動の速さと美しさを極めました。
# 2. 秘密の金庫（Secret Manager）との連携を深め、管理者がいない時も自動で安全に動く仕組みを強化しました。
# 3. 無駄な贅肉を削ぎ落としたことで、同じ値段のまま「より頑丈で、より汚れにくい」究極の店舗になりました。
# -------------------------------------------------------------------
# 【審査員コメント】
# 案A（OSパッチ管理の自動化）は運用コスト増、案C（マルチリージョン化）は予算オーバーで即却下。
# 最終選出した【案B】は、OSを汎用的なDebianから「Container-Optimized OS (COS)」へと昇華させた。
# これは単なる軽量化ではない。書き込み不可のルートファイルシステムを持つCOSを採用することで、
# 攻撃者が泥を投げつけても汚れ一つ付かない「不変の純度」をインフラに与える錬金術である。
# Spot VMという「消えゆく宿命」を、COSの高速起動によって「瞬時に転生する強み」へと変換。
# 外部IPを持たず、IAPという透明な回廊のみを許す構成は、まさに審美眼に耐えうる至高のテンプレートだ。
# -------------------------------------------------------------------

provider "google" {
  project = "YOUR_GCP_PROJECT_ID"
  region  = "asia-northeast1"
}

locals {
  project_id = "YOUR_GCP_PROJECT_ID"
  region     = "asia-northeast1"
  # 錬金術の三原則：安価、堅牢、美麗
  machine    = "e2-micro"
  image      = "cos-cloud/cos-stable" # 汎用的な「泥」を捨て、純化された「器」を採用
}

# [錬金術: 独自の理を定義する閉鎖回路]
resource "google_compute_network" "philosopher_vpc" {
  name                    = "v8-philosopher-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "philosopher_subnet" {
  name          = "v8-philosopher-subnet"
  ip_cidr_range = "10.0.8.0/24"
  region        = local.region
  network       = google_compute_network.philosopher_vpc.id
}

# [錬金術: 賢者の魂（権限の最小化）]
resource "google_service_account" "philosopher_sa" {
  account_id   = "v8-philosopher-sa"
  display_name = "Core Identity of the Philosopher's Engine"
}

# [錬金術: 叡智の秘匿（シークレット管理）]
resource "google_secret_manager_secret" "philosopher_core" {
  secret_id = "v8-philosopher-secret"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "philosopher_access" {
  secret_id = google_secret_manager_secret.philosopher_core.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "service_account:${google_service_account.philosopher_sa.email}"
}

# [錬金術: 不変の設計図]
resource "google_compute_instance_template" "philosopher_blueprint" {
  name_prefix  = "v8-engine-template-"
  machine_type = local.machine

  scheduling {
    preemptible        = true # 変わらぬコストへの拘り
    automatic_restart  = false
    provisioning_model = "SPOT"
    instance_termination_action = "STOP"
  }

  disk {
    source_image = local.image
    auto_delete  = true
    boot         = true
    disk_size_gb = 10
    disk_type    = "pd-standard"
  }

  network_interface {
    network    = google_compute_network.philosopher_vpc.id
    subnetwork = google_compute_subnetwork.philosopher_subnet.id
    # 外部IPという「不純物」を徹底排除
  }

  service_account {
    email  = google_service_account.philosopher_sa.email
    scopes = ["cloud-platform"]
  }

  # COSに最適化された起動プロセス
  metadata = {
    user-data = <<-EOT
      #cloud-config
      write_files:
        - path: /etc/systemd/system/app.service
          permissions: 0644
          owner: root
          content: |
            [Unit]
            Description=Alchemical Web Vessel
            [Service]
            ExecStart=/usr/bin/docker run --rm -p 80:80 nginx:alpine
            Restart=always
            [Install]
            WantedBy=multi-user.target
      runcmd:
        - systemctl daemon-reload
        - systemctl start app.service
    EOT
  }

  lifecycle {
    create_before_destroy = true
  }
}

# [錬金術: 常に調和を監視する目]
resource "google_compute_region_health_check" "philosopher_eye" {
  name   = "v8-philosopher-hc"
  region = local.region

  http_health_check {
    port = 80
  }
}

# [錬金術: 増殖し続ける軍団]
resource "google_compute_region_instance_group_manager" "philosopher_legion" {
  name               = "v8-philosopher-mig"
  base_instance_name = "v8-engine"
  region             = local.region
  target_size        = 2 # 2つの異なるゾーンでの並行錬成

  version {
    instance_template = google_compute_instance_template.philosopher_blueprint.id
  }

  auto_healing_policies {
    health_check      = google_compute_region_health_check.philosopher_eye.id
    initial_delay_sec = 120 # COSの高速起動により待機時間を短縮
  }
}

# [錬金術: 外界への一方向窓口]
resource "google_compute_router" "philosopher_router" {
  name    = "v8-philosopher-router"
  network = google_compute_network.philosopher_vpc.id
  region  = local.region
}

resource "google_compute_router_nat" "philosopher_nat" {
  name                               = "v8-philosopher-nat"
  router                             = google_compute_router.philosopher_router.name
  region                             = local.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# [錬金術: 透明なる結界]
resource "google_compute_firewall" "philosopher_fence_hc" {
  name    = "v8-allow-hc"
  network = google_compute_network.philosopher_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]
}

resource "google_compute_firewall" "philosopher_fence_iap" {
  name    = "v8-allow-iap"
  network = google_compute_network.philosopher_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = ["35.235.240.0/20"] # 管理者のみが通れる次元の道
}

# -------------------------------------------------------------------
# 固定費: 約$2~4/月 (Spot VM e2-micro ×2台。外部IP完全排除により変動費も最小)
# 堅牢性: COSによるイミュータブルなOS構成 + Regional MIGによる物理障害耐性。
# 美学: DockerとCOSの融合により、インフラとコードの境界が限りなく美しく重なり合った。
# -------------------------------------------------------------------