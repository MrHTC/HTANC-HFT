# Data Stack

## Overview
Supabase PostgreSQL as the managed database, accessed via Prisma (Python) ORM. This provides a scalable, managed database with built-in auth integration and modern type-safe database access.

## Database
**Supabase (PostgreSQL)** — Managed PostgreSQL with built-in auth, real-time subscriptions, and auto-scaling. Pairs directly with Supabase Auth for seamless user management.

## ORM / Database Client
**Prisma (Python)** — Schema-first ORM providing type-safe database access, automatic migrations, and excellent DX. Integrates well with FastAPI for auto-generated API schemas.

## Decision Relationships
- Prisma's schema-first approach aligns with the project's emphasis on type safety and developer experience
- Supabase provides both database and auth, reducing operational complexity
- Prisma migrations handle schema changes cleanly alongside Supabase managed database
