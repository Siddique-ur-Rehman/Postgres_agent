
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage


@wrap_tool_call
def sql_safety_middleware(request, handler):
    # Apply these checks only to SQL execution calls.
    if request.tool_call["name"] != "execute_sql":
        return handler(request)

    query = request.tool_call["args"].get("query", "")
    cleaned_query = query.strip()

    # Allow only SELECT statements in this first version.
    if not cleaned_query.lower().startswith("select "):
        return ToolMessage(
            content="Blocked: Only SELECT queries are allowed.",
            tool_call_id=request.tool_call["id"],
        )

    # Reject multiple SQL statements.
    if ";" in cleaned_query.rstrip(";"):
        return ToolMessage(
            content="Blocked: Multiple SQL statements are not allowed.",
            tool_call_id=request.tool_call["id"],
        )

    # Continue to the tool only if validation passes.
    return handler(request)
