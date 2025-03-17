from src.utils.logger.custom_logging import LoggerMixin
from src.helpers.qdrant_connection_helper import QdrantConnection
from src.schemas.response import BasicResponse
from src.database.models.schemas import Users
from src.database.services.collection_management_service import CollectionManagementService

class VectorStoreQdrant(LoggerMixin):
    def __init__(self) -> None:
        super().__init__()
        self.qdrant = QdrantConnection()
        self.collection_service = CollectionManagementService()

    def create_qdrant_collection(self, collection_name: str, user: Users):
        resp = BasicResponse(status="Success",
                             message="create qdrant collection success.",
                             data=collection_name)
        try:
            if not self.qdrant.client.collection_exists(collection_name=collection_name):
                # 1. Tạo collection trong Qdrant vector database
                is_created = self.qdrant._create_collection(collection_name)
                
                if is_created:
                    # 2. Lưu metadata vào PostgreSQL
                    try:
                        # Tạo record trong bảng vectorstore_collection
                        collection_id = self.collection_service.create_collection(
                            collection_name=collection_name,
                            user_id=user.id
                        )
                        self.logger.info(f"Collection metadata saved with ID: {collection_id}")
                        resp.message = f"create qdrant collection '{collection_name}' success."
                    except Exception as db_error:
                        # Nếu lưu vào PostgreSQL thất bại, ghi log nhưng vẫn coi như thành công
                        # vì collection đã được tạo trong Qdrant
                        self.logger.error(f"Created Qdrant collection but failed to save metadata: {str(db_error)}")
                        resp.message = f"create qdrant collection '{collection_name}' success (metadata save failed)."
                else:
                    resp.message = f"create qdrant collection '{collection_name}' failed."
                    resp.status = "Failed"
                    resp.data = None
            else:
                resp.message = f"collection '{collection_name}' already exist."
                resp.status = "Failed"
                resp.data = None
            
            return resp
        except Exception as e:
            self.logger.error(f"create qdrant collection '{collection_name}' failed. Detail error: {str(e)}")
            return BasicResponse(status="Failed",
                                 message=f"Create qdrant collection {collection_name} failed. Detail error: {str(e)}",
                                 data=None)
        
    def delete_qdrant_collection(self, collection_name: str, user: Users):
        try:
            # 1. Kiểm tra xem collection có tồn tại trong Qdrant không
            if self.qdrant.client.collection_exists(collection_name=collection_name):
                # 2. Kiểm tra quyền sở hữu qua PostgreSQL
                is_owner = self.collection_service.is_collection_owner(
                    user_id=user.id, 
                    collection_name=collection_name
                )
                
                # Admin luôn có quyền xóa bất kỳ collection nào
                if user.role == 'ADMIN':
                    is_owner = True
                
                if is_owner:
                    # 3. Xóa collection từ Qdrant
                    self.qdrant._delete_collection(collection_name)
                    
                    # 4. Xóa metadata từ PostgreSQL
                    try:
                        self.collection_service.delete_collection(collection_name)
                    except Exception as db_error:
                        self.logger.error(f"Deleted Qdrant collection but failed to remove metadata: {str(db_error)}")
                    
                    return BasicResponse(status="Success",
                                        message=f"Delete qdrant collection '{collection_name}' success.",
                                        data=collection_name)
                else:
                    return BasicResponse(status="Failed",
                                        message=f"User is not owner of {collection_name} collection",
                                        data=None)
            else:
                return BasicResponse(status="Failed",
                                    message=f"Collection {collection_name} is not exist.",
                                    data=None)
        except Exception as e:
            self.logger.error(f"Delete qdrant collection '{collection_name}'failed. Detail error: {str(e)}")
            return BasicResponse(status="Failed",
                                 message=f"Delete qdrant collection '{collection_name}'failed. Detail error: {str(e)}",
                                 data=None)
    
    def list_qdrant_collections(self, user: Users = None):
        try:
            # 1. Lấy danh sách tất cả collection từ Qdrant
            collections = self.qdrant.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if user.role == 'ADMIN':
                # Admin có thể xem tất cả collection
                return collection_names
            
            # 2. Lọc các collection thuộc quyền sở hữu của user từ PostgreSQL
            try:
                user_collections = self.collection_service.get_user_collections(user.id)
                
                # 3. Lấy giao của 2 danh sách (collections tồn tại cả trong Qdrant và PostgreSQL)
                return list(set(collection_names).intersection(set(user_collections)))
            except Exception as db_error:
                self.logger.error(f"Error fetching user collections: {str(db_error)}")
                # Nếu không thể lấy từ DB, trả về danh sách rỗng
                return []
        except Exception as e:
            self.logger.error(f"List qdrant collections failed. Detail error: {str(e)}")
            raise Exception(f"List qdrant collections failed: {str(e)}")

