from fastapi.routing import APIRouter
from fastapi import status, Response, Depends
from src.handlers.vector_store_handler import VectorStoreQdrant
from src.schemas.auth import User
from src.database.models.schemas import Users
from src.handlers.auth_handler import Authentication

router = APIRouter(prefix="/vectorstore")

@router.post('/create_collection',
             response_description='Create collection in Qdrant')
async def create_collection(
    response: Response,
    collection_name: str,
    current_user: User = Depends(Authentication.get_current_active_user)
):
    # Convert from User auth to Users object for VectorStoreQdrant
    user = Users(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role='ADMIN' if Authentication.is_admin(current_user.username) else 'USER'
    )
    
    resp = VectorStoreQdrant().create_qdrant_collection(collection_name, user)
    if resp.data:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return resp

@router.post('/delete_collection',
             response_description='Delete collection in Qdrant')
async def delete_collection(
    response: Response,
    collection_name: str,
    current_user: User = Depends(Authentication.get_current_active_user)
):
    user = Users(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role='ADMIN' if Authentication.is_admin(current_user.username) else 'USER'
    )
    
    resp = VectorStoreQdrant().delete_qdrant_collection(collection_name, user)
    if resp.data:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return resp

@router.get('/list_collections',
            response_description='List all collections in Qdrant')
async def list_collections(
    response: Response,
    current_user: User = Depends(Authentication.get_current_active_user)
):
    user = Users(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role='ADMIN' if Authentication.is_admin(current_user.username) else 'USER'
    )
    
    user.is_admin = Authentication.is_admin(current_user.username)

    try:
        collections = VectorStoreQdrant().list_qdrant_collections(user)
        response.status_code = status.HTTP_200_OK
        return {"status": "Success", "message": "List collections success", "data": collections}
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "Failed", "message": str(e), "data": None}