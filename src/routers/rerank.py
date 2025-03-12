from fastapi import APIRouter, Response, Query, status, Depends, Body
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, validator
import uuid
from src.schemas.response import BasicResponse
from src.handlers.rerank_handler import default_reranker

router = APIRouter()


class Candidate(BaseModel):
    content: str
    doc_id: Optional[str] = None

    @validator("doc_id", pre=True, always=True)
    def generate_doc_id(cls, value):
        if value is None or value == "":
            return str(uuid.uuid4())
        return value

class RerankRequest(BaseModel):
    candidates: List[Candidate]

@router.post("/rerank", response_description="Rerank")
async def rerank_endpoint(response: Response,
                    query: Annotated[str, Query()] = None,
                    threshold: Annotated[float, Query()] = 0.3,
                    request: RerankRequest = Body(include_in_schema=False), 
                    ):
    """
    Rerank candidates based on their relevance to the query.
    Uses the singleton reranker instance to avoid reloading models.
    
    Args:
        query (str): Query string for reranking
        threshold (float): Score threshold for filtering results
        request (RerankRequest): Request body with candidates
        
    Returns:
        BasicResponse: Response with reranked results
    """
    candidates = request.candidates
    try:
        result = default_reranker.process_candidates(candidates, query, threshold)

        result_response = BasicResponse(
            status="success",
            message="Reranking is successful!",
            data=result
        )
        response.status_code = status.HTTP_200_OK
    except Exception as e:
        # Create a failure response in case of any issues
        result_response = BasicResponse(
            status="fail",
            message=f"Reranking failed: {str(e)}",
            data=request.candidates
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return result_response

# from fastapi import APIRouter, Response, Query, status, Depends, Body
# from typing import Annotated, List, Optional
# from pydantic import BaseModel, Field, validator
# import uuid
# from src.schemas.response import BasicResponse
# from src.handlers.rerank_handler import RerankHandler

# rerank_handler = RerankHandler()
# router = APIRouter()


# class Candidate(BaseModel):
#     content: str
#     doc_id: Optional[str] = None

#     @validator("doc_id", pre=True, always=True)
#     def generate_doc_id(cls, value):
#         if value is None or value == "":
#             return str(uuid.uuid4())
#         return value

# class RerankRequest(BaseModel):
#     candidates: List[Candidate]

# @router.post("/rerank", response_description="Rerank")
# async def retriever(response: Response,
#                     query: Annotated[str, Query()] = None,
#                     threshold: Annotated[float, Query()] = 0.3,
#                     request: RerankRequest = Body(include_in_schema=False), 
#                     ):
#     candidates = request.candidates
#     query = query
#     threshold = threshold
#     try:
#         result = rerank_handler.process_candidates(candidates, query, threshold)

#         result_response = BasicResponse(
#             status="success",
#             message="Reranking is successful!",
#             data=result
#         )
#         response.status_code = status.HTTP_200_OK
#     except Exception as e:
#         # Create a failure response in case of any issues
#         result_response = BasicResponse(
#             status="fail",
#             message=f"Reranking failed: {str(e)}",
#             data=request.candidates
#         )
#         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

#     return result_response
