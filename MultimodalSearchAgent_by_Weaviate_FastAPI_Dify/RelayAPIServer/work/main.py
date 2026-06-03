import dotenv
import os

import fastapi
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.query import MetadataQuery


dotenv.load_dotenv()
GOOGLE_AI_STUDIO_API_KEY = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
GOOGLE_AI_STUDIO_PROJECT_ID = os.getenv("GOOGLE_AI_STUDIO_PROJECT_ID")


class SearchRequest(pydantic.BaseModel):
    query: str = pydantic.Field(description="""
    検索したい商品を自然文で入力します。
    例:
    - 無地もしくはワンポイントのデザインで白のパーカー
    - インナーとしても使えそうな薄手の生地のロングTシャツで色は控えめで無地
    - オフィスでも付けれる派手過ぎず大人しすぎずな腕時計
    """)


app = fastapi.FastAPI()
# CORS
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"])

header = {"X-Goog-Studio-Api-Key": GOOGLE_AI_STUDIO_API_KEY}
client = weaviate.connect_to_weaviate_cloud(cluster_url=WEAVIATE_URL,
                                            auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
                                            headers=header)
collection = client.collections.get("product_database")


@app.post("/search_product_database_by_weaviate_hybrid_search",
          summary="商品検索",
          description="ユーザの自然文を用いて、商品をマルチモーダル検索とタグ検索のハイブリッドで検索します。説明文、画像、タグを考慮して検索を行います。")
def search(req: SearchRequest):
    try:
        response = collection.query.hybrid(query=req.query,
                                           alpha=0.75,
                                           return_metadata=MetadataQuery(score=True,
                                                                         explain_score=False),
                                           limit=5)
        formatted_answer_list = []
        for obj in response.objects:
            formatted_answer = (
                    "商品名: {a}\n"
                    "説明: {b}\n"
                    "スコア: {d}\n"
                    "![{a}]({c})"
            ).format(a=obj.properties["name"], b=obj.properties["description"], c=obj.properties["image_url"], d=obj.metadata.score)
            formatted_answer_list.append(formatted_answer)
        return {"message": "\n\n".join(formatted_answer_list)}
    except Exception as e:
        return {"message": str(e)}


@app.on_event("shutdown")
def shutdown_event():
    client.close()