# -------------------------------------------------------------------
# Generation 0: The Sacrificial Lamb (生贄のコード)
# -------------------------------------------------------------------

provider "google" {
  project = "YOUR_GCP_PROJECT_ID"
  region  = "asia-northeast1"
}

# 1. たった1台の、しかもちょっと高いサーバー (e2-standard-2)
# 2. スポットVM設定なし（定価で課金される！）
# 3. 1箇所（aゾーン）だけに置いてあるので、そこが落ちたら即死
# 4. MIG（身代わり製造機）を使っていないので、壊れても復活しない

resource "google_compute_instance" "vulnerable_vm" {
  name         = "v0-lonely-server"
  machine_type = "e2-standard-2" # ちょっと贅沢な設定（AIに削らせたい！）
  zone         = "asia-northeast1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default" # セキュリティ設定もガバガバ
    access_config {
      # 外部IPも持たせちゃう（無駄なコスト）
    }
  }

  # ここに「スポットVM」や「MIG」の設定は一切なし！
  # AI「こんなの、サバイバル以前の問題だよ……」
}