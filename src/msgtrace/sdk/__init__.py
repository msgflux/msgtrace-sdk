"""
msgtrace SDK public API.

This module exports the main components for tracing AI applications.
"""

from msgtrace.sdk.attributes import MsgTraceAttributes
from msgtrace.sdk.events import (
    EventStream,
    EventType,
    StreamEvent,
    add_agent_complete_event,
    add_agent_start_event,
    add_agent_step_event,
    add_event,
    add_flow_complete_event,
    add_flow_reasoning_event,
    add_flow_step_event,
    add_model_reasoning_event,
    add_model_request_event,
    add_model_response_chunk_event,
    add_model_response_event,
    add_tool_call_event,
    add_tool_error_event,
    add_tool_result_event,
)
from msgtrace.sdk.spans import Spans
from msgtrace.sdk.tracer import tracer

__all__ = [
    # Core
    "tracer",
    "Spans",
    "MsgTraceAttributes",
    # Events
    "EventType",
    "StreamEvent",
    "EventStream",
    "add_event",
    # Convenience event functions
    "add_agent_start_event",
    "add_agent_complete_event",
    "add_agent_step_event",
    "add_model_request_event",
    "add_model_response_event",
    "add_model_response_chunk_event",
    "add_model_reasoning_event",
    "add_tool_call_event",
    "add_tool_result_event",
    "add_tool_error_event",
    "add_flow_step_event",
    "add_flow_reasoning_event",
    "add_flow_complete_event",
]
