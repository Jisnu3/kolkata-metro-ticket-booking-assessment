# TESTIMONIAL

## Overall Approach

I began by understanding the project structure and identifying how the React frontend communicates with the FastAPI backend. After successfully setting up the application, I reviewed the existing APIs, database structure, and service layer to understand the flow of data. I then implemented the missing backend functionality and integrated it with the frontend while preserving the existing API contracts.

---

## Understanding the Project

The application is divided into four major components:

- React + Vite frontend
- FastAPI backend
- SQLite database for metro station and route information
- PostgreSQL database for ticket management

I studied the existing codebase, reviewed the SQLite schema documentation, and understood how different modules interacted before implementing the missing features.

---

## Bugs Encountered During Setup

During the setup process, I encountered several issues:

- Missing frontend dependency (`lucide-react`).
- SQLite database path configuration issue.
- PostgreSQL authentication failure due to incorrect credentials.
- Missing implementation in the `get_all_stations()` endpoint.
- Incomplete shortest route calculation logic in `graph_engine.py`.

---

## How I Resolved These Issues

- Installed all missing frontend dependencies.
- Corrected the SQLite database path so the backend could access the station database.
- Updated the PostgreSQL configuration to establish a successful database connection.
- Implemented the station retrieval endpoint using SQLite.
- Implemented the shortest path calculation using Dijkstra's Algorithm while preserving the existing API contract.
- Integrated the completed backend functionality with the frontend and verified successful route generation.

---

## Challenges Faced

The primary challenge was understanding an unfamiliar codebase with incomplete functionality. Implementing the routing logic while maintaining compatibility with the existing project structure and API responses required careful analysis of the database schema and service architecture.

---

## Assumptions Made

- The SQLite database already contained valid metro station and connection data.
- The existing API endpoints and response structure should remain unchanged.
- The provided database schema accurately represented the metro network.

---

## Improvements with Additional Time

If given additional time, I would implement the following improvements:

- Add unit and integration tests for backend services.
- Improve frontend validation and user-friendly error handling.
- Optimize the route calculation for larger transportation networks.
- Enhance the UI with better route visualization and loading indicators.
- Add structured logging and monitoring for backend services.
- Improve code documentation and increase overall test coverage.

---

## Summary

This assessment provided valuable experience in understanding an unfamiliar codebase, debugging application setup issues, implementing backend algorithms, integrating APIs with the frontend, and delivering a working end-to-end solution while maintaining clean and readable code.