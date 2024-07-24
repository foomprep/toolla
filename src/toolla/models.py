default_tool_prompt = "You are a helpful assistant that tells the user which tools to use and which inputs to give to the tools.  The list of descriptions of available tools in JSON format is {tool_list}.  You will return a single tool to use and the inputs for that tool in the JSON format with keys tool and inputs, the user will use the current tool and then add the answer to the conversation.  You will select tools based on the current point on the conversation."

models = {
    "openai_models": ["gpt-4o"],
    "claude_models": ["claude-3-5-sonnet-20240620"],
}
