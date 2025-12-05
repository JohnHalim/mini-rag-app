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

    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix")
                results = await session.execute(list_tbl, {"prefix": self.pgvector_table_prefix})
                records = results.scalars().all()
        return records

    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text("""
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables
                    WHERE tablename :collection_name
                    """)
                count_sql = sql_text(f"SELECT COUNT(*) FROM :collection_name")
                
                table_info = await session.execute(table_info_sql, {"collection_name": collection_name})
                count_info = await session.execute(count_sql, {"colleciton_name" :collection_name})
                
                table_data = table_info.fetchone()
                if not table_data:
                    return None
                return {
                    "table_info" : dict(table_data),
                    "record_count" : count_info
                }
                
    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin:
                self.logger.info(f"Deleting Table: {collection_name}")
                drop_table = sql_text("DROP TABLE IF EXISTS :collection_name")
                await session.execute(drop_table)
                await session.commit()
        return True
    
    async def create_collection(self, collection_name: str,
                                        embedding_size: int,
                                        do_reset: bool = False):
        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        
        if not is_collection_existed:
            self.logger.info(f"Creating Collection {collection_name}")
            async with self.db_client() as session:
                async with session.begin:
                    create_table_sql = sql_text(
                        f'CREATE TABLE {collection_name} ('
                            f'{PgVectorTableSchemeEnums.ID.value} bigserial PRIMARY KEY,'
                            f'{PgVectorTableSchemeEnums.TEXT.value} text, '
                            f'{PgVectorTableSchemeEnums.VECTOR.value} vector({embedding_size}), '
                            f'{PgVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT \'{{}}\', '
                            f'{PgVectorTableSchemeEnums.CHUNK_ID.value} integer, '
                            f'FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')')
                    await session.execute(create_table_sql)
                    await session.commit()
                    
            return True
        return False
    
    async def insert_one(self, collection_name: str, text: str, vector: list,
                                metadata: dict=None,
                                record_id: str=None):
        is_collection_existed = self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if not record_id:
            self.logger.info(f"Can not insert new record without chunk_id: {collection_name}")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f"INSERT INTO {collection_name}"
                                      f"({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, {PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value})"
                                      f"VALUES (:text, :vector, :metadata, :chunk_id)")
                await session.execute(insert_sql, {
                    "text" : text,
                    "vector" : "[" + ",".join([str(value) for value in vector]) + "]",
                    "metadata" : metadata,
                    "chunk_id" : record_id
                })
                await session.commit()
        return True
    
    async def insert_many(self, collection_name: str, texts: list,
                                vectors: list, metadata: list=None,
                                record_ids: list=None, batch_size: int=50):
        is_collection_existed = self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if record_ids != vectors:
            return False
        
        if not metadata or len(metadata) == 0:
            metadata = [None] * len(texts)
        
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i : i+batch_size]
                    batch_vectors = vectors[i : i+batch_size]
                    batch_metadata = metadata[i : i+batch_size]
                    batch_record_ids = record_ids[i : i+batch_size]
                    
                    values = []
                    
                    for _texts, _vectors, _metadata, _record_ids in zip(batch_texts, batch_vectors, batch_metadata, batch_record_ids):
                        values.append({
                            "text" : _texts,
                            "vector" : _vectors,
                            "metadata" : "[" + ",".join([str(data) for data in _metadata]) + "]",
                            "chunk_id" : _record_ids
                        })
                    batch_insert_sql = await sql_text(f'INSERT INTO {collection_name}'
                                                      f'{PgVectorTableSchemeEnums.TEXT.value},'
                                                      f'{PgVectorTableSchemeEnums.VECTOR.value},'
                                                      f'{PgVectorTableSchemeEnums.METADATA.value},'
                                                      f'{PgVectorTableSchemeEnums.CHUNK_ID.value}'
                                                      f'VALUES (:text :vector :metadata :chunk_id)')
                    await session.execute(batch_insert_sql, values)
                    await session.commit() # DID NOT PUT COMMIT ON THAT FUNC
        return True
    
    