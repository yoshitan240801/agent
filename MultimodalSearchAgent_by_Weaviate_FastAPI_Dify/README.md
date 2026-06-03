# Weaviate Hybrid Search + FastAPI + Dify Agent Sample

## Overview

本リポジトリは、Weaviate Cloud を利用したマルチモーダル検索システムのサンプルです。

商品画像、説明文、タグ情報を Weaviate Cloud に登録し、自然文による商品検索を実現します。

検索APIは FastAPI で実装し、Dify Agent の Custom Tool から利用する構成を想定しています。

---

## Features

* Weaviate Cloud によるベクトル検索
* Gemini Embedding を利用したマルチモーダル埋め込み
* Hybrid Search（Vector Search + BM25）
* FastAPI による REST API 化
* Docker コンテナによるデプロイ
* Dify Agent との連携
* 自然文検索
* Query Expansion による曖昧検索対応

---

## Architecture

```text
+-------------------+
|      User         |
+---------+---------+
          |
          v
+-------------------+
|   Dify Agent      |
|       Claude      |
+---------+---------+
          |
          v
+-------------------+
|  FastAPI Server   |
|  (Relay API)      |
+---------+---------+
          |
          v
+-------------------+
| Weaviate Cloud    |
| Hybrid Search     |
+---------+---------+
          |
          v
+-------------------+
| Gemini Embedding  |
+-------------------+
```

---

## Repository Structure

```text
.
├── RelayAPIServer
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   └── work
│       ├── .env
│       └── main.py
│
├── manage_weaviate_cloud.ipynb
│
├── openapi.yaml
│
└── README.md
```

---

## Files

### manage_weaviate_cloud.ipynb

Weaviate Cloud の構築用 Notebook です。

主な内容:

* Collection作成
* Property定義
* Vectorizer設定
* Gemini Embedding設定
* データ登録
* Hybrid Search検証
* Query Agent検証

---

### RelayAPIServer/work/main.py

FastAPI による検索APIです。

実装内容:

* Weaviate Cloud接続
* Hybrid Search実行
* 検索結果整形
* REST API公開

エンドポイント:

```text
POST /search_product_database_by_weaviate_hybrid_search
```

---

### Dockerfile

FastAPI サーバのコンテナイメージ作成用です。

---

### docker-compose.yaml

FastAPI サーバ起動用です。

---

### openapi.yaml

Dify Custom Tool 登録用 OpenAPI Specification です。

---

## Environment Variables

`.env`

```env
GOOGLE_AI_STUDIO_API_KEY=xxxxxxxx
WEAVIATE_API_KEY=xxxxxxxx
WEAVIATE_URL=https://xxxx.weaviate.network
```

---

## FastAPI Startup

```bash
docker compose up -d
```

確認:

```bash
http://localhost:10002/docs
```

OpenAPI:

```bash
http://localhost:10002/openapi.json
```

---

## Example Request

```bash
curl -X POST \
"http://localhost:10002/search_product_database_by_weaviate_hybrid_search" \
-H "Content-Type: application/json" \
-d '{
  "query": "白の無地パーカー"
}'
```

---

## Hybrid Search

検索は Weaviate の Hybrid Search を利用しています。

```python
response = collection.query.hybrid(
    query=query,
    alpha=0.75,
    limit=5
)
```

### Search Targets

* description
* tags
* image embedding

### alpha

```text
alpha = 1.0
    → Vector Searchのみ

alpha = 0.0
    → BM25のみ

alpha = 0.75
    → Vector Search寄り
```

---

## Dify Integration

Dify Agent の Custom Tool として利用できます。

Dify Agent は以下を担当します。

* Query Expansion
* 曖昧表現の解釈
* Tool選択
* 検索結果要約

---

## Example Queries

```text
白の無地パーカー

オフィスでも使いやすい腕時計

シンプルで落ち着いた雰囲気のバッグ

インナーとして使える薄手のロングTシャツ
```

---

## Future Work

* Query Agent の活用
* Reranking
* Recommendation機能
* Metadata Filter
* Multi Collection Search
* Bedrock連携
* User Preference Learning

---

## Notes

本リポジトリは学習・検証用サンプルです。

APIキー等の機密情報は含まれていません。
