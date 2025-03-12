from src.utils.logger.custom_logging import LoggerMixin
from src.helpers.qdrant_connection import QdrantConnection
from src.schemas.response import BasicResponse
# from src.database.data_layer_access.file_dal import FileManagementDAL
from src.database.models.schemas import Users
from src.database.data_layer_access.vectorstore_dal import VectorStoreDAL

class VectorStoreQdrant(LoggerMixin):
    def __init__(self) -> None:
        super().__init__()
        self.qdrant = QdrantConnection()

    def create_qdrant_collection(self, collection_name: str, user: Users):
        resp = BasicResponse(status="Success",
                             message="create qdrant collection success.",
                             data=collection_name)
        try:
            if not self.qdrant.client.collection_exists(collection_name=collection_name):
                is_created = self.qdrant._create_collection(collection_name)
                VectorStoreDAL().create_vector_store_collection(user.id, collection_name)
                if is_created:
                    resp.message = f"create qdrant collection '{collection_name}' success."
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
            vectorstore_dal = VectorStoreDAL()
            if vectorstore_dal.collection_own_by_user(user.id, collection_name):
                if self.qdrant.client.collection_exists(collection_name=collection_name):
                    
                    self.qdrant._delete_collection(collection_name)
                    # FileManagementDAL().delete_record_by_collection(collection_name=collection_name)
                    # minio_storage.delete_folder_collection(collection_name=collection_name)
                    vectorstore_dal.delete_vector_store_collection(user.id, collection_name)
                    return BasicResponse(status="Success",
                                        message=f"Delete qdrant collection '{collection_name}' success.",
                                        data=collection_name)
                return BasicResponse(status="Failed",
                                        message=f"Collection {collection_name} is not exist.",
                                        data=None)
            
            return BasicResponse(status="Failed",
                                        message=f"User is not own {collection_name} collection",
                                        data=None)

        except Exception as e:
            self.logger.error(f"Delete qdrant collection '{collection_name}'failed. Detail error: {str(e)}")
            return BasicResponse(status="Failed",
                                 message=f"Delete qdrant collection '{collection_name}'failed. Detail error: {str(e)}",
                                 data=None)
    
    def list_qdrant_collections(self, user: Users = None):
        try:
            collections = self.qdrant.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if user.is_admin:
                return collection_names
            
            vectorstore_dal = VectorStoreDAL()
            user_collections = vectorstore_dal.get_user_collections(user.id)
            return user_collections

            # return collection_names
            
        except Exception as e:
            self.logger.error(f"List qdrant collections failed. Detail error: {str(e)}")
            raise Exception(f"List qdrant collections failed: {str(e)}")