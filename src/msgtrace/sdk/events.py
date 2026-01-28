"""
Events - Span events and real-time streaming infrastructure.

Provides:
- Span event emission (via span.add_event())
- Real-time event streaming queue for astream() consumers
- Event type constants following OpenTelemetry GenAI conventions
"""

from __future__ import annotations

import asyncio
import contextvars
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from opentelemetry import trace

# =============================================================================
# Event Types (OpenTelemetry GenAI Semantic Conventions)
# =============================================================================


class EventType:
    """
    Constants for span event names following OpenTelemetry conventions.

    These are used with span.add_event() to create timestamped events
    within a span's lifetime.
    """

    # Agent lifecycle
    AGENT_START = "gen_ai.agent.start"
    AGENT_STEP = "gen_ai.agent.step"
    AGENT_COMPLETE = "gen_ai.agent.complete"
    AGENT_ERROR = "gen_ai.agent.error"

    # Model interactions
    MODEL_REQUEST = "gen_ai.model.request"
    MODEL_RESPONSE = "gen_ai.model.response"
    MODEL_RESPONSE_CHUNK = "gen_ai.model.response.chunk"
    MODEL_REASONING = "gen_ai.model.reasoning"
    MODEL_REASONING_CHUNK = "gen_ai.model.reasoning.chunk"

    # Tool operations
    TOOL_CALL = "gen_ai.tool.call"
    TOOL_RESULT = "gen_ai.tool.result"
    TOOL_ERROR = "gen_ai.tool.error"

    # Flow control (ReAct, CoT, etc.)
    FLOW_STEP = "gen_ai.flow.step"
    FLOW_REASONING = "gen_ai.flow.reasoning"
    FLOW_COMPLETE = "gen_ai.flow.complete"

    # Module lifecycle
    MODULE_START = "gen_ai.module.start"
    MODULE_COMPLETE = "gen_ai.module.complete"
    MODULE_ERROR = "gen_ai.module.error"


# =============================================================================
# Stream Event Data Structure
# =============================================================================


@dataclass(frozen=True)
class StreamEvent:
    """
    An event captured during span execution for real-time streaming.

    Attributes:
        name: Event name (an EventType constant).
        attributes: Event-specific data.
        timestamp_ns: Nanoseconds since epoch when event occurred.
        span_name: Name of the span that emitted this event.
        span_id: Hex string of the span ID.
        trace_id: Hex string of the trace ID.
    """

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    timestamp_ns: int = field(default_factory=time.time_ns)
    span_name: str = ""
    span_id: str = ""
    trace_id: str = ""


# =============================================================================
# Streaming Queue (Context Variable)
# =============================================================================

_event_queue: contextvars.ContextVar[asyncio.Queue | None] = contextvars.ContextVar(
    "_event_queue", default=None
)


# =============================================================================
# Event Emission Functions
# =============================================================================


def add_event(
    name: str,
    attributes: dict[str, Any] | None = None,
) -> None:
    """
    Add an event to the current span AND stream to consumers.

    This is the core function that provides dual emission:
    1. span.add_event() - for persistence/export to OTel backends
    2. queue.put_nowait() - for real-time streaming to astream() consumers

    Zero overhead when not streaming (queue contextvar is None).

    Args:
        name: Event name (use EventType constants).
        attributes: Event-specific data. Dicts/lists are JSON-serialized.

    Example:
        add_event(EventType.TOOL_CALL, {
            "tool_name": "search",
            "tool_id": "call_123",
            "arguments": {"query": "weather"},
        })
    """
    span = trace.get_current_span()
    attrs = attributes or {}

    # Serialize complex types for OTel compatibility
    serialized_attrs = {}
    for key, value in attrs.items():
        if isinstance(value, (dict, list)):
            serialized_attrs[key] = json.dumps(value)
        else:
            serialized_attrs[key] = value

    # 1. Always emit to OTel span (for persistence)
    if span.is_recording():
        span.add_event(name, serialized_attrs)

    # 2. Also emit to streaming queue (if active)
    queue = _event_queue.get()
    if queue is not None:
        span_context = span.get_span_context() if span.is_recording() else None
        event = StreamEvent(
            name=name,
            attributes=attrs,  # Keep original (non-serialized) for streaming
            timestamp_ns=time.time_ns(),
            span_name=span.name if span.is_recording() else "",
            span_id=(format(span_context.span_id, "016x") if span_context else ""),
            trace_id=(format(span_context.trace_id, "032x") if span_context else ""),
        )
        queue.put_nowait(event)


# =============================================================================
# Convenience Event Functions
# =============================================================================


def add_agent_start_event(agent_name: str, **extra: Any) -> None:
    """Emit agent start event."""
    add_event(EventType.AGENT_START, {"agent_name": agent_name, **extra})


def add_agent_complete_event(agent_name: str, response: Any = None, **extra: Any) -> None:
    """Emit agent completion event."""
    attrs = {"agent_name": agent_name, **extra}
    if response is not None:
        attrs["response"] = response
    add_event(EventType.AGENT_COMPLETE, attrs)


