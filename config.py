

from langchain_core.tools import tool
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key="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",
    temperature=0.6
)


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is 30°C and sunny."

@tool
def calculator(expression: str) -> str:
    """Evaluate a basic math expression, e.g. '2 + 2 * 3'."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

llm_with_tool = llm.bind_tools([get_weather , calculator])
