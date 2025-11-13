import { render, screen } from '@testing-library/react'
import MessageBubble from '../MessageBubble'
import { Message } from '@/types'

describe('MessageBubble', () => {
  const mockUserMessage: Message = {
    role: 'user',
    content: 'Hello, I want to plan a trip to Paris',
    timestamp: new Date('2024-01-15T10:30:00'),
  }

  const mockAssistantMessage: Message = {
    role: 'assistant',
    content: 'Great! Paris is a wonderful destination. Let me help you plan your trip.',
    timestamp: new Date('2024-01-15T10:30:05'),
  }

  describe('User Messages', () => {
    it('renders user message content', () => {
      render(<MessageBubble message={mockUserMessage} />)

      expect(screen.getByText(mockUserMessage.content)).toBeInTheDocument()
    })

    it('applies correct styling for user messages', () => {
      const { container } = render(<MessageBubble message={mockUserMessage} />)

      // Check for justify-end (right alignment)
      const wrapper = container.querySelector('.justify-end')
      expect(wrapper).toBeInTheDocument()

      // Check for blue background
      const bubble = container.querySelector('.bg-blue-500')
      expect(bubble).toBeInTheDocument()
      expect(bubble).toHaveClass('text-white', 'rounded-br-none')
    })

    it('displays timestamp for user messages', () => {
      render(<MessageBubble message={mockUserMessage} />)

      expect(screen.getByText('10:30 AM')).toBeInTheDocument()
    })

    it('applies light blue text color to user message timestamp', () => {
      const { container } = render(<MessageBubble message={mockUserMessage} />)

      const timestamp = screen.getByText('10:30 AM')
      expect(timestamp).toHaveClass('text-blue-100')
    })
  })

  describe('Assistant Messages', () => {
    it('renders assistant message content', () => {
      render(<MessageBubble message={mockAssistantMessage} />)

      expect(screen.getByText(mockAssistantMessage.content)).toBeInTheDocument()
    })

    it('applies correct styling for assistant messages', () => {
      const { container } = render(<MessageBubble message={mockAssistantMessage} />)

      // Check for justify-start (left alignment)
      const wrapper = container.querySelector('.justify-start')
      expect(wrapper).toBeInTheDocument()

      // Check for gray background
      const bubble = container.querySelector('.bg-gray-200')
      expect(bubble).toBeInTheDocument()
      expect(bubble).toHaveClass('text-gray-900', 'rounded-bl-none')
    })

    it('displays timestamp for assistant messages', () => {
      render(<MessageBubble message={mockAssistantMessage} />)

      expect(screen.getByText('10:30 AM')).toBeInTheDocument()
    })

    it('applies gray text color to assistant message timestamp', () => {
      render(<MessageBubble message={mockAssistantMessage} />)

      const timestamp = screen.getByText('10:30 AM')
      expect(timestamp).toHaveClass('text-gray-500')
    })
  })

  describe('Message Without Timestamp', () => {
    it('does not render timestamp when not provided', () => {
      const messageWithoutTimestamp: Message = {
        role: 'user',
        content: 'Test message',
      }

      render(<MessageBubble message={messageWithoutTimestamp} />)

      // Only the content should be present
      expect(screen.getByText('Test message')).toBeInTheDocument()

      // No timestamp elements should exist
      const { container } = render(<MessageBubble message={messageWithoutTimestamp} />)
      const timestamps = container.querySelectorAll('.text-xs.mt-1')
      expect(timestamps).toHaveLength(0)
    })
  })

  describe('Content Formatting', () => {
    it('preserves whitespace and line breaks in content', () => {
      const multilineMessage: Message = {
        role: 'assistant',
        content: 'Line 1\nLine 2\nLine 3',
        timestamp: new Date(),
      }

      const { container } = render(<MessageBubble message={multilineMessage} />)

      const contentElement = container.querySelector('.whitespace-pre-wrap')
      expect(contentElement).toBeInTheDocument()
      expect(contentElement).toHaveClass('break-words')
    })

    it('handles long text with word breaking', () => {
      const longMessage: Message = {
        role: 'user',
        content: 'a'.repeat(200),
        timestamp: new Date(),
      }

      const { container } = render(<MessageBubble message={longMessage} />)

      const contentElement = container.querySelector('.break-words')
      expect(contentElement).toBeInTheDocument()
    })

    it('renders special characters correctly', () => {
      const specialCharsMessage: Message = {
        role: 'assistant',
        content: 'Hello! Check these emojis: 🎉 🌍 ✈️ & symbols < > " \' /',
        timestamp: new Date(),
      }

      render(<MessageBubble message={specialCharsMessage} />)

      expect(screen.getByText(/Hello! Check these emojis:/)).toBeInTheDocument()
    })
  })

  describe('Styling', () => {
    it('limits message width to 70%', () => {
      const { container } = render(<MessageBubble message={mockUserMessage} />)

      const bubble = container.querySelector('.max-w-\\[70\\%\\]')
      expect(bubble).toBeInTheDocument()
    })

    it('applies rounded corners correctly', () => {
      const { container } = render(<MessageBubble message={mockUserMessage} />)

      const bubble = container.querySelector('.rounded-2xl')
      expect(bubble).toBeInTheDocument()
    })

    it('applies padding to message bubble', () => {
      const { container } = render(<MessageBubble message={mockUserMessage} />)

      const bubble = container.querySelector('.px-4.py-3')
      expect(bubble).toBeInTheDocument()
    })
  })
})
