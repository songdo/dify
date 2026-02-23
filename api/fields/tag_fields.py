<<<<<<< HEAD
from flask_restx import Namespace, fields

dataset_tag_fields = {
    "id": fields.String,
    "name": fields.String,
    "type": fields.String,
    "binding_count": fields.String,
}


def build_dataset_tag_fields(api_or_ns: Namespace):
    return api_or_ns.model("DataSetTag", dataset_tag_fields)
=======
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ResponseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        populate_by_name=True,
        serialize_by_alias=True,
        protected_namespaces=(),
    )


class DataSetTag(ResponseModel):
    id: str
    name: str
    type: str
    binding_count: str | None = None
>>>>>>> upstream/main
