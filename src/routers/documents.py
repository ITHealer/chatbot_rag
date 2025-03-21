import os
import mimetypes
import asyncio
from typing import List, Optional
from fastapi import Response, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from fastapi import UploadFile, Query, Body, File

from src.schemas.response import BasicResponse
from src.schemas.base import DocumentIds

from src.handlers.auth_handler import Authentication
from src.handlers.data_ingestion_handler import DataIngestion
from src.handlers.file_partition_handler import DocumentExtraction

# from src.database.repository.user_repository import UserRepository
from src.database.repository.user_orm_repository import UserORMRepository
from src.database.repository.file_repository import FileProcessingRepository, FileProcessingVecDB
from src.utils.constants import (
    LLMModelName,
    TypeDatabase,
    TypeDocument,
)

auth = Authentication()
router = APIRouter(prefix="/document", dependencies=[Depends(auth.get_current_user)])

user_repo = UserORMRepository()
data_ingestion = DataIngestion()
document_extraction = DocumentExtraction()
file_repo = FileProcessingRepository()
file_vecdb = FileProcessingVecDB()


@router.get("/search", response_description="Get all documents by search engine")
async def get_files(
    response: Response,
    key_word: Optional[str] = Query(None, description="Search by keyword"),
    file_type: Optional[str] = Query(
        None, enum=TypeDocument.list(), description="Search by type: pdf/word/image..."
    ),
    created_at: Optional[str] = Query(None, description="Search by creation date"),
    limit: Optional[int] = Query(10, description="Limit the number of results"),
    offset: Optional[int] = Query(0, description="Skip records for pagination"),
):
    try:
        extension_map = {
            "pdf": "application/pdf",
            "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image": "image%",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }

        default_extension = None
        extension = extension_map.get(file_type, default_extension)
        files = file_repo.get_files_by_search_engine(
            key_word, extension, created_at, limit, offset
        )

        if files:
            resp = BasicResponse(
                status="success",
                message="Successfully retrieved all files.",
                data=files,
            )
            response.status_code = status.HTTP_200_OK
        else:
            resp = BasicResponse(
                status="failed",
                message="No files found matching the search criteria.",
                data=None,
            )
            response.status_code = status.HTTP_404_NOT_FOUND

    except Exception as e:
        resp = BasicResponse(
            status="error", message=f"An error occurred: {str(e)}", data=None
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return resp


@router.delete("/delete", response_description="Delete documents by file_name")
async def delete_files(
    response: Response,
    file_name: Optional[str] = Query(
        None,
        description="File name with extension (e.g., file.pdf, file.docx, file.pptx)",
    ),
    type_db: str = Query(
        default=TypeDatabase.Qdrant.value,
        enum=TypeDatabase.list(),
        description="Select vector database type",
    ),
):
    if file_name is None or file_name.strip() == "":
        resp = BasicResponse(
            status="warning",
            message="File name is not provided or is empty. Please check the inputted name again.",
        )
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp

    file_extension = os.path.splitext(file_name)[1]
    if file_extension == "":
        resp = BasicResponse(
            status="warning",
            message="File name is not provided or is empty. Please check the inputted name again.",
        )
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp

    file_repo.delete_document_by_file_name(file_name)
    await file_vecdb.delete_document_by_file_name(file_name, type_db=type_db)

    response.status_code = status.HTTP_200_OK
    resp = BasicResponse(
                status="success",
                message="Successfully deleted document from repository and vector database.",
           )
    return resp


@router.delete("/batch-delete", response_description="Batch delete documents by id")
async def batch_delete_files(
    response: Response,
    type_db: str = Query(
        default=TypeDatabase.Qdrant.value,
        enum=TypeDatabase.list(),
        description="Select vector database type",
    ),
    document_ids: DocumentIds = Body(None, description="List of documents id"),
):
    doc_ids = document_ids.document_ids
    if not doc_ids:
        resp = BasicResponse(
            status="warning",
            message="document_ids is empty. Please check the inputted again.",
        )
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    doc_file_names = [
        file_name[0]
        for doc_id in doc_ids
        if (file_name := file_repo.get_document_by_id(document_id=doc_id)) is not None
    ]
    file_repo.delete_document_by_batch_ids(document_ids=doc_ids)
    await file_vecdb.delete_document_by_batch_ids(document_ids=doc_ids, type_db=type_db)
  
    response.status_code = status.HTTP_200_OK
    resp = BasicResponse(
                status="success",
                message="Successfully batch deleted documents.",
           )
    
    return resp


@router.post(
    "/upload",
    response_description="Upload document, extract text, and store in vector database",
)
async def upload_document(
    response: Response,
    collection_name: str = Query(..., description="Qdrant collection name to store the document"),
    backend: str = Query("pymupdf", description="Text extraction backend (pymupdf or docling)"),
    files: List[UploadFile] = File(..., description="Document files to upload"),
):
    async def process_file(file: UploadFile):
        try:
            result = await data_ingestion.ingest(
                file=file,
                collection_name=collection_name,
                backend=backend
            )
            return BasicResponse(
                status="success",
                message=f"Successfully processed file {file.filename}",
                data=result.get("data")
            )
        except Exception as e:
            return BasicResponse(
                status="error",
                message=f"Failed to process file {file.filename}: {str(e)}",
                data=None
            )

    tasks = [process_file(file) for file in files]
    results = await asyncio.gather(*tasks)

    successful_results = [result for result in results if result.status == "success"]
    
    if successful_results:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    
    return results


@router.post(
    "/extract",
    response_description="Extract text from documents without storing in vector database",
)
async def extract_text(
    response: Response,
    backend: str = Query("pymupdf", description="Text extraction backend (pymupdf or docling)"),
    files: List[UploadFile] = File(..., description="Document files to process"),
):
    async def process_file(file: UploadFile):
        try:
            file_data = await file.read()
            temp_file_path = data_ingestion._save_temp_file(file.filename, file_data)
            document_id = str(os.path.basename(temp_file_path))
            
            # Extract text
            result = await document_extraction.extract_text(
                file=file,
                backend=backend,
                temp_file_path=temp_file_path,
                document_id=document_id
            )
            
            if result.status == "success" and result.data is not None:
                serializable_docs = []
                for doc in result.data:
                    serializable_docs.append({
                        "page_content": doc.page_content,
                        "metadata": doc.metadata
                    })
                
                return BasicResponse(
                    status=result.status,
                    message=result.message,
                    data=serializable_docs
                )
            
            return result
        except Exception as e:
            return BasicResponse(
                status="error",
                message=f"Failed to extract text from {file.filename}: {str(e)}",
                data=None
            )
        finally:
            await file.seek(0)

    tasks = [process_file(file) for file in files]
    results = await asyncio.gather(*tasks)

    successful_results = [result for result in results if result.status == "success"]
    
    if successful_results:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    
    return results