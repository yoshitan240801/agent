import dotenv
import json
import os

import fastapi
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import requests


dotenv.load_dotenv()
OPENSEARCH_HOST = "https://host.docker.internal:10004"
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")

opensearch_bra_panty_index_name = "bra_panty_product_database"
opensearch_bra_panty_pipeline_name = "my-bra-and-panty-agentic-search-pipeline"


class SearchRequest(pydantic.BaseModel):
    query: str = pydantic.Field(description="""
    検索したい商品の内容を自然文で入力します。
    例:
    - ワンポイントの装飾があるようなショーツを探してます。Tバックでお願いします。
    - 15,000円以内で、明るめな色で鮮やかなデザインのブラジャーを探してます。Bカップです。パッドの有るものをお願いします。谷間を作れるものがイイです。
    """)


app = fastapi.FastAPI()
# CORS
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.post("/search_bra_and_panty_by_opensearch_agentic_search",
          summary="ブラジャー、ショーツ検索",
          description="ユーザの自然文を用いて、ブラジャーおよびショーツ商品情報の商品名、商品詳細、商品特徴、商品画像、サイズ、価格からLLMが自動でDSLを作成してエージェント検索によってブラジャーおよびショーツを検索します。商品名、商品詳細、商品特徴、商品画像はマルチモーダルモデルでエンベディングしたベクトルも考慮します。")
def search(req: SearchRequest):
    agentic_search_payload = {"_source": ["product",
                                          "category",
                                          "name",
                                          "description",
                                          "detail",
                                          "image_url",
                                          "product_url",
                                          "size_price"],
                              "size": 5,
                              "query": {"agentic": {"query_text": req.query}}}
    agentic_search_url = "{a}/{b}/_search?search_pipeline={c}".format(a=OPENSEARCH_HOST,
                                                                      b=opensearch_bra_panty_index_name,
                                                                      c=opensearch_bra_panty_pipeline_name)
    try:
        response = requests.post(url=agentic_search_url,
                                 auth=(OPENSEARCH_USER,
                                       OPENSEARCH_PASSWORD),
                                 headers={"Content-Type": "application/json"},
                                 json=agentic_search_payload,
                                 verify=False)
        formatted_answer_json_dict = {}
        formatted_answer_json_dict["dsl_query"] = json.loads(response.json()["ext"]["dsl_query"])
        search_results_list = []
        num = 1
        for obj in response.json()["hits"]["hits"]:
            search_result_dict = {}
            search_result_dict["rank"] = num
            search_result_dict["score"] = obj["_score"]
            search_result_dict["product"] = obj["_source"]["product"]
            search_result_dict["category"] = obj["_source"]["category"]
            search_result_dict["name"] = obj["_source"]["name"]
            search_result_dict["description"] = obj["_source"]["description"]
            search_result_dict["detail"] = obj["_source"]["detail"]
            search_result_dict["image_url"] = "![{a}]({b})".format(a=obj["_source"]["product"], b=obj["_source"]["image_url"])
            search_result_dict["product_url"] = obj["_source"]["product_url"]
            search_result_dict["size_price"] = obj["_source"]["size_price"]
            search_results_list.append(search_result_dict)
            num = int(num) + 1
        formatted_answer_json_dict["results"] = search_results_list
        return json.dumps(formatted_answer_json_dict,
                          ensure_ascii=False)
    except Exception as e:
        return {"message": str(e)}
