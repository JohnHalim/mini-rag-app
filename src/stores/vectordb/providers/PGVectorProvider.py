from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums, PgVectorDistanceMethodEnums, PgVectorIndexTypeEnums, PgVectorTableSchemeEnums
from models.db_schemes import RetrievedDocument
from typing import List
import logging
from sqlalchemy.sql import text as sql_text
import json

class PGVectorProvider(VectorDBInterface):
    def __init__(self, db_client, default_vector_size: int = 786,
                 distance_method: str = None):
        
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.distance_method = distance_method
        
        self.pgvector_table_prefix = PgVectorTableSchemeEnums._PREFIX.value
        
        self.logger = logging.getLogger("uvicorn")
        
    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                ))
            await session.commit()
            
    async def disconnect(self):
        pass
    
    async def is_collection_existed(self, collection_name: str) -> bool:
        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_stmt = sql_text('SELECT * FROM pg_tables WHERE tablename = :collection_name')
                results = await session.execute(list_stmt, {"collection_name" : collection_name})
                record = results.scalar_one_or_none()
                
            return record

