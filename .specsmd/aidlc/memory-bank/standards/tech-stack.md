# Tech Stack

## Overview
Python/FastAPI backend with Next.js frontend, Supabase for auth and database, and uv for Python package management. This stack separates concerns cleanly between a high-performance async API and a modern React frontend.

## Languages
- **Python** — Backend API development (FastAPI, async ecosystem)
- **TypeScript** — Frontend application (Next.js, React)

Python chosen for its rich async ecosystem, ML/AI integration capabilities, and developer productivity. TypeScript for type safety and the mature React/Next.js ecosystem on the frontend.

## Framework
- **Backend**: FastAPI — Modern async Python framework with automatic OpenAPI docs, Pydantic validation, and type hints
- **Frontend**: Next.js (React) — SSR/SSG, file-based routing, Vercel deployment option

FastAPI enables high-throughput async endpoints with auto-generated documentation. Next.js provides a mature full-stack frontend framework with excellent DX.

## Authentication
**Supabase Auth** — Integrated with Supabase for email/password, social login, and row-level security. Seamless integration with the Supabase database backend.

## Infrastructure & Deployment
**TBD** — To be decided based on scaling requirements and budget.

## Package Manager
- **Python**: uv — Fast dependency management and virtual environments
- **Frontend**: npm / pnpm (TBD)

## Decision Relationships
- FastAPI + Supabase provides a cohesive Python-native backend stack with built-in auth and database
- Next.js frontend communicates with FastAPI via REST API
- uv chosen for Python to match the project's emphasis on modern tooling
