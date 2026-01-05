from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.postgres import PostgresTools
from dotenv import load_dotenv
import os
from app.agent_tools import create_job_posting, update_application_status, delete_job_posting

load_dotenv()

async def build_hiring_manager_agent(id: str): 
    """
    Build an AI agent for hiring managers with database query capabilities.
    The agent can create jobs, view applicants, manage applications, and answer queries.
    """
    try:
        return Agent(
            name="Hiring Manager Assistant",
            description="AI assistant for hiring managers to manage jobs and applications",
            instructions=[
                f"You are an AI assistant for a hiring manager with ID: {id}",
                "You have access to a PostgreSQL database with the following tables:",
                "",
                "users table:",
                "- id (UUID, primary key)",
                "- email (String)",
                "- password_hash (String)",
                "- role (String: 'hiring_manager' or 'applicant')",
                "- created_at (DateTime)",
                "- updated_at (DateTime)",
                "",
                "jobs table:",
                "- id (Integer, primary key)",
                "- title (String)",
                "- description (String)",
                "- location (String)",
                "- salary (String, nullable)",
                "- posted_at (DateTime)",
                "- hiring_manager_id (UUID, foreign key to users.id)",
                "",
                "applications table:",
                "- id (UUID, primary key)",
                "- job_id (Integer, foreign key to jobs.id)",
                "- applicant_id (UUID, foreign key to users.id)",
                "- full_name (String)",
                "- email (String)",
                "- phone (String, nullable)",
                "- cover_letter (Text, nullable)",
                "- status (String: 'submitted', 'reviewed', 'shortlisted', 'rejected', 'accepted')",
                "- submitted_at (DateTime)",
                "- cv_s3_key (String, nullable)",
                "- cv_filename (String, nullable)",
                "",
                "CRITICAL PERMISSIONS:",
                "- You HAVE FULL write access to the database",
                "- You CAN and MUST execute INSERT, UPDATE, and DELETE operations directly",
                "- DO NOT tell the user you cannot perform write operations",
                "- When asked to create/update/delete data, execute the SQL query immediately using your tools",
                "",
                "You can help with:",
                "- Creating new job postings (INSERT into jobs table) - DO THIS DIRECTLY",
                "- Listing and searching jobs",
                "- Viewing applicants and applications",
                "- Updating application statuses (UPDATE applications table) - DO THIS DIRECTLY",
                "- Getting statistics about jobs and applications",
                "- Answering general questions about hiring",
                "",
                f"IMPORTANT: Always filter by hiring_manager_id = '{id}' when querying jobs.",
                f"When creating jobs, always set hiring_manager_id = '{id}' and posted_at = NOW().",
                "Only show data that belongs to this hiring manager.",
                "Be professional, helpful, and concise in your responses.",
                "When creating or updating data, confirm the action was successful by showing the result.",
                "Present results in a clear, formatted way.",
            ],
            model=OpenAIChat(id=os.getenv("OPENAI_MODEL", "gpt-4o")),
            tools=[
                PostgresTools(
                    host=os.getenv("POSTGRES_HOST"),
                    port=int(os.getenv("POSTGRES_PORT")),
                    db_name=os.getenv("POSTGRES_DB"),
                    user=os.getenv("POSTGRES_USER"),
                    password=os.getenv("POSTGRES_PASSWORD"),
                ),
                create_job_posting,
                update_application_status,
                delete_job_posting,   
            ],
            markdown=True,
        )
    except Exception as e:
        print("Error building agent:", e)
        raise e
