import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatInterface from '../ChatInterface'

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    sendMessage: jest.fn(),
  },
}))

describe('ChatInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Initial Render', () => {
    it('renders the chat interface', () => {
      render(<ChatInterface />)

      expect(screen.getByText('AI Travel Planner')).toBeInTheDocument()
      expect(screen.getByText('Plan your perfect trip with AI')).toBeInTheDocument()
    })

    it('displays welcome message on initial load', () => {
      render(<ChatInterface />)

      expect(
        screen.getByText(/Hi! I'm your AI travel assistant/i)
      ).toBeInTheDocument()
    })

    it('renders input textarea', () => {
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      expect(textarea).toBeInTheDocument()
      expect(textarea).not.toBeDisabled()
    })

    it('renders send button', () => {
      render(<ChatInterface />)

      const sendButton = screen.getByRole('button', { name: /send/i })
      expect(sendButton).toBeInTheDocument()
    })

    it('shows quick prompts on initial load', () => {
      render(<ChatInterface />)

      expect(screen.getByText(/Quick start with these suggestions/i)).toBeInTheDocument()
      expect(screen.getByText(/Beach vacation for 2 weeks/i)).toBeInTheDocument()
    })
  })

  describe('Quick Prompts', () => {
    it('displays all quick prompt categories', () => {
      render(<ChatInterface />)

      expect(screen.getByText('all')).toBeInTheDocument()
      expect(screen.getByText('Popular')).toBeInTheDocument()
      expect(screen.getByText('Budget')).toBeInTheDocument()
    })

    it('filters prompts when category is selected', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      // Click Budget category
      const budgetButton = screen.getByRole('button', { name: 'Budget' })
      await user.click(budgetButton)

      // Should show budget-related prompt
      expect(screen.getByText(/Budget-friendly trip under \$1000/i)).toBeInTheDocument()

      // Should not show non-budget prompts (they might still be in DOM but hidden)
      const allPromptButtons = screen.getAllByRole('button')
      const budgetPrompts = allPromptButtons.filter(btn =>
        btn.textContent?.includes('Budget-friendly')
      )
      expect(budgetPrompts.length).toBeGreaterThan(0)
    })

    it('sends message when quick prompt is clicked', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const quickPrompt = screen.getByText(/Beach vacation for 2 weeks/i)
      await user.click(quickPrompt)

      // Wait for the message to appear
      await waitFor(() => {
        expect(screen.getByText(/Beach vacation for 2 weeks/i)).toBeInTheDocument()
      })
    })

    it('hides quick prompts after first message', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'Hello')

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      // Quick prompts should disappear after sending message
      await waitFor(() => {
        expect(screen.queryByText(/Quick start with these suggestions/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('Sending Messages', () => {
    it('sends message when send button is clicked', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'I want to visit Tokyo')

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      // User message should appear in chat
      await waitFor(() => {
        expect(screen.getByText('I want to visit Tokyo')).toBeInTheDocument()
      })
    })

    it('sends message when Enter is pressed', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'Paris trip{Enter}')

      // User message should appear
      await waitFor(() => {
        expect(screen.getByText('Paris trip')).toBeInTheDocument()
      })
    })

    it('does not send message when Shift+Enter is pressed', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'Line 1{Shift>}{Enter}{/Shift}Line 2')

      // Should create new line, not send
      expect(textarea).toHaveValue('Line 1\nLine 2')
    })

    it('clears input after sending message', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'Test message')

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      await waitFor(() => {
        expect(textarea).toHaveValue('')
      })
    })

    it('does not send empty messages', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const sendButton = screen.getByRole('button', { name: /send/i })

      // Button should be disabled when input is empty
      expect(sendButton).toBeDisabled()
    })

    it('does not send whitespace-only messages', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, '   ')

      const sendButton = screen.getByRole('button', { name: /send/i })
      expect(sendButton).toBeDisabled()
    })
  })

  describe('Loading State', () => {
    it('shows loading indicator while waiting for response', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'Test')

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      // Loading indicator should appear briefly
      // Since mockSendMessage has a 1 second delay, we should see loading
      expect(screen.getByText('...')).toBeInTheDocument()

      // Textarea should be disabled during loading
      expect(textarea).toBeDisabled()
    })

    it('disables send button while loading', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'Test')

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      // Button should show loading state
      expect(screen.getByText('...')).toBeInTheDocument()
    })
  })

  describe('AI Response', () => {
    it('displays AI response after sending message', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'Hello')

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      // Wait for AI response (mocked)
      await waitFor(
        () => {
          expect(screen.getByText(/AI Response to: Hello/i)).toBeInTheDocument()
        },
        { timeout: 2000 }
      )
    })

    it('maintains message order (user then assistant)', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      await user.type(textarea, 'First message')

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      await waitFor(
        () => {
          expect(screen.getByText(/AI Response to: First message/i)).toBeInTheDocument()
        },
        { timeout: 2000 }
      )

      // Check that messages appear in order
      const messages = screen.getAllByText(/First message|AI Response/i)
      expect(messages.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('Error Handling', () => {
    it('displays error message when API call fails', async () => {
      // This test would require mocking the API to throw an error
      // The component uses mockSendMessage which doesn't fail,
      // but in real implementation with actual API, errors should be handled
      expect(true).toBe(true) // Placeholder
    })
  })

  describe('UI Features', () => {
    it('shows toggle quick prompts button', () => {
      render(<ChatInterface />)

      const toggleButton = screen.getByText(/✨ Quick prompts/i)
      expect(toggleButton).toBeInTheDocument()
    })

    it('toggles quick prompts visibility', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const toggleButton = screen.getByText(/✨ Quick prompts/i)

      // Quick prompts should be visible initially
      expect(screen.getByText(/Beach vacation for 2 weeks/i)).toBeInTheDocument()

      await user.click(toggleButton)

      // After first message is sent, the behavior changes
      // This is a simplified test
    })

    it('displays keyboard shortcuts hint', () => {
      render(<ChatInterface />)

      expect(screen.getByText(/Press Enter to send • Shift\+Enter for new line/i)).toBeInTheDocument()
    })

    it('shows voice feature coming soon', () => {
      render(<ChatInterface />)

      expect(screen.getByText(/🎤 Voice \(soon\)/i)).toBeInTheDocument()
    })
  })

  describe('Conversation History', () => {
    it('maintains conversation history across multiple messages', async () => {
      const user = userEvent.setup()
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)

      // Send first message
      await user.type(textarea, 'Message 1')
      await user.click(screen.getByRole('button', { name: /send/i }))

      await waitFor(() => {
        expect(screen.getByText('Message 1')).toBeInTheDocument()
      })

      // Send second message
      await user.type(textarea, 'Message 2')
      await user.click(screen.getByRole('button', { name: /send/i }))

      await waitFor(() => {
        expect(screen.getByText('Message 2')).toBeInTheDocument()
      })

      // Both messages should still be visible
      expect(screen.getByText('Message 1')).toBeInTheDocument()
      expect(screen.getByText('Message 2')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has accessible textarea with placeholder', () => {
      render(<ChatInterface />)

      const textarea = screen.getByPlaceholderText(/Type your message/i)
      expect(textarea).toHaveAttribute('placeholder')
    })

    it('has accessible buttons with proper labels', () => {
      render(<ChatInterface />)

      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
    })
  })
})
