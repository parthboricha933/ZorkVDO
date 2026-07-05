"""Pydantic models — request/response DTOs for the API.

These are deliberately separate from the persistence layer: a model can
be returned to the user without leaking internal fields like `password_hash`.
"""
