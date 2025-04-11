from crewai import Agent, Crew, Process, Task, LLM
from src.datespot_v2.schema.schema import DetailExtractionOutputSchema, DateSpotListSchema, DateSpotReviewListSchema
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import yaml
import asyncio
import time
import json


with open('src/datespot_v2/config/agents.yaml', 'r') as file:
    agents_config = yaml.safe_load(file)

with open('src/datespot_v2/config/tasks.yaml', 'r') as file:
    tasks_config = yaml.safe_load(file)

def get_extarcter_crew():
    detail_extracter = Agent(
                role = agents_config['detail_extracter']["role"],
                goal = agents_config['detail_extracter']["goal"],
                backstory = agents_config['detail_extracter']["backstory"],
                llm=LLM(model='openai/gpt-4o-mini'),
                allow_delegation=False,
                verbose=True
            )
    detail_extraction_task = Task(
                description = tasks_config['detail_extraction_task']["description"],
                agent = detail_extracter,
                expected_output = tasks_config['detail_extraction_task']["expected_output"],
                output_pydantic = DetailExtractionOutputSchema
            )
    return Crew(agents=[detail_extracter], tasks=[detail_extraction_task])

def get_finder_crew():
    datespot_finder = Agent(
                role = agents_config['datespot_finder']["role"],
                goal = agents_config['datespot_finder']["goal"],
                backstory = agents_config['datespot_finder']["backstory"],
                llm=LLM(model='openai/gpt-4o'),
                allow_delegation=False,
                verbose=True
            )

    datespot_search_task_web = Task(
                description = tasks_config['datespot_search_task_web']["description"],
                agent = datespot_finder,
                expected_output = tasks_config['datespot_search_task_web']["expected_output"],
                output_pydantic = DateSpotListSchema,
                tools = [SerperDevTool(), ScrapeWebsiteTool()]
            )
    
    datespot_reviewer = Agent(
                role = agents_config['datespot_reviewer']["role"],
                goal = agents_config['datespot_reviewer']["goal"],
                backstory = agents_config['datespot_reviewer']["backstory"],
                llm=LLM(model='openai/gpt-4o-mini'),
                allow_delegation=False,
                verbose=True
            )

    datespot_review_task = Task(
                description = tasks_config['datespot_review_task']["description"],
                agent = datespot_reviewer,
                expected_output = tasks_config['datespot_review_task']["expected_output"],
                output_pydantic = DateSpotReviewListSchema
            )
    return Crew(agents=[datespot_finder, datespot_reviewer], tasks = [datespot_search_task_web, datespot_review_task])

def get_deduplication_crew():
    deduplication_agent = Agent(
        role="Data Cleaner",
        goal="Deduplicate location entries and merge their data fields intelligently",
        backstory="You are a skilled data wrangler specializing in cleaning and harmonizing structured location data",
        llm=LLM(model='openai/gpt-4o-mini'),
        verbose = False
    )

    # Define the task
    deduplicate_task = Task(
        description=(
            "You are provided with a list of locations, which may contain duplicate entries "
            "based on the 'name' field. Your task is to deduplicate this list. If multiple entries share the same name, "
            "merge their information as follows:\n\n"
            "- Keep the first instance as the base.\n"
            "- Merge the 'category' fields as a union of both lists only including unique categories.\n"
            "- Summarize the 'description' fields into one.\n"
            "- Combine 'contact_information' if they differ.\n"
            "- Use the higher value for 'agent_rating'.\n"
            "- Summarize 'reasoning' into one.\n"
            "- Keep the 'website' instancde that looks right\n"
            "- If the 'image_url' doesn't look right or there is no value, keep it as empty otherwise keep the instance that looks legit\n\n"
            "Input List: {overall_finds}"
        ),
        agent=deduplication_agent,
        expected_output="A deduplicated list of locations with modified information.",
        output_pydantic= DateSpotReviewListSchema
    )
    
    return Crew(agents=[deduplication_agent], tasks=[deduplicate_task])


def calculate_cost(given_crews):
     prompt_token = 0
     for given_crew in given_crews:
         prompt_token += (given_crew.usage_metrics.prompt_tokens + given_crew.usage_metrics.completion_tokens)
     costs = 1.93 * prompt_token / 1_000_000
     return costs


