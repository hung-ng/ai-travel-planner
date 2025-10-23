import { Message } from "../types";

interface MessageBubbleProps {
     message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === 'user';
    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${
          isUser 
          ? 'bg-blue-500 text-white rounded-br-none'
           : 'bg-gray-200 text-gray-900 rounded-bl-none'
        }`}>
                <p className="whitespace-pre-wrap break-words">{message.content}</p>
                {message.timestamp && (
                    <p className={`text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
                        {new Date(message.timestamp).toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                            })}
                    </p>
                )}
            </div>
        </div>
    );
}
