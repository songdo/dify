<<<<<<< HEAD
from flask_restx import Namespace, fields

from libs.helper import TimestampField

annotation_fields = {
    "id": fields.String,
    "question": fields.String,
    "answer": fields.Raw(attribute="content"),
    "hit_count": fields.Integer,
    "created_at": TimestampField,
    # 'account': fields.Nested(simple_account_fields, allow_null=True)
}


def build_annotation_model(api_or_ns: Namespace):
    """Build the annotation model for the API or Namespace."""
    return api_or_ns.model("Annotation", annotation_fields)


annotation_list_fields = {
    "data": fields.List(fields.Nested(annotation_fields)),
}

annotation_hit_history_fields = {
    "id": fields.String,
    "source": fields.String,
    "score": fields.Float,
    "question": fields.String,
    "created_at": TimestampField,
    "match": fields.String(attribute="annotation_question"),
    "response": fields.String(attribute="annotation_content"),
}

annotation_hit_history_list_fields = {
    "data": fields.List(fields.Nested(annotation_hit_history_fields)),
}
=======
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _to_timestamp(value: datetime | int | None) -> int | None:
    if isinstance(value, datetime):
        return int(value.timestamp())
    return value


class ResponseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        populate_by_name=True,
        serialize_by_alias=True,
        protected_namespaces=(),
    )


class Annotation(ResponseModel):
    id: str
    question: str | None = None
    answer: str | None = Field(default=None, validation_alias="content")
    hit_count: int | None = None
    created_at: int | None = None

    @field_validator("created_at", mode="before")
    @classmethod
    def _normalize_created_at(cls, value: datetime | int | None) -> int | None:
        return _to_timestamp(value)


class AnnotationList(ResponseModel):
    data: list[Annotation]
    has_more: bool
    limit: int
    total: int
    page: int


class AnnotationExportList(ResponseModel):
    data: list[Annotation]


class AnnotationHitHistory(ResponseModel):
    id: str
    source: str | None = None
    score: float | None = None
    question: str | None = None
    created_at: int | None = None
    match: str | None = Field(default=None, validation_alias="annotation_question")
    response: str | None = Field(default=None, validation_alias="annotation_content")

    @field_validator("created_at", mode="before")
    @classmethod
    def _normalize_created_at(cls, value: datetime | int | None) -> int | None:
        return _to_timestamp(value)


class AnnotationHitHistoryList(ResponseModel):
    data: list[AnnotationHitHistory]
    has_more: bool
    limit: int
    total: int
    page: int
>>>>>>> upstream/main
