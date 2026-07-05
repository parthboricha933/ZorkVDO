"""Business-logic services.

Each service is plain Python — no FastAPI imports — so it's trivially
testable without spinning up an HTTP server. Services receive their
dependencies (repositories, storage, AI client) via constructor
injection.
"""
