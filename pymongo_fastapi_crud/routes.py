from fastapi import FastAPI, APIRouter, Body, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
import pymongo

from pymongo_fastapi_crud.models import UnlabeledJob, ProbabilityUpdate, LabelledJob
from client import database, close_connection

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


router = APIRouter()
app = FastAPI()


class Request:
    def __init__(self, database):
        self.app = type('obj', (object,), {'database': database})


requests = Request(database)


class MongoAPI:
    @router.get(
        "/unlabelled_get",
        response_description="Get all unlabelled data",
        response_model=List[UnlabeledJob],
        status_code=status.HTTP_200_OK
    )
    def get_unlabelled_data():
        unlabelled_data = list(requests.app.database["unlabelled"].find())
        return unlabelled_data

    @router.post(
        "/update_prob",
        response_description="Update probabilities for all entries",
        status_code=status.HTTP_200_OK
    )
    def update_probabilities(
        updates: List[ProbabilityUpdate] = Body(...)
    ):
        database = requests.app.database["unlabelled"]

        # Prepare the bulk update operations
        bulk_operations = []
        for update in updates:
            bulk_operations.append(
                pymongo.UpdateOne(
                    {"job_id": update['job_id']},
                    {
                        "$set": {"probability": update['probability']}
                    },
                    upsert=True
                )
            )

        result = database.bulk_write(bulk_operations)

        return {
            "message": "Probabilities updated successfully",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_count": result.upserted_count
        }

    @router.get(
        "/labelled_get",
        response_description="Get all labelled data",
        response_model=List[LabelledJob],
        status_code=status.HTTP_200_OK
    )
    def get_labelled_data():
        labelled_data = list(requests.app.database["labelled"].find())
        return labelled_data

    @app.on_event("startup")
    def startup_db_client():
        app.database = database

    @app.on_event("shutdown")
    def shutdown_db_client(self):
        close_connection()

    app.include_router(router)
