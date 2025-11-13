"""
Service layer for business logic

Services are organized into modules:
- ai: Chat completions and embedding generation
- context: Context extraction, formatting, and management
- rag: Vector storage and retrieval
- conversation: Orchestrates AI, context, and RAG for conversations
"""

# AI services
from .ai import chat_service, embedding_service

# Context services
from .context import context_manager, context_extractor, context_formatter, query_enhancer

# RAG services
from .rag import retrieval_service, vector_store

# Conversation orchestration
from .conversation import conversation_service

__all__ = [
    # AI
    'chat_service',
    'embedding_service',

    # Context
    'context_manager',
    'context_extractor',
    'context_formatter',
    'query_enhancer',

    # RAG
    'retrieval_service',
    'vector_store',

    # Conversation
    'conversation_service',
]
