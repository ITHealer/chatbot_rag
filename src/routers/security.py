from fastapi.routing import APIRouter
from src.schemas.response import BasicResponse
from fastapi import status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.auth import Token, UserCreate, PasswordChange

from src.handlers.auth_handler import *


router = APIRouter()

@router.post('/token', response_description='Security')
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request) -> Token:
    user = Authentication.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session = request.session
    session['username'] = user.username
    access_token_expires = timedelta(minutes=auth_config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    access_token = Authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post('/register', response_description='Register a user')
async def register(user_create: UserCreate) -> Dict:
    user = Authentication.register_user(user_create)
    access_token = Authentication.create_access_token(
        data={"sub": user.username})
    return {"message": "user created successfully", "access_token": access_token}


@router.post('/create-admin', response_description='Create an admin user', response_model=BasicResponse)
async def create_admin(
    response: Response,
    user_create: UserCreate,
    current_user: User = Depends(Authentication().get_current_user)
):
    if not Authentication.is_admin(current_user.username):
        resp = BasicResponse(status='failed',
                          message='Only administrators can create admin accounts.')
        response.status_code = status.HTTP_403_FORBIDDEN
        return resp
    
    user_create.role = "ADMIN"
    
    try:
        user = Authentication.register_user(user_create)
        resp = BasicResponse(status='success',
                          message='Admin user created successfully.',
                          data=user.model_dump(exclude_none=True))
        response.status_code = status.HTTP_201_CREATED
    except HTTPException as e:
        resp = BasicResponse(status='failed',
                          message=e.detail)
        response.status_code = e.status_code
    
    return resp

@router.get('/get-current-user', description='Get current user', response_model=BasicResponse)
async def get_current_user(response: Response, current_user: User = Depends(Authentication().get_current_user)):
    if current_user:
        resp = BasicResponse(status='success',
                             message='Get session by user ID successfully.',
                             data=current_user.model_dump(exclude_none=True))
        response.status_code = status.HTTP_200_OK
    else:
        resp = BasicResponse(status='failed',
                             message='Get current user failed.')
        response.status_code = status.HTTP_400_BAD_REQUEST

    return resp


@router.post('/change-password', response_description='Change the password', response_model=BasicResponse)
async def change_password(response: Response,
                          request: PasswordChange,
                          active_user: UserInDB = Depends(Authentication().get_current_user)):
    if Authentication.change_password(active_user, request.username, request.old_password, request.new_password):
        resp = BasicResponse(status='success',
                             message='password changed successfully.')
        response.status_code = status.HTTP_200_OK
    else:
        resp = BasicResponse(status='success',
                             message='something went wrong with password change.')
        response.status_code = status.HTTP_400_BAD_REQUEST
    return resp
