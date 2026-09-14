import time

from fastapi import FastAPI, HTTPException, status

from app.exceptions.exceptions import AppException, setup_exception_handlers
from app.exceptions.traceability import setup_opentelemetry

app = FastAPI()

# Register OpenTelemetry tracing
tracer = setup_opentelemetry(app)

# Register global exception handlers
setup_exception_handlers(app)


@app.get("/trace")
def trace_demo():
    with tracer.start_as_current_span("trace_demo"):
        time.sleep(0.02)

    return {
        "message": "trace captured",
        "service": "fastapi-observability-demo",
    }


@app.get("/users")
def get_users():

    with tracer.start_as_current_span("validate_user"):
        time.sleep(0.01)

    with tracer.start_as_current_span("database_query"):
        time.sleep(0.05)

    with tracer.start_as_current_span("external_api"):
        time.sleep(0.9)

    with tracer.start_as_current_span("prepare_response"):
        time.sleep(0.01)

    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }


@app.get("/error/http")
def trigger_http_error():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found in the system",
    )


@app.get("/error/custom")
def trigger_custom_error():
    raise AppException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Custom business logic exception occurred",
    )


@app.get("/error/unhandled")
def trigger_unhandled_error():
    # Will trigger 500 error handler
    return 1 / 0