from typing import Annotated, Literal

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

import config
from .tools import search_knowledge_base, collection_var


class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    collection_name: str | None


class RagAgent:
    """多模态 RAG ReAct Agent，支持会话上下文。"""

    def __init__(
        self,
        model_name: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        self._model = ChatOpenAI(
            model=model_name or config.LLM_MODEL,
            base_url=base_url or config.LLM_BASE_URL,
            api_key=api_key or config.LLM_API_KEY,
        )
        self._system_prompt = (
            "你是一个乐于助人的助手。回答知识库问题前先调用 search_knowledge_base 检索相关内容。"
            "如果检索到图片，请仔细观察图片内容并结合文本信息作答。"
        )
        self._tools = [search_knowledge_base]
        self._graph = self._build_graph()

    # ------------------------------------------------------------------
    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("agent", self._call_model)
        builder.add_node("tools", self._execute_tools)
        builder.set_entry_point("agent")
        builder.add_conditional_edges(
            "agent", self._should_continue, {"tools": "tools", END: END}
        )
        builder.add_edge("tools", "agent")
        return builder.compile()

    # ------------------------------------------------------------------
    # nodes
    # ------------------------------------------------------------------

    def _call_model(self, state: AgentState) -> dict:
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=self._system_prompt), *messages]

        response = self._model.bind_tools(self._tools).invoke(messages)
        return {"messages": [response]}

    def _execute_tools(self, state: AgentState) -> dict:
        last_msg = state["messages"][-1]
        if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
            return {}

        tool_map = {"search_knowledge_base": search_knowledge_base}
        tool_messages: list[ToolMessage] = []

        # 注入 collection_name 到工具上下文，让 search_knowledge_base 能读取
        coll = state.get("collection_name")
        token = collection_var.set(coll)

        try:
            for tc in last_msg.tool_calls:
                fn = tool_map.get(tc["name"])
                if fn is None:
                    tool_messages.append(
                        ToolMessage(content=f"未知工具: {tc['name']}", tool_call_id=tc["id"])
                    )
                    continue
                try:
                    result = fn.invoke(tc["args"])
                except Exception as e:
                    tool_messages.append(
                        ToolMessage(content=f"工具执行出错: {e}", tool_call_id=tc["id"])
                    )
                    continue
                tool_messages.append(
                    ToolMessage(content=result, tool_call_id=tc["id"])
                )
        finally:
            collection_var.reset(token)

        return {"messages": tool_messages}

    @staticmethod
    def _should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        last_msg = state["messages"][-1]
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            return "tools"
        return END

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def chat(self, message: str, session_id: str = "default", collection_name: str | None = None) -> str:
        """发送消息并获取回复，session_id 相同则共享上下文。"""
        result = self._graph.invoke(
            {
                "messages": [HumanMessage(content=message)],
                "collection_name": collection_name,
            },
            config={"configurable": {"thread_id": session_id}},
        )
        return result["messages"][-1].content
