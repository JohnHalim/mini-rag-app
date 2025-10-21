from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from models.enums.ResponseEnums import ResponseSignal

import logging

logger = logging.getLogger("uvicorn.error")


nlp_router = APIRouter(
    prefix="/api/v1/nlp", 
    tags=["api_v1", "nlp"]
    )


@nlp_router.post(path="/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value},
        )

    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        vectordb_client=request.app.vectordb_client,
    )
    
    has_records = True
    page_no = 1
    inserted_items_count=0
    idx=0
    
    while has_records:
        
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)
        if len(page_chunks):
            page_no += 1
            
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        

        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunks_ids
        )
        
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal" : ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                }
            )
        
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "signal" : ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count" : inserted_items_count
        }
    )
    
@nlp_router.get(path="/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    nlp_controller = NLPController(generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client,
                                   vectordb_client=request.app.vectordb_client)
    
    collection_info = nlp_controller.get_vector_db_collection_info(project=project)
    
    # collection_info_dict = {
    #     "name": collection_info.name,
    #     "vectors_count": collection_info.vectors_count,
    #     "points_count": collection_info.points_count,
    #     "segments_count": collection_info.segments_count,
    #     "status": str(collection_info.status),
    #     "config": {
    #         "params": collection_info.config.params.dict(),
    #         "vectors": {
    #             "size": collection_info.config.vectors.size,
    #             "distance": str(collection_info.config.vectors.distance)
    #         }
    #     }
    # }    
    
    return JSONResponse(
        content={
            "signal" : ResponseSignal.VECTORDB_collection_RETRIEVED.value,
            "collection_info" : collection_info
        }
    )

@nlp_router.post(path="/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    nlp_controller = NLPController(generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client,
                                   vectordb_client=request.app.vectordb_client)
    
    search_result = nlp_controller.search_vectordb_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit
        )
    
    if not search_result:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal" : ResponseSignal.VECTORDB_SEARCH_ERROR.value
            }
        )
    
    return JSONResponse(
        content={
            "signal" : ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "search_result" : search_result
        }
    )
    
