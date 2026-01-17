# System Architecture

## Overview

This system consists of:

- **FastAPI Backend**: REST API for core operations
- **Celery Worker**: Async task processing (LLM calls, document rendering)
- **PostgreSQL**: Primary data store
- **Redis**: Cache & message broker

## Core Flows

### 1. Job Application Flow
1. User uploads resume
2. Extract key sections → JD match → Generate customized resume
3. Schedule application via worker

### 2. Resume Generation Flow
1. Extract job description
2. Map evidence from candidate profile
3. Generate resume via LLM
4. Render to PDF

### 3. Matching & Ranking
1. Parse job requirements
2. Score candidate fit
3. Return match metrics

## Project Structure

See `../` for detailed folder layout.

## Database Schema

[TODO: Add Entity-Relationship Diagram]

## API Endpoints

[See docs/api.md](api.md)