def add_agent_step_event(
    agent_name: str, step_number: int, step_type: str = "", **extra: Any
) -> None:
    """Emit agent step event (iteration in agent loop)."""
    add_event(
        EventType.AGENT_STEP,
        {"agent_name": agent_name, "step_number": step_number, "step_type": step_type, **extra},
    )


def add_model_request_event(
    model: str | None = None, message_count: int | None = None, **extra: Any
) -> None:
    """Emit model request event."""
    attrs = {**extra}
    if model:
        attrs["model"] = model
    if message_count is not None:
        attrs["message_count"] = message_count
    add_event(EventType.MODEL_REQUEST, attrs)


def add_model_response_event(response_type: str, **extra: Any) -> None:
    """Emit model response event."""
    add_event(EventType.MODEL_RESPONSE, {"response_type": response_type, **extra})


def add_model_response_chunk_event(chunk: str, index: int = 0, **extra: Any) -> None:
    """Emit model response chunk event (for streaming)."""
    add_event(EventType.MODEL_RESPONSE_CHUNK, {"chunk": chunk, "index": index, **extra})


def add_model_reasoning_event(reasoning: str, step: int | None = None, **extra: Any) -> None:
    """Emit model reasoning event."""
    attrs = {"reasoning": reasoning, **extra}
    if step is not None:
        attrs["step"] = step
    add_event(EventType.MODEL_REASONING, attrs)


def add_tool_call_event(
    tool_name: str,
    tool_id: str,
    arguments: dict[str, Any] | None = None,
    step: int | None = None,
    **extra: Any,
) -> None:
    """Emit tool call event."""
    attrs = {"tool_name": tool_name, "tool_id": tool_id, **extra}
    if arguments:
        attrs["arguments"] = arguments
    if step is not None:
        attrs["step"] = step
    add_event(EventType.TOOL_CALL, attrs)


def add_tool_result_event(
    tool_name: str,
    tool_id: str,
    result: Any = None,
    step: int | None = None,
    **extra: Any,
) -> None:
    """Emit tool result event."""
    attrs = {"tool_name": tool_name, "tool_id": tool_id, **extra}
    if result is not None:
        attrs["result"] = result
    if step is not None:
        attrs["step"] = step
    add_event(EventType.TOOL_RESULT, attrs)


def add_tool_error_event(
    tool_name: str,
    tool_id: str,
    error: str,
    step: int | None = None,
    **extra: Any,
) -> None:
    """Emit tool error event."""
    attrs = {"tool_name": tool_name, "tool_id": tool_id, "error": error, **extra}
    if step is not None:
        attrs["step"] = step
    add_event(EventType.TOOL_ERROR, attrs)


def add_flow_step_event(step_number: int, **extra: Any) -> None:
    """Emit flow control step event."""
    add_event(EventType.FLOW_STEP, {"step_number": step_number, **extra})


def add_flow_reasoning_event(reasoning: str, step: int | None = None, **extra: Any) -> None:
    """Emit flow control reasoning event."""
    attrs = {"reasoning": reasoning, **extra}
    if step is not None:
        attrs["step"] = step
    add_event(EventType.FLOW_REASONING, attrs)


def add_flow_complete_event(step: int | None = None, **extra: Any) -> None:
    """Emit flow control completion event."""
    attrs = {**extra}
    if step is not None:
        attrs["step"] = step
    add_event(EventType.FLOW_COMPLETE, attrs)


# =============================================================================
# Streaming Context Manager
# =============================================================================


class EventStream:
    """
    Context manager for capturing span events as a stream.

    Used by Module.astream() to yield events in real-time.

    Example:
        async with EventStream() as stream:
            task = asyncio.create_task(agent.acall("Hello"))
            async for event in stream:
                print(event.name, event.attributes)
            await task
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue = asyncio.Queue()
        self._token: contextvars.Token | None = None
        self._callbacks: list[Callable[[StreamEvent], None]] = []

    def on_event(self, callback: Callable[[StreamEvent], None]) -> None:
        """Register a callback for each event."""
        self._callbacks.append(callback)

    async def __aenter__(self) -> EventStream:
        self._token = _event_queue.set(self._queue)
        return self

    async def __aexit__(self, *exc) -> None:
        if self._token is not None:
            _event_queue.reset(self._token)
        # Signal end of stream
        self._queue.put_nowait(None)

    def __enter__(self) -> EventStream:
        self._token = _event_queue.set(self._queue)
        return self

    def __exit__(self, *exc) -> None:
        if self._token is not None:
            _event_queue.reset(self._token)

    def close(self) -> None:
        """Signal end of event stream."""
        self._queue.put_nowait(None)

    async def __aiter__(self):
        """Async iteration over events."""
        while True:
            event = await self._queue.get()
            if event is None:
                break
            for callback in self._callbacks:
                callback(event)
            yield event

    @property
    def events(self) -> list[StreamEvent]:
        """
        Collect all events synchronously (drains queue).

        Use only after stream is closed.
        """
        collected = []
        while not self._queue.empty():
            event = self._queue.get_nowait()
            if event is not None:
                collected.append(event)
        return collected
