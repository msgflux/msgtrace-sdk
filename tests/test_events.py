"""
Tests for events module - span events and real-time streaming.
"""

import asyncio
import os

import pytest

from msgtrace.sdk import Spans
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


@pytest.fixture(autouse=True)
def enable_telemetry():
    """Enable telemetry for all tests."""
    os.environ["MSGTRACE_TELEMETRY_ENABLED"] = "true"
    os.environ["MSGTRACE_EXPORTER"] = "console"
    yield
    os.environ.pop("MSGTRACE_TELEMETRY_ENABLED", None)
    os.environ.pop("MSGTRACE_EXPORTER", None)


class TestEventType:
    """Test EventType constants."""

    def test_agent_events(self):
        """Test agent event type constants."""
        assert EventType.AGENT_START == "gen_ai.agent.start"
        assert EventType.AGENT_STEP == "gen_ai.agent.step"
        assert EventType.AGENT_COMPLETE == "gen_ai.agent.complete"
        assert EventType.AGENT_ERROR == "gen_ai.agent.error"

    def test_model_events(self):
        """Test model event type constants."""
        assert EventType.MODEL_REQUEST == "gen_ai.model.request"
        assert EventType.MODEL_RESPONSE == "gen_ai.model.response"
        assert EventType.MODEL_RESPONSE_CHUNK == "gen_ai.model.response.chunk"
        assert EventType.MODEL_REASONING == "gen_ai.model.reasoning"
        assert EventType.MODEL_REASONING_CHUNK == "gen_ai.model.reasoning.chunk"

    def test_tool_events(self):
        """Test tool event type constants."""
        assert EventType.TOOL_CALL == "gen_ai.tool.call"
        assert EventType.TOOL_RESULT == "gen_ai.tool.result"
        assert EventType.TOOL_ERROR == "gen_ai.tool.error"

    def test_flow_events(self):
        """Test flow event type constants."""
        assert EventType.FLOW_STEP == "gen_ai.flow.step"
        assert EventType.FLOW_REASONING == "gen_ai.flow.reasoning"
        assert EventType.FLOW_COMPLETE == "gen_ai.flow.complete"

    def test_module_events(self):
        """Test module event type constants."""
        assert EventType.MODULE_START == "gen_ai.module.start"
        assert EventType.MODULE_COMPLETE == "gen_ai.module.complete"
        assert EventType.MODULE_ERROR == "gen_ai.module.error"


class TestStreamEvent:
    """Test StreamEvent dataclass."""

    def test_stream_event_creation(self):
        """Test basic StreamEvent creation."""
        event = StreamEvent(
            name="test.event",
            attributes={"key": "value"},
        )
        assert event.name == "test.event"
        assert event.attributes == {"key": "value"}
        assert event.timestamp_ns > 0
        assert event.span_name == ""
        assert event.span_id == ""
        assert event.trace_id == ""

    def test_stream_event_with_span_info(self):
        """Test StreamEvent with span information."""
        event = StreamEvent(
            name="test.event",
            attributes={"key": "value"},
            span_name="my_span",
            span_id="abc123",
            trace_id="def456",
        )
        assert event.span_name == "my_span"
        assert event.span_id == "abc123"
        assert event.trace_id == "def456"

    def test_stream_event_is_frozen(self):
        """Test that StreamEvent is immutable."""
        event = StreamEvent(name="test.event")
        with pytest.raises(AttributeError):
            event.name = "modified"


class TestAddEvent:
    """Test add_event function."""

    def test_add_event_within_span(self):
        """Test add_event within a span context."""
        with Spans.span_context("test_span"):
            # Should not raise
            add_event("test.event", {"key": "value"})

    def test_add_event_outside_span(self):
        """Test add_event outside span context (should not raise)."""
        # Should not raise even without an active span
        add_event("test.event", {"key": "value"})

    def test_add_event_with_complex_attributes(self):
        """Test add_event with dict and list attributes (JSON serialized)."""
        with Spans.span_context("test_span"):
            add_event(
                "test.event",
                {
                    "string": "value",
                    "number": 42,
                    "dict": {"nested": "value"},
                    "list": [1, 2, 3],
                },
            )

    def test_add_event_with_none_attributes(self):
        """Test add_event with None attributes."""
        with Spans.span_context("test_span"):
            add_event("test.event", None)
            add_event("test.event")  # No attributes at all