# from src.utils.logger.custom_logging import LoggerMixin
# from src.helpers.qdrant_connection_helper import QdrantConnection
# from src.schemas.response import BasicResponse
# # from src.database.data_layer_access.file_dal import FileManagementDAL
# from src.database.models.schemas import Users
# from src.database.data_layer_access.vectorstore_dal import VectorStoreDAL

# class VectorStoreQdrant(LoggerMixin):
#     def __init__(self) -> None:
#         super().__init__()
#         self.qdrant = QdrantConnection()

#     def create_qdrant_collection(self, collection_name: str, user: Users):
#         resp = BasicResponse(status="Success",
#                              message="create qdrant collection success.",
#                              data=collection_name)
#         try:
#             if not self.qdrant.client.collection_exists(collection_name=collection_name):
#                 is_created = self.qdrant._create_collection(collection_name)
#                 VectorStoreDAL().create_vector_store_collection(user.id, collection_name)
#                 if is_created:
#                     resp.message = f"create qdrant collection '{collection_name}' success."
#                 else:
#                     resp.message = f"create qdrant collection '{collection_name}' failed."
#                     resp.status = "Failed"
#                     resp.data = None
#             else:
#                 resp.message = f"collection '{collection_name}' already exist."
#                 resp.status = "Failed"
#                 resp.data = None
            
#             return resp
#         except Exception as e:
#             self.logger.error(f"create qdrant collection '{collection_name}' failed. Detail error: {str(e)}")
#             return BasicResponse(status="Failed",
#                                  message=f"Create qdrant collection {collection_name} failed. Detail error: {str(e)}",
#                                  data=None)
        
#     def delete_qdrant_collection(self, collection_name: str, user: Users):
#         try:
#             vectorstore_dal = VectorStoreDAL()
#             if vectorstore_dal.collection_own_by_user(user.id, collection_name):
#                 if self.qdrant.client.collection_exists(collection_name=collection_name):
                    
#                     self.qdrant._delete_collection(collection_name)
#                     # FileManagementDAL().delete_record_by_collection(collection_name=collection_name)
#                     # minio_storage.delete_folder_collection(collection_name=collection_name)
#                     vectorstore_dal.delete_vector_store_collection(user.id, collection_name)
#                     return BasicResponse(status="Success",
#                                         message=f"Delete qdrant collection '{collection_name}' success.",
#                                         data=collection_name)
#                 return BasicResponse(status="Failed",
#                                         message=f"Collection {collection_name} is not exist.",
#                                         data=None)
            
#             return BasicResponse(status="Failed",
#                                         message=f"User is not own {collection_name} collection",
#                                         data=None)

#         except Exception as e:
#             self.logger.error(f"Delete qdrant collection '{collection_name}'failed. Detail error: {str(e)}")
#             return BasicResponse(status="Failed",
#                                  message=f"Delete qdrant collection '{collection_name}'failed. Detail error: {str(e)}",
#                                  data=None)
    
#     def list_qdrant_collections(self, user: Users = None):
#         try:
#             collections = self.qdrant.client.get_collections().collections
#             collection_names = [c.name for c in collections]
            
#             if user.is_admin:
#                 return collection_names
            
#             vectorstore_dal = VectorStoreDAL()
#             user_collections = vectorstore_dal.get_user_collections(user.id)
#             return user_collections

#             # return collection_names
            
#         except Exception as e:
#             self.logger.error(f"List qdrant collections failed. Detail error: {str(e)}")
#             raise Exception(f"List qdrant collections failed: {str(e)}")