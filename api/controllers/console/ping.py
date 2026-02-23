<<<<<<< HEAD
from flask_restx import Resource, fields

from . import console_ns


@console_ns.route("/ping")
class PingApi(Resource):
    @console_ns.doc("health_check")
    @console_ns.doc(description="Health check endpoint for connection testing")
    @console_ns.response(
        200,
        "Success",
        console_ns.model("PingResponse", {"result": fields.String(description="Health check result", example="pong")}),
    )
    def get(self):
        """Health check endpoint for connection testing"""
        return {"result": "pong"}
=======
from pydantic import BaseModel, Field

from controllers.fastopenapi import console_router


class PingResponse(BaseModel):
    result: str = Field(description="Health check result", examples=["pong"])


@console_router.get(
    "/ping",
    response_model=PingResponse,
    tags=["console"],
)
def ping() -> PingResponse:
    """Health check endpoint for connection testing."""
    return PingResponse(result="pong")
>>>>>>> upstream/main
