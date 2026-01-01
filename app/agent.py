from phi.agent import Agent
from phi.tools.postgres import PostgresTools
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize PostgresTools with connection details
postgres_tools = PostgresTools(
    host=os.getenv("POSTGRES_HOST"),
    port=int(os.getenv("POSTGRES_PORT")),
    db_name=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"), 
    password=os.getenv("POSTGRES_PASSWORD")
)

async def build_hiring_manager_agent(id:str): 
    return Agent(instructions=[
    f"Current hiring_manager_id is {id}.",],
    tools=[postgres_tools])
