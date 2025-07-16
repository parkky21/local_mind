import re
import json

def sse_headers():
    return {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

def parse_tool_call_from_content(content):
    match = re.search(r"<tool_call>(.*?)</tool_call>", content, re.DOTALL)
    if not match:
        raise ValueError("No <tool_call> block found in message content")
    return json.loads(match.group(1).strip())
