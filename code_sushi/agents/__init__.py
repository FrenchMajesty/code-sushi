"""
Initialization file for the API module.

This module handles all external integrations, such as LLM APIs, and acts
as the interface between Code Sushi and external services.
"""
from .agent_team import AgentTeam

__all__ = ["AgentTeam"]
