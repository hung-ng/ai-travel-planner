from app.services.ai_service import ai_service
from app.services.rag_service import rag_service

class ConversationService:
    async def process_message(self, user_message: str, conversation_history: list, trip_context: dict):
        """Process user message and generate response"""
        
        # 1. Get relevant context from RAG
        rag_results = await rag_service.search(user_message)
        context = "\n".join(rag_results['documents'][0]) if rag_results['documents'] else ""
        
        # 2. Build prompt with context
        system_prompt = f"""You are a helpful travel planning assistant. 
        Use this travel knowledge to help plan trips:
        {context}
        
        Current trip context: {trip_context}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history,
            {"role": "user", "content": user_message}
        ]
        print(messages)
        
        # 3. Get AI response
        response = await ai_service.chat_completion(messages)
        
        return response

conversation_service = ConversationService()