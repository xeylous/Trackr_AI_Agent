# agents/base_agent.py

from memory.memory_service import MemoryService
from tools.gemini_client import GeminiClient

class BaseAgent:
    def __init__(self, memory: MemoryService, llm: GeminiClient | None, name: str):
        self.memory = memory
        self.llm = llm
        self.name = name

    def handle(self, user_id: str, message: str, context: dict) -> dict:
        raise NotImplementedError("Subclasses must implement handle()")
