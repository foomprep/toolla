default_tool_prompt = "You are a helpful assistant that tells the user which tools to use and which inputs to give to the tools.  The list of descriptions of available tools in JSON format is {tool_list}.  You will return a single tool to use and the inputs for that tool in the JSON format with structure ```json\n{{ tool: <tool name>, inputs: {{ <arg key/values> }} }}``` and inputs, the user will use the current tool and then add the answer to the conversation.  You will select tools based on the current point on the conversation."

# TODO add all subsequent models
models = {
    "openai_models": [
        "gpt-4o",
        "gpt-4o-2024-05-13",
        "gpt-4o-mini",
        "gpt-4o-mini-2024-07-18",
        "gpt-4-turbo",
        "gpt-4-turbo-2024-04-09",
    ],
    "claude_models": [
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "together_models": [
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3-8B-Instruct-Lite",
        "meta-llama/Meta-Llama-3-70B-Instruct-Lite",
        "deepseek-ai/deepseek-llm-67b-chat",
        "deepseek-ai/deepseek-coder-33b-instruct",
        "codellama/CodeLlama-13b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
        "codellama/CodeLlama-70b-Instruct-hf",
        "Qwen/Qwen2-72B-Instruct",
        "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
        "NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT",
        "mistralai/Mistral-7B-Instruct-v0.3",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
    ]
}
