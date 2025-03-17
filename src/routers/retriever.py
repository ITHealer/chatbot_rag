from fastapi import APIRouter, Response, Query, status
from typing import Annotated
from src.handlers.retrieval_handler import default_search_retrieval
from src.utils.config import settings
from src.schemas.response import BasicResponse

router = APIRouter()

@router.post("/retriever", response_description="Retriever")
async def retriever(response: Response,
                    query: Annotated[str, Query()],
                    top_k: Annotated[int, Query()] = 5,
                    collection_name: Annotated[str, Query()] = settings.QDRANT_COLLECTION_NAME
                ):
    """
    Retrieve and rerank documents from the vector database.
    Uses singleton instance to avoid reloading models.
    
    Args:
        query (str): Query string for retrieval
        top_k (int): Number of top results to return
        collection_name (str): Name of the collection to search
        
    Returns:
        BasicResponse: Response with retrieved documents
    """
    # Use the singleton instance instead of creating a new one
    resp = await default_search_retrieval.qdrant_retrieval(query, top_k, collection_name)
    
    if resp:
        response.status_code = status.HTTP_200_OK
        data= [docs.json() for docs in resp]
        return BasicResponse(status="Success",
                         message="Success retriever data from qdrant",
                         data=data)
    else:
        return BasicResponse(status="Failed",
                         message="Failed retriever data from qdrant",
                         data=resp)

# from fastapi import APIRouter, Response, Query, status, Depends
# from typing import Annotated
# from src.handlers.retrieval_handler import SearchRetrieval
# from src.utils.config import settings
# from src.schemas.response import BasicResponse

# router = APIRouter()

# @router.post("/retriever", response_description="Retriever")
# async def retriever(response: Response,
#                     query: Annotated[str, Query()],
#                     top_k: Annotated[int, Query()] = 5,
#                     collection_name: Annotated[str, Query()] = settings.QDRANT_COLLECTION_NAME
#                 ):
    
#     resp = await SearchRetrieval().qdrant_retrieval(query, top_k, collection_name)
#     if resp:
#         response.status_code = status.HTTP_200_OK
#         data= [docs.json() for docs in resp]
#         return BasicResponse(status="Success",
#                          message="Success retriever data from qdrant",
#                          data=data)
#     else:
#         return BasicResponse(status="Failed",
#                          message="Failed retriever data from qdrant",
#                          data=resp)