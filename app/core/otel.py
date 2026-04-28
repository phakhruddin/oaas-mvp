import os
from contextlib import contextmanager


class NoopSpan:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def set_attribute(self, key, value):
        return None

    def record_exception(self, exc):
        return None


class NoopTracer:
    def start_as_current_span(self, name: str):
        return NoopSpan()


_tracer = None


def setup_otel(service_name: str = "oaas-mvp"):
    """Configure OpenTelemetry tracing when enabled.

    If ENABLE_OTEL is not true, this returns a no-op tracer so local development
    keeps working without OpenTelemetry packages or a collector.
    """
    global _tracer

    if os.getenv("ENABLE_OTEL", "false").lower() != "true":
        _tracer = NoopTracer()
        return _tracer

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        print("[OTEL] OpenTelemetry packages missing. Falling back to no-op tracer.")
        _tracer = NoopTracer()
        return _tracer

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    _tracer = trace.get_tracer(service_name)
    return _tracer


def get_tracer():
    global _tracer

    if _tracer is None:
        _tracer = setup_otel()

    return _tracer


@contextmanager
def start_span(name: str, **attributes):
    tracer = get_tracer()

    with tracer.start_as_current_span(name) as span:
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(key, value)
        yield span
