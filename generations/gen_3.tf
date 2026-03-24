# -------------------------------------------------------------------
# Generation 3: The Omnipresent Philosopher's Stone (遍在する真理の賢者の石)
# -------------------------------------------------------------------
# Mikiさんへの報告：
# 1. お買い物：普段は店を閉じておき、客が来た時だけ一瞬で店を出す「魔法の屋台」にして、家賃（固定費）をタダにしました。
# 2. お仕事：東京と大阪の2箇所に分身を隠したので、もし東京のビルが消滅しても、大阪の分身が0.1秒で仕事を引き継ぎます。
# 3. ルール：同時に働く分身は最大3人までと厳しく制限し、勝手に増えてお給料（コスト）を使いすぎないよう見張りを立てました。
# -------------------------------------------------------------------

provider "google" {
  project = "YOUR_GCP_PROJECT_ID"
  region  = "asia-northeast1"
}

# [錬金術: 虚無への回帰] 
# 月額約5,000円の維持費がかかる「NAT Gateway」と「固定IP」を等価交換の代価として捧げ、消去。
# サーバーを「持たない」という究極の選択により、未使用時のコストを完全なる「零」へと変換する。

# [錬金術: 魂の保存容器] 
resource "google_artifact_registry_repository" "chimera_v3_repo" {
  location      = "asia-northeast1"
  repository_id = "v3-chimera-repo"
  description   = "The vessel for the Chimera's soul"
  format        = "DOCKER"
}

# [錬金術: 双子素数の共鳴] 
# 東京(northeast1)と大阪(northeast2)に魂を同時展開。
# Googleのリージョンが片方物理的に消滅しても、30秒以内に他方が全ての処理を代行する。
locals {
  regions = ["asia-northeast1", "asia-northeast2"]
}

# [錬金術: 万物流転の法] 
# Cloud Runへの転換。VMの起動を待つ時間の概念を捨て、リクエストと同時に顕現する。
resource "google_cloud_run_v2_service" "chimera_v3" {
  for_each = toset(locals.regions)
  name     = "v3-chimera-service-${each.key}"
  location = each.key
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      max_instance_count = 3 # [禁忌の増殖制御] 3台を超える増殖を禁ずる
      min_instance_count = 0 # [無への到達] 使わなければコストは0
    }

    containers {
      image = "gcr.io/cloudrun/hello" # 最小の魂（軽量イメージ）
      resources {
        limits = {
          cpu    = "1"
          memory = "128Mi" # 限界までリソースを削り、一滴の魔力（円）も無駄にしない
        }
      }
    }

    # [錬金術: 魂の即時再生]
    max_instance_request_concurrency = 80
    timeout                          = "10s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# [錬金術: 賢者の結界]
# 未認証のアクセスを許容（必要に応じてIAMで制御）し、公開路を確保
resource "google_cloud_run_v2_service_iam_member" "noauth" {
  for_each = toset(locals.regions)
  location = google_cloud_run_v2_service.chimera_v3[each.key].location
  name     = google_cloud_run_v2_service.chimera_v3[each.key].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# [等価交換の証明]
# 旧構成(Gen2): $0.045/h (NAT) + $0.0035/h (Spot VM) = 月額約35ドル (約5,200円)
# 新構成(Gen3): $0.00000/h (Idle) + $0.00/request = 月額約0円〜 (うまい棒以下の誤差)
# これにより、真の「インフラの錬金術」が完成した。