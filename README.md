# Hiring-Platform
# Recruitment System Backend (FastAPI)

A web based recruitment system backend built with **FastAPI**, **PostgreSQL**, **JWT authentication**, and **agentic AI** (PhiData) that can query the database using natural language.

## Features

### Core
- JWT based authentication (signup, login, current user)
- Hiring manager APIs
  - Post a job
  - List jobs created by the logged in hiring manager
- Applicant foundations (can be extended)
  - Application model support (apply to a job, list applicants, etc.)

### Agentic AI
- Hiring manager can query the database using natural language (example: “show my jobs”)
- PhiData agent connected to PostgreSQL (database connectivity to AI agents)
- Agent can call tools or run SQL queries to fetch results based on the logged in user context

## Tech Stack
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL (Docker)**
- **JWT** (python-jose)
- **Password hashing** (passlib + bcrypt)
- **PhiData** for agentic AI and Postgres tool integration

---

## Project Structure (example)

