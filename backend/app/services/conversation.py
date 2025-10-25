from app.services.ai import chat_service
from app.services.rag import retrieval_service
from app.services.context import context_manager, query_enhancer
from app.config import settings
import json
from typing import List, Dict


class ConversationService:
    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict],
        conversation_summary: str = None,
        conversation_context: Dict = None,
        trip_context: Dict = None,
    ) -> tuple[str, Dict, str]:
        """
        Process user message with efficient context management

        Returns:
            (ai_response, updated_context, updated_summary)
        """

        print(f"\n{'='*60}")
        print(f"[CONVERSATION] Processing message")
        print(f"[CONVERSATION] Total messages in history: {len(conversation_history)}")
        print(f"{'='*60}")

        # Step 1: Extract context from current message
        print(f"\n[CONTEXT] Extracting context...")
        all_messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]
        updated_context = context_manager.extract_context(all_messages)

        # Merge with existing context
        if conversation_context:
            updated_context = {**conversation_context, **updated_context}

        print(f"[CONTEXT] Extracted: {json.dumps(updated_context, indent=2)}")

        # Step 2: Get optimized context for AI
        print(f"\n[CONTEXT] Getting optimized context...")
        recent_messages, context_description = context_manager.get_context_for_ai(
            messages=conversation_history,
            summary=conversation_summary,
            context=updated_context,
        )

        print(
            f"[CONTEXT] Using last {len(recent_messages)} messages (from {len(conversation_history)} total)"
        )
        if context_description:
            print(f"[CONTEXT] Context description: {context_description[:200]}...")
            print(f"[CONTEXT] Context: {json.dumps(updated_context, indent=2)}")


        # Step 3: Get relevant context from RAG
        print(f"\n[RAG] Searching vector database...")

        # Enhance query with extracted context for better retrieval
        enhanced_query = query_enhancer.enhance_query(user_message, updated_context)
        if enhanced_query != user_message:
            print(f"[RAG] Original query: '{user_message}'")
            print(f"[RAG] Enhanced query: '{enhanced_query}'")

        # Create metadata filter based on context
        metadata_filter = query_enhancer.create_contextual_filter(updated_context)
        if metadata_filter:
            print(f"[RAG] Using metadata filter: {metadata_filter}")

        rag_results = await retrieval_service.search(
            query=enhanced_query,
            n_results=10,
            filter_metadata=metadata_filter
        )

        rag_context = ""
        if rag_results and rag_results.get("documents"):
            rag_documents = rag_results["documents"][0]
            rag_context = "\n\n".join(rag_documents)
            print(f"[RAG] Found {len(rag_documents)} relevant documents")

        # Step 4: Build system prompt
        print(f"\n[AI] Building system prompt...")
        system_prompt = self._build_system_prompt(
            rag_context=rag_context,
            context_description=context_description,
            trip_context=trip_context,
            conversation_context=updated_context,
        )

        # Step 5: Prepare messages for AI
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(recent_messages)
        messages.append({"role": "user", "content": user_message})

        print(f"[AI] Sending {len(messages)} messages to AI")
        print(
            f"[AI] Estimated tokens: ~{sum(len(m['content'].split()) for m in messages) * 1.3:.0f}"
        )

        # Step 6: Call AI
        response = await chat_service.get_completion(
            messages=messages,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )

        # Step 7: Check if we should summarize
        updated_summary = conversation_summary
        message_count = len(conversation_history) + 1

        if await context_manager.should_summarize(message_count, 0):
            print(f"\n[CONTEXT] Creating summary (threshold reached)...")
            updated_summary = await context_manager.create_summary(
                messages=all_messages, existing_summary=conversation_summary
            )
            print(f"[CONTEXT] Summary: {updated_summary[:200]}...")

        print(f"\n[CONVERSATION] ✅ Complete!")
        print(f"{'='*60}\n")

        return response, updated_context, updated_summary

    def _build_system_prompt(
        self,
        rag_context: str,
        context_description: str,
        trip_context: Dict,
        conversation_context: Dict = None
    ) -> str:
        """Build system prompt with all context"""

        parts = [
            "You are an expert travel planning assistant.",
        ]

        # Add context description if exists
        if context_description:
            parts.append(f"\nCONVERSATION CONTEXT:\n{context_description}")

        # Add extracted context (duration, budget, travel_style) from conversation
        if conversation_context:
            additional_context = query_enhancer.get_context_for_prompt(conversation_context)
            if additional_context:
                parts.append(f"\nUSER PREFERENCES:\n{additional_context}")

        # Add RAG context if exists
        if rag_context:
            parts.append(
                f"\nRELEVANT TRAVEL KNOWLEDGE:\n{rag_context[:4000]}"
            )  # Limit size

        # Add trip context if exists
        if trip_context:
            trip_info = json.dumps(trip_context, indent=2)
            parts.append(f"\nCURRENT TRIP:\n{trip_info}")

        # Add instructions
        parts.append(
            """
YOUR ROLE:
- Help users plan detailed, personalized travel itineraries
- Provide specific recommendations for activities, restaurants, and attractions
- Consider budget constraints, travel dates, and user preferences
- Ask clarifying questions when needed
- Be enthusiastic, friendly, and practical

RESPONSE GUIDELINES:
- Be conversational and warm
- Give specific names and details, not generic suggestions
- Include estimated costs when relevant
- If you need more information, ask specific questions
- Use the knowledge base and conversation context to give accurate information
"""
        )

        return "\n".join(parts)


# Singleton instance
conversation_service = ConversationService()
