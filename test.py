from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=300
)

test_prompt = """
    Hello
"""

response = llm.invoke(test_prompt)
print("🔍 LLM Test Response:", response)