'use client';

import {useState, useRef, useEffect} from 'react';
import {api} from '@/lib/api';
import {Message} from '@/types';
import MessageBubble from './MessageBubble';
import LoadingSpinner from './LoadingSpinner';

const mockSendMessage = async (message: string) => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  return {
    message: `AI Response to: ${message}`,
    conversation_id: 1
  };
};

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const quickPrompts = [
  { icon: '🏖️', text: 'Beach vacation for 2 weeks', category: 'Popular' },
  { icon: '🏔️', text: 'Mountain hiking adventure', category: 'Popular' },
  { icon: '🌆', text: 'City tour with culture & food', category: 'Popular' },
  { icon: '💰', text: 'Budget-friendly trip under $1000', category: 'Budget' },
  { icon: '✈️', text: 'Weekend getaway ideas', category: 'Quick' },
  { icon: '🍷', text: 'Food and wine tour', category: 'Experience' },
  { icon: '👨‍👩‍👧‍👦', text: 'Family-friendly destinations', category: 'Family' },
  { icon: '🎒', text: 'Solo backpacking trip', category: 'Adventure' },
];

const suggestionsByContext = {
  initial: [
    'Tell me about your ideal destination',
    'What\'s your budget range?',
    'How many days are you planning?',
    'Any specific interests or activities?'
  ],
  destination: [
    'What are the must-see attractions?',
    'Recommend local restaurants',
    'Best time to visit?',
    'Transportation options'
  ],
  budget: [
    'How can I save money?',
    'Budget accommodation options',
    'Free activities in the area',
    'Cost breakdown by category'
  ],
  activities: [
    'Day trip ideas',
    'Evening entertainment',
    'Hidden gems',
    'Local experiences'
  ]
};

export default function EnhancedChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I'm your AI travel assistant. Tell me about your dream trip and I'll help you plan it! 🌍",
      timestamp: new Date(),
    },
  ]);
  
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showQuickPrompts, setShowQuickPrompts] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: textToSend,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setShowQuickPrompts(false);

    try {
      const response = await mockSendMessage(textToSend);
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: "Sorry, I'm having trouble connecting. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPrompt = (promptText: string) => {
    handleSend(promptText);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const categories = ['all', ...Array.from(new Set(quickPrompts.map(p => p.category)))];
  const filteredPrompts = selectedCategory === 'all' 
    ? quickPrompts 
    : quickPrompts.filter(p => p.category === selectedCategory);

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="flex flex-col h-[700px] bg-white rounded-lg shadow-lg border border-gray-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-lg">
          <h2 className="text-xl font-semibold">AI Travel Planner</h2>
          <p className="text-sm text-blue-100">Plan your perfect trip with AI</p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            return (
              <div key={idx} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                  isUser 
                    ? 'bg-blue-500 text-white rounded-br-none'
                    : 'bg-gray-200 text-gray-900 rounded-bl-none'
                }`}>
                  <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                  <p className={`text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            );
          })}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 rounded-2xl px-4 py-3 rounded-bl-none">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}

          {/* Prompts */}
          {showQuickPrompts && messages.length <= 2 && (
            <div className="space-y-3">
              <div className="text-center">
                <p className="text-sm text-gray-500 mb-3">Quick start with these suggestions:</p>
                
                {/* Category */}
                <div className="flex flex-wrap gap-2 justify-center mb-4">
                  {categories.map(cat => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        selectedCategory === cat
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {filteredPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleQuickPrompt(prompt.text)}
                    className="flex items-center gap-2 p-3 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg hover:from-blue-100 hover:to-purple-100 transition-all text-left group"
                  >
                    <span className="text-2xl">{prompt.icon}</span>
                    <div className="flex-1">
                      <span className="text-sm font-medium text-gray-700 group-hover:text-blue-700">
                        {prompt.text}
                      </span>
                      <span className="block text-xs text-gray-500">{prompt.category}</span>
                    </div>
                    <svg className="w-4 h-4 text-gray-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Suggestions */}
          {!showQuickPrompts && messages.length > 2 && !loading && (
            <div className="flex flex-wrap gap-2">
              <p className="w-full text-xs text-gray-500 mb-1">Suggested questions:</p>
              {suggestionsByContext.initial.slice(0, 3).map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(suggestion)}
                  className="px-3 py-1.5 bg-white border border-gray-300 rounded-full text-xs text-gray-700 hover:bg-gray-50 hover:border-blue-300 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4 bg-gray-50 rounded-b-lg">
          <div className="flex gap-2 mb-2">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Shift+Enter for new line)"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={2}
              disabled={loading}
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium self-end"
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              <button
                onClick={() => setShowQuickPrompts(!showQuickPrompts)}
                className="px-3 py-1 text-xs bg-white border border-gray-300 rounded-full text-gray-600 hover:bg-gray-50 transition-colors"
              >
                ✨ Quick prompts
              </button>
              <button className="px-3 py-1 text-xs bg-white border border-gray-300 rounded-full text-gray-600 hover:bg-gray-50 transition-colors">
                🎤 Voice (soon)
              </button>
            </div>
            <p className="text-xs text-gray-500">
              Press Enter to send • Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}