class TestConvenienceEventFunctions:
    """Test convenience event functions."""

    def test_add_agent_start_event(self):
        """Test add_agent_start_event."""
        with Spans.span_context("test"):
            add_agent_start_event("my_agent")
            add_agent_start_event("my_agent", custom="attr")

    def test_add_agent_complete_event(self):
        """Test add_agent_complete_event."""
        with Spans.span_context("test"):
            add_agent_complete_event("my_agent")
            add_agent_complete_event("my_agent", response="result")
            add_agent_complete_event("my_agent", response={"key": "value"})

    def test_add_agent_step_event(self):
        """Test add_agent_step_event."""
        with Spans.span_context("test"):
            add_agent_step_event("my_agent", step_number=1)
            add_agent_step_event("my_agent", step_number=2, step_type="tool_call")

    def test_add_model_request_event(self):
        """Test add_model_request_event."""
        with Spans.span_context("test"):
            add_model_request_event()
            add_model_request_event(model="gpt-4")
            add_model_request_event(model="gpt-4", message_count=5)

    def test_add_model_response_event(self):
        """Test add_model_response_event."""
        with Spans.span_context("test"):
            add_model_response_event("text_generation")
            add_model_response_event("tool_call", has_reasoning=True)

    def test_add_model_response_chunk_event(self):
        """Test add_model_response_chunk_event."""
        with Spans.span_context("test"):
            add_model_response_chunk_event("Hello")
            add_model_response_chunk_event("World", index=1)

    def test_add_model_reasoning_event(self):
        """Test add_model_reasoning_event."""
        with Spans.span_context("test"):
            add_model_reasoning_event("I need to search...")
            add_model_reasoning_event("Let me think...", step=1)

    def test_add_tool_call_event(self):
        """Test add_tool_call_event."""
        with Spans.span_context("test"):
            add_tool_call_event("search", "call_123")
            add_tool_call_event("search", "call_123", arguments={"query": "weather"})
            add_tool_call_event("search", "call_123", step=1)

    def test_add_tool_result_event(self):
        """Test add_tool_result_event."""
        with Spans.span_context("test"):
            add_tool_result_event("search", "call_123")
            add_tool_result_event("search", "call_123", result="Sunny, 25°C")
            add_tool_result_event("search", "call_123", result={"temp": 25}, step=1)

    def test_add_tool_error_event(self):
        """Test add_tool_error_event."""
        with Spans.span_context("test"):
            add_tool_error_event("search", "call_123", "Connection timeout")
            add_tool_error_event("search", "call_123", "Not found", step=1)

    def test_add_flow_step_event(self):
        """Test add_flow_step_event."""
        with Spans.span_context("test"):
            add_flow_step_event(step_number=1)
            add_flow_step_event(step_number=2, iteration="reasoning")

    def test_add_flow_reasoning_event(self):
        """Test add_flow_reasoning_event."""
        with Spans.span_context("test"):
            add_flow_reasoning_event("Thinking about the problem...")
            add_flow_reasoning_event("Step 2 reasoning", step=2)

    def test_add_flow_complete_event(self):
        """Test add_flow_complete_event."""
        with Spans.span_context("test"):
            add_flow_complete_event()
            add_flow_complete_event(step=3)


