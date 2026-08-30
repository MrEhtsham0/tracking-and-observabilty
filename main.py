# import time
# from fastapi import FastAPI
# from opentelemetry import trace
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import (
#     ConsoleSpanExporter,
#     SimpleSpanProcessor,
# )

# processor = SimpleSpanProcessor(
#     ConsoleSpanExporter()
# )
# from opentelemetry.sdk.resources import Resource

# resource = Resource.create({
#     "service.name": "fastapi-observability-demo",
# })

# provider = TracerProvider(resource=resource)
# provider.add_span_processor(processor)
# trace.set_tracer_provider(provider)

# tracer = trace.get_tracer(__name__)

# app = FastAPI()
# FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

# @app.get("/hello")
# def hello():
#     # Manual creation of a span
#     # with tracer.start_as_current_span("hello"):
#     return {"message": "hello"}

# @app.get("/users")
# def get_users():

#     with tracer.start_as_current_span("validate_user"):
#         time.sleep(0.01)  # 10ms

#     with tracer.start_as_current_span("database_query"):
#         time.sleep(0.05)  # 50ms

#     with tracer.start_as_current_span("external_api"):
#         time.sleep(0.9)  # 900ms — bottleneck

#     with tracer.start_as_current_span("prepare_response"):
#         time.sleep(0.01)  # 10ms

#     return {
#         "users": [
#             {"id": 1, "name": "Alice"},
#             {"id": 2, "name": "Bob"},
#         ]
#     }

import time

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# -------------------------
# Resource
# -------------------------

resource = Resource.create({
    "service.name": "fastapi-observability-demo",
})


# -------------------------
# Tracer Provider
# -------------------------

provider = TracerProvider(
    resource=resource
)


# -------------------------
# OTLP Exporter
# -------------------------

exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True,
)


# -------------------------
# Batch Processor
# -------------------------

processor = BatchSpanProcessor(
    exporter
)

provider.add_span_processor(processor)


# -------------------------
# Register provider
# -------------------------

trace.set_tracer_provider(provider)


# -------------------------
# Tracer
# -------------------------

tracer = trace.get_tracer(__name__)


# -------------------------
# FastAPI
# -------------------------

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)


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
