import dotenv
import json
import os

import fastapi
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import requests


dotenv.load_dotenv()
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")

opensearch_index_name = "my-index-name"
opensearch_pipeline_name = "my-pipeline-name"


class SearchRequest(pydantic.BaseModel):
    query: str = pydantic.Field(description="""
    検索したい商品の内容を自然文で入力します。
    例:
    - 10,000円前後でセクシーなものを探してます。
    - 15,000円以内で、明るめな色で鮮やかなデザインのブラジャーを探してます。Bカップです。パッドの有るものをお願いします。谷間を作れるものがイイです。
    """)


app = fastapi.FastAPI()
# CORS
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"])

@app.post("/search_bra_by_opensearch_agentic_search",
          summary="ブラジャー検索",
          description="ユーザの自然文を用いて、ブラジャー商品情報の商品名、商品詳細、商品特徴、商品画像、サイズ、価格からLLMが自動でDSLを作成して検索するエージェント検索でブラジャーを検索します。商品名、商品詳細、商品特徴、商品画像はマルチモーダルモデルでエンベディングしたベクトルも考慮します。")
def search(req: SearchRequest):
    try:
        agentic_search_payload = {"_source": ["product_name",
                                              "description",
                                              "features",
                                              "image_url",
                                              "page_url",
                                              "sizes",
                                              "prices"],
                                  "size": 5,
                                  "query": {"agentic": {"query_text": req.query}}}
        agentic_search_url = "{a}/{b}/_search?search_pipeline={c}".format(a=OPENSEARCH_HOST,
                                                                          b=opensearch_index_name,
                                                                          c=opensearch_pipeline_name)
        response = requests.post(url=agentic_search_url,
                                 auth=(OPENSEARCH_USER,
                                       OPENSEARCH_PASSWORD),
                                 headers={"Content-Type": "application/json"},
                                 json=agentic_search_payload,
                                 verify=False
                                )
        formatted_answer_json_dict = {}
        formatted_answer_json_dict["dsl_query"] = json.loads(response.json()["ext"]["dsl_query"])
        search_results_list = []
        num = 1
        for obj in response.json()["hits"]["hits"]:
            search_result_dict = {}
            search_result_dict["rank"] = num
            search_result_dict["score"] = obj["_score"]
            search_result_dict["product_name"] = obj["_source"]["product_name"]
            search_result_dict["description"] = obj["_source"]["description"]
            search_result_dict["features"] = obj["_source"]["features"]
            search_result_dict["sizes"] = obj["_source"]["sizes"]
            search_result_dict["prices"] = obj["_source"]["prices"]
            search_result_dict["image_url"] = "![{a}]({b})".format(a=obj["_source"]["product_name"], b=obj["_source"]["image_url"])
            search_result_dict["page_url"] = obj["_source"]["page_url"]
            search_results_list.append(search_result_dict)
            num = int(num) + 1
        formatted_answer_json_dict["results"] = search_results_list
        return json.dumps(formatted_answer_json_dict,
                          ensure_ascii=False)
    except Exception as e:
        return {"message": str(e)}


@app.on_event("shutdown")
def shutdown_event():
    pass