from __future__ import annotations

from typing import Any, cast

from langgraph.graph import END, START, StateGraph

from app.application.pipeline.nodes import PipelineNodes
from app.application.pipeline.state import PipelineState


class SummarizationPipeline:
    """Compiles and runs the LangGraph pipeline."""

    def __init__(self, nodes: PipelineNodes) -> None:
        graph = StateGraph(PipelineState)
        graph.add_node("transcribe", nodes.transcribe)
        graph.add_node("summarize", nodes.summarize)
        graph.add_node("prepare_reference_clip", nodes.prepare_reference_clip)
        graph.add_node("synthesize", nodes.synthesize)

        graph.add_edge(START, "transcribe")
        graph.add_edge("transcribe", "summarize")
        graph.add_edge("summarize", "prepare_reference_clip")
        graph.add_edge("prepare_reference_clip", "synthesize")
        graph.add_edge("synthesize", END)

        self._compiled = graph.compile()

    def run(self, state: PipelineState) -> PipelineState:
        payload: Any = state
        result: Any = self._compiled.invoke(payload)
        return cast(PipelineState, result)
