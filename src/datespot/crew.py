from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from src.datespot.schema.schema import DetailExtractionOutputSchema, DateSpotReviewSchema
# from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from src.datespot.tools.custom_tool import CustomSerperPlaceTool
import streamlit as st

@CrewBase
class Datespot():
    """Datespot crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def detail_extracter(self) -> Agent:
        return Agent(
            config=self.agents_config['detail_extracter'],
            llm = LLM(model = 'openai/gpt-4o-mini'),
            allow_delegation=False,
            verbose=True
        )
    
    @agent
    def datespot_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['datespot_finder'],
            llm = LLM(model = 'openai/gpt-4o-mini'),
            allow_delegation=False,
            verbose=True
        )

    @agent
    def datespot_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['datespot_reviewer'],
            llm = LLM(model = 'openai/gpt-4o-mini'),
            verbose=True
        )
        
        
    @task
    def detail_extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config['detail_extraction_task'],
            output_pydantic = DetailExtractionOutputSchema,
        )

    @task
    def datespot_search_task_api(self) -> Task:
        return Task(
            config=self.tasks_config['datespot_search_task_api'],
            tools = [CustomSerperPlaceTool(result_as_answer=True)],
            # output_pydantic = DateSpotListSchema,
            # output_file = "places_found.json"
        )

    @task
    def datespot_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['datespot_review_task'],
            output_pydantic = DateSpotReviewSchema
        )

    

    @crew
    def crew(self) -> Crew:
        """Creates the Datespot crew"""
        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
