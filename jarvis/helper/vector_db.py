from pymilvus import connections, Collection, CollectionSchema, DataType, FieldSchema, utility
from typing import List, Dict, Any, Tuple

class MilvusClient:
    def __init__(self, collection_name: str = "project_files", host: str = "localhost", port: str = "19530", dim: int = 1536):
        self.host = host
        self.port = port
        self.dim = dim
        self.collection_name = collection_name
        self._connect()
        
        # Check and create collection if doesn't exist
        if not utility.has_collection(self.collection_name):
            self._create_collection()

    def _connect(self):
        connections.connect(
            alias="default",
            host=self.host,
            port=self.port
        )

    def _create_collection(self):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
        ]
        schema = CollectionSchema(fields)
        collection = Collection(self.collection_name, schema)
        
        # Create index for vector field
        collection.create_index(
            field_name="embeddings",
            index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 1024}}
        )
        return collection

    def insert(self, texts: List[str], file_paths: List[str], vectors: List[List[float]]) -> List[int]:
        collection = Collection(self.collection_name)
        data = [
            [],  # for ids (auto-generated)
            texts,  # for text field
            file_paths,  # for file_path field
            vectors  # for embeddings field
        ]
        mr = collection.insert(data)
        return mr.primary_keys

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        collection = Collection(self.collection_name)
        collection.load()
        
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        
        results = collection.search(
            data=[query_vector],
            anns_field="embeddings",
            param=search_params,
            limit=top_k,
            output_fields=["text", "file_path"]
        )
        
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "text": hit.entity.get('text'),
                    "file_path": hit.entity.get('file_path')
                })
                
        collection.release()
        return search_results

    def drop_collection(self):
        """Drop the collection if it exists"""
        if utility.has_collection(self.collection_name):
            Collection(self.collection_name).drop()
            return True
        return False