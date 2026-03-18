from fastapi import FastAPI, Query
from typing import Optional, List
from opensearchpy import OpenSearch
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Search Service")
INDEX_NAME = "products"


def get_client():
    # For AWS OpenSearch, endpoint is https://... — strip the scheme for the host
    host = settings.opensearch_endpoint.replace("https://", "").replace("http://", "").rstrip("/")
    use_ssl = settings.opensearch_endpoint.startswith("https")
    return OpenSearch(
        hosts=[{"host": host, "port": 443 if use_ssl else 9200}],
        http_auth=(settings.opensearch_username, settings.opensearch_password),
        use_ssl=use_ssl,
        verify_certs=use_ssl,
    )


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting Search Service")
    logger.info(f"  Environment: {settings.environment}")
    logger.info(f"  OpenSearch: {settings.opensearch_endpoint}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "search-service"}


@app.get("/search")
def search(
    q: Optional[str] = Query(None, description="Full-text search query"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    if not q and not category:
        return []

    must_clauses = []
    if q:
        must_clauses.append({
            "multi_match": {
                "query": q,
                "fields": ["name^3", "description", "category"],
                "fuzziness": "AUTO"
            }
        })
    if category:
        must_clauses.append({"term": {"category.keyword": category}})

    body = {
        "query": {"bool": {"must": must_clauses}},
        "size": 50
    }

    try:
        client = get_client()
        response = client.search(index=INDEX_NAME, body=body)
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
