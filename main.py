from langchain.agents.structured_output import ProviderStrategy
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# receive a user search query
user_query = input("Please enter what you want me to search the web for: ")

# link llm (free hugging face model)
llm = HuggingFaceEndpoint(
repo_id="deepseek-ai/DeepSeek-V4-Flash-0731",
    task="text-generation",
)
model = ChatHuggingFace(llm=llm)

# create the search tool using tavily
search_tool = TavilySearch()


# define the ai agent response schema
class Source(BaseModel):
    """The schema for a source of information."""

    title: str = Field(description="The title of the source.")
    url: str = Field(description="The URL of the source.")


class AgentResponse(BaseModel):
    """The schema for the AI agent's response."""

    answer: str = Field(
        description="The result of the user query after searching the web and processing the information."
    )
    sources: list[Source] = Field(
        default_factory=list,
        description="A list of sources used to answer the user query.",
    )


# create ai agent and add to it (llm, search_tool)
search_agent = create_agent(
    model=model,
    tools=[search_tool],
    name="web-search-agent",
    response_format=ProviderStrategy(AgentResponse),
)


def main():
    print(f"The agent is searching the web for: {user_query}")
    # invoke the agent to search the web and find result for the user query + give it the conversation history
    response = search_agent.invoke({"messages": [HumanMessage(content=user_query)]})

    agent_sources = "\n".join(
        f"Title: {s.title}, URL: {s.url}" for s in response['structured_response'].sources
    )
    print(f"""
    The agent has found the following answer and sources:
    Answer: {response['structured_response'].answer}
    """)
    if response['structured_response'].sources != []:
        print(f"Sources:\n{agent_sources}")



if __name__ == "__main__":
    main()
