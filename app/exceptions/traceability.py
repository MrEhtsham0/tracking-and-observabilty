from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_opentelemetry(
    app: FastAPI,
    service_name: str = "fastapi-observability-demo",
    endpoint: str = "http://localhost:4317",
    insecure: bool = True,
) -> trace.Tracer:
    """
    Configures OpenTelemetry tracing with OTLP gRPC exporter and instruments FastAPI.

    Args:
        app: The FastAPI application instance.
        service_name: Name of the service for OpenTelemetry resource attributes.
        endpoint: OTLP gRPC collector endpoint (default: http://localhost:4317).
        insecure: Whether to disable transport security for local development.

    Returns:
        trace.Tracer: Tracer instance for creating custom spans.
    """
    # -------------------------
    # Resource
    # -------------------------
    resource = Resource.create({
        "service.name": service_name,
    })

    # -------------------------
    # Tracer Provider
    # -------------------------
    provider = TracerProvider(resource=resource)

    # -------------------------
    # OTLP Exporter
    # -------------------------
    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=insecure,
    )

    # -------------------------
    # Batch Processor
    # -------------------------
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # -------------------------
    # Register Provider
    # -------------------------
    trace.set_tracer_provider(provider)

    # -------------------------
    # Instrument FastAPI App
    # -------------------------
    FastAPIInstrumentor.instrument_app(app)

    return trace.get_tracer(service_name)
