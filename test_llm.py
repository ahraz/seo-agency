from tools.llm import get_llm

llm = get_llm()

response = llm.call(
    "Reply only with: DeepSeek connection successful"
)

print(response)