class TestEventStream:
    """Test EventStream context manager."""

    def test_event_stream_sync_context(self):
        """Test EventStream as sync context manager."""
        with EventStream() as stream:
            assert stream is not None
            assert stream._queue is not None

    @pytest.mark.asyncio
    async def test_event_stream_async_context(self):
        """Test EventStream as async context manager."""
        async with EventStream() as stream:
            assert stream is not None
            assert stream._queue is not None

    @pytest.mark.asyncio
    async def test_event_stream_captures_events(self):
        """Test that EventStream captures events emitted within context."""
        collected_events = []

        async with EventStream() as stream:
            # Emit events in a separate task
            async def emit_events():
                with Spans.span_context("test_span"):
                    add_event("test.event.1", {"index": 1})
                    add_event("test.event.2", {"index": 2})
                stream.close()

            task = asyncio.create_task(emit_events())

            async for event in stream:
                collected_events.append(event)

            await task

        assert len(collected_events) == 2
        assert collected_events[0].name == "test.event.1"
        assert collected_events[0].attributes == {"index": 1}
        assert collected_events[1].name == "test.event.2"
        assert collected_events[1].attributes == {"index": 2}

    @pytest.mark.asyncio
    async def test_event_stream_with_span_info(self):
        """Test that EventStream events include span information.

        Note: Spans.span_context() uses start_span() which doesn't set
        the span as "current" in OTel context. So span_name/span_id/trace_id
        will be empty unless using start_as_current_span() or similar.
        This test verifies events are captured regardless.
        """
        collected_events = []

        async with EventStream() as stream:

            async def emit_events():
                with Spans.span_context("my_test_span"):
                    add_event("test.event", {"key": "value"})
                stream.close()

            task = asyncio.create_task(emit_events())

            async for event in stream:
                collected_events.append(event)

            await task

        assert len(collected_events) == 1
        event = collected_events[0]
        assert event.name == "test.event"
        assert event.attributes == {"key": "value"}
        # Note: span_name is empty because span_context uses start_span()
        # not start_as_current_span(). This is expected behavior.

    @pytest.mark.asyncio
    async def test_event_stream_callback(self):
        """Test EventStream with callback."""
        callback_events = []

        async with EventStream() as stream:
            stream.on_event(lambda e: callback_events.append(e))

            async def emit_events():
                with Spans.span_context("test"):
                    add_event("test.event", {"from": "callback_test"})
                stream.close()

            task = asyncio.create_task(emit_events())

            async for _ in stream:
                pass

            await task

        assert len(callback_events) == 1
        assert callback_events[0].name == "test.event"

    def test_event_stream_close(self):
        """Test EventStream close method."""
        with EventStream() as stream:
            stream.close()
            # Queue should have None sentinel
            assert stream._queue.get_nowait() is None

    @pytest.mark.asyncio
    async def test_event_stream_multiple_events_order(self):
        """Test that events maintain order in stream."""
        collected_events = []

        async with EventStream() as stream:

            async def emit_events():
                with Spans.span_context("test"):
                    for i in range(5):
                        add_event(f"event.{i}", {"index": i})
                stream.close()

            task = asyncio.create_task(emit_events())

            async for event in stream:
                collected_events.append(event)

            await task

        assert len(collected_events) == 5
        for i, event in enumerate(collected_events):
            assert event.name == f"event.{i}"
            assert event.attributes["index"] == i


class TestEventStreamIntegration:
    """Integration tests for event streaming with spans."""

    @pytest.mark.asyncio
    async def test_nested_spans_events(self):
        """Test event streaming with nested spans."""
        collected_events = []

        async with EventStream() as stream:

            async def emit_events():
                with Spans.init_flow("parent_flow"):
                    add_agent_start_event("my_agent")
                    with Spans.init_module("child_module"):
                        add_tool_call_event("search", "call_1")
                        add_tool_result_event("search", "call_1", result="found")
                    add_agent_complete_event("my_agent", response="done")
                stream.close()

            task = asyncio.create_task(emit_events())

            async for event in stream:
                collected_events.append(event)

            await task

        assert len(collected_events) == 4
        assert collected_events[0].name == EventType.AGENT_START
        assert collected_events[1].name == EventType.TOOL_CALL
        assert collected_events[2].name == EventType.TOOL_RESULT
        assert collected_events[3].name == EventType.AGENT_COMPLETE

    @pytest.mark.asyncio
    async def test_streaming_simulation(self):
        """Test simulated streaming response with chunk events."""
        collected_chunks = []

        async with EventStream() as stream:

            async def emit_chunks():
                with Spans.span_context("llm_response"):
                    chunks = ["The ", "weather ", "is ", "sunny ", "today."]
                    for i, chunk in enumerate(chunks):
                        add_model_response_chunk_event(chunk, index=i)
                        await asyncio.sleep(0.01)  # Simulate streaming delay
                stream.close()

            task = asyncio.create_task(emit_chunks())

            async for event in stream:
                if event.name == EventType.MODEL_RESPONSE_CHUNK:
                    collected_chunks.append(event.attributes["chunk"])

            await task

        assert collected_chunks == ["The ", "weather ", "is ", "sunny ", "today."]
        assert "".join(collected_chunks) == "The weather is sunny today."
