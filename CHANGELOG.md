# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-01-28

### Added

#### Span Events Infrastructure (`msgtrace.sdk.events`)

New module for emitting span events and real-time streaming, following OpenTelemetry GenAI semantic conventions.

##### Event Types (`EventType`)
Constants for span event names:
- **Agent lifecycle**: `AGENT_START`, `AGENT_STEP`, `AGENT_COMPLETE`, `AGENT_ERROR`
- **Model interactions**: `MODEL_REQUEST`, `MODEL_RESPONSE`, `MODEL_RESPONSE_CHUNK`, `MODEL_REASONING`, `MODEL_REASONING_CHUNK`
- **Tool operations**: `TOOL_CALL`, `TOOL_RESULT`, `TOOL_ERROR`
- **Flow control**: `FLOW_STEP`, `FLOW_REASONING`, `FLOW_COMPLETE` (for ReAct, CoT, etc.)
- **Module lifecycle**: `MODULE_START`, `MODULE_COMPLETE`, `MODULE_ERROR`

##### Core Function: `add_event(name, attributes)`
Dual emission to both OTel span and streaming queue:
```python
from msgtrace.sdk.events import add_event, EventType

add_event(EventType.TOOL_CALL, {
    "tool_name": "search",
    "tool_id": "call_123",
    "arguments": {"query": "weather"},
})
```

##### Convenience Functions
- `add_agent_start_event(agent_name, **extra)`
- `add_agent_complete_event(agent_name, response=None, **extra)`
- `add_agent_step_event(agent_name, step_number, step_type="", **extra)`
- `add_model_request_event(model=None, message_count=None, **extra)`
- `add_model_response_event(response_type, **extra)`
- `add_model_response_chunk_event(chunk, index=0, **extra)`
- `add_model_reasoning_event(reasoning, step=None, **extra)`
- `add_tool_call_event(tool_name, tool_id, arguments=None, step=None, **extra)`
- `add_tool_result_event(tool_name, tool_id, result=None, step=None, **extra)`
- `add_tool_error_event(tool_name, tool_id, error, step=None, **extra)`
- `add_flow_step_event(step_number, **extra)`
- `add_flow_reasoning_event(reasoning, step=None, **extra)`
- `add_flow_complete_event(step=None, **extra)`

##### Real-Time Streaming (`EventStream`)
Context manager for capturing span events as an async stream:
```python
from msgtrace.sdk.events import EventStream

async with EventStream() as stream:
    task = asyncio.create_task(agent.acall("Hello"))
    async for event in stream:
        print(event.name, event.attributes)
    await task
```

##### Stream Event Data Structure (`StreamEvent`)
Frozen dataclass with:
- `name`: Event name (EventType constant)
- `attributes`: Event-specific data
- `timestamp_ns`: Nanoseconds since epoch
- `span_name`, `span_id`, `trace_id`: Span context

### Benefits
- Zero overhead when not streaming (context variable is None)
- Automatic JSON serialization for complex types (dicts, lists)
- Full compatibility with OpenTelemetry span events
- Thread-safe through context variables
- Enables real-time UI updates and streaming responses

## [1.1.0] - 2025-12-04

### Added

#### Module Attributes
- `MsgTraceAttributes.set_module_name(name)` - Set module name for better organization (e.g., 'vector_search', 'intent_classifier')
- `MsgTraceAttributes.set_module_type(module_type)` - Set module type for specialized visualizations in msgtrace frontend
  - Supported types: 'Agent', 'Tool', 'LLM', 'Transcriber', 'Retriever', 'Embedder', 'Custom'
  - Enables automatic grouping and type-specific analytics

#### Extended Tool Attributes
- `MsgTraceAttributes.set_tool_execution_type(execution_type)` - Track how tools are executed
  - Values: 'local' (in-process), 'remote' (external service)
  - Useful for performance analysis and debugging
- `MsgTraceAttributes.set_tool_protocol(protocol)` - Track communication protocol used
  - Values: 'mcp' (Model Context Protocol), 'a2a' (Agent-to-Agent), 'http', 'grpc', etc.
  - Enables protocol-specific debugging and monitoring

#### Extended Agent Attributes
- `MsgTraceAttributes.set_agent_response(response)` - Capture agent response content
  - Accepts string or dict (automatically JSON-serialized)
  - Useful for debugging agent behavior and outputs
  - Can be used alongside existing `set_agent_name`, `set_agent_id`, `set_agent_type`

### Benefits
- Better categorization of AI operations by module type
- Enhanced tool execution tracking with protocol and execution type metadata
- Improved agent debugging with response content capture
- Enables specialized visualizations in msgtrace frontend
- Full compatibility with OpenTelemetry GenAI semantic conventions

### Migration Notes
All new attributes follow the same patterns as existing methods:
- Thread-safe through OpenTelemetry's span API
- Only record when span is recording (zero overhead when disabled)
- Automatic JSON serialization for complex types
- Consistent naming with GenAI semantic conventions

## [1.0.0] - 2025-11-26

## [0.1.0] - TBD

### Added
- Initial release
- OpenTelemetry-based tracing for AI applications
- Support for Gen AI semantic conventions
- Automatic token counting and cost calculation
- Tool call tracking and execution monitoring
- Comprehensive test suite
- Full CI/CD automation
- Automated release workflow
- Security validation for releases

[Unreleased]: https://github.com/msgflux/msgtrace-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/msgflux/msgtrace-sdk/releases/tag/v0.1.0
