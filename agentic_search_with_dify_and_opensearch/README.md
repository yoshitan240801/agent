# Agentic Search with Dify and OpenSearch

OpenSearch Agentic Search を利用した自然文商品検索システムのサンプル実装です。

検索対象の商品データに対して

- ベクトル検索（Amazon Nova Multimodal Embeddings）
- BM25検索
- Agentic Search (QueryPlanningTool)
- Claude (Dify Agent)

を組み合わせ、自然文から商品検索を行います。

画像・商品説明・商品名・特徴量を組み合わせた検索を行い、
LLMが検索結果をユーザ向けに分かりやすく要約します。

---

# Features

- OpenSearch Agentic Search
- QueryPlanningTool
- Amazon Nova Multimodal Embeddings
- Neural Search
- BM25 Search
- Bool Query
- Dify Agent
- FastAPI Middleware
- Claude Sonnet

---

# Architecture

```
                 User

                  │
                  ▼

          Dify Agent (Claude)

                  │
          Tool (OpenAPI)

                  │
                  ▼

             FastAPI

                  │

      OpenSearch Agentic Search

                  │

      QueryPlanningTool (LLM)

                  │

      OpenSearch DSL Generation

                  │

      Bool Query

        ├── Neural Search
        │      ├─ image_vector
        │      ├─ product_name_vector
        │      ├─ description_vector
        │      └─ features_vector
        │
        └── BM25 Search
               ├─ product_name
               ├─ description
               └─ features

                  │

          OpenSearch Index

                  │

          Search Results

                  │

            FastAPI

                  │

          Dify (Claude)

                  │

         User Friendly Answer
```

---

# Search Flow

```
User Query

    │

    ▼

Dify Agent

    │

Natural language

    │

    ▼

FastAPI

    │

OpenSearch Agentic Search

    │

QueryPlanningTool

    │

Generate DSL

    │

Bool Query

    ├── Neural Search
    └── BM25 Search

    │

Retrieve Products

    │

FastAPI

    │

JSON

    │

Dify Claude

    │

Summary

    │

User
```

---

# Repository Structure

```
agentic_search_with_dify_and_opensearch
│
├── dify
│   └── tool.yaml
│
├── fastapi
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   └── main.py
│
├── opensearch
│   ├── 01_connector_model_control.ipynb
│   ├── 02_agent_pipeline_control.ipynb
│   ├── 03_dbindex_control.ipynb
│   ├── 04_data_register.ipynb
│   └── 05_search.ipynb
│
└── README.md
```

---

# OpenSearch Index

Each product stores the following information.

| Field | Purpose |
|---------|----------|
| product_name | BM25 |
| description | BM25 |
| features | BM25 |
| product_name_vector | Semantic Search |
| description_vector | Semantic Search |
| features_vector | Semantic Search |
| image_vector | Image Similarity Search |
| sizes | Filter |
| prices | Filter |
| image_url | Display |
| page_url | Display |

---

# Search Strategy

The QueryPlanningTool dynamically generates an OpenSearch DSL.

The generated query combines:

- Neural Search
- BM25 Search
- Filters

using a `bool.should` query.

Typical Neural Search targets are:

- image_vector
- product_name_vector
- description_vector
- features_vector

Visual queries automatically increase the boost of `image_vector`.

Examples:

- red elegant bra
- gorgeous floral design
- cute lace
- luxurious atmosphere

Text-oriented queries increase the weight of textual vectors and BM25.

Examples:

- push-up
- hand washable
- polyester
- B70
- under 15000 yen

---

# Technologies

- OpenSearch
- OpenSearch Agentic Search
- QueryPlanningTool
- Amazon Bedrock
- Amazon Nova Multimodal Embeddings
- Claude Sonnet
- Dify
- FastAPI
- Docker

---

# Example Query

```
夏らしい明るい色で
B70
パッドあり
15000円以内
```

Generated search includes

- image similarity
- product semantic similarity
- feature semantic similarity
- BM25
- price filter
- size filter

---

# Future Improvements

Potential future enhancements include:

- Reranking
- Hybrid Search Score Optimization
- Image Caption Generation
- Personalization
- User Behavior Feedback
- Recommendation System
- Shopping Assistant

---

# License

MIT License