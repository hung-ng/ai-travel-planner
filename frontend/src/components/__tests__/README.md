# Frontend Unit Tests

This directory contains unit tests for the AI Travel Planner frontend components and utilities.

## Test Structure

```
frontend/src/
├── components/
│   └── __tests__/
│       ├── ChatInterface.test.tsx       # Chat UI component tests
│       ├── MessageBubble.test.tsx       # Message display component tests
│       └── LoadingSpinner.test.tsx      # Loading indicator tests
└── lib/
    └── __tests__/
        └── api.test.ts                  # API client tests
```

## Setup

### Install Dependencies

```bash
cd frontend
npm install
```

The following testing packages are included:
- `jest` - Test framework
- `@testing-library/react` - React component testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers for DOM
- `@testing-library/user-event` - User interaction simulation
- `jest-environment-jsdom` - Browser-like environment for tests

## Running Tests

### Run All Tests

```bash
npm test
```

### Watch Mode (Re-run on file changes)

```bash
npm run test:watch
```

### Coverage Report

```bash
npm run test:coverage
```

This generates a coverage report in `coverage/` directory. Open `coverage/lcov-report/index.html` to view detailed coverage.

### Run Specific Test File

```bash
# Test specific component
npm test ChatInterface

# Test specific file with full path
npm test src/components/__tests__/MessageBubble.test.tsx
```

### Run Tests Matching Pattern

```bash
# Run tests with "user message" in describe/it blocks
npm test -- -t "user message"
```

## Test Coverage

### Components

#### LoadingSpinner (`LoadingSpinner.test.tsx`)
- ✅ Renders three animated dots
- ✅ Applies correct styling and animations
- ✅ Animation delays for bouncing effect
- ✅ Flex container layout

#### MessageBubble (`MessageBubble.test.tsx`)
- ✅ Renders user and assistant messages
- ✅ Different styling for user vs assistant messages
- ✅ Timestamp display and formatting
- ✅ Handles messages without timestamps
- ✅ Preserves whitespace and line breaks
- ✅ Word breaking for long text
- ✅ Special character rendering
- ✅ Correct width, padding, and border radius

#### ChatInterface (`ChatInterface.test.tsx`)
- ✅ Initial render with welcome message
- ✅ Quick prompts display and filtering
- ✅ Category selection
- ✅ Message sending via button and Enter key
- ✅ Input clearing after send
- ✅ Loading state management
- ✅ AI response display
- ✅ Conversation history
- ✅ Keyboard shortcuts (Enter vs Shift+Enter)
- ✅ Empty message validation
- ✅ UI feature toggles
- ✅ Accessibility attributes

### Utilities

#### API Client (`api.test.ts`)
- ✅ Health check endpoint
- ✅ Send message (POST /api/chat/message)
- ✅ Create trip (POST /api/trips/)
- ✅ Get single trip (GET /api/trips/:id)
- ✅ Get all trips (GET /api/trips/)
- ✅ Request/response structure validation
- ✅ Error handling
- ✅ HTTP method verification

## Writing New Tests

### Component Test Template

```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MyComponent from '../MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)

    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('handles user interaction', async () => {
    const user = userEvent.setup()
    render(<MyComponent />)

    const button = screen.getByRole('button', { name: /click me/i })
    await user.click(button)

    expect(screen.getByText('Clicked!')).toBeInTheDocument()
  })
})
```

### API Test Template

```typescript
import axios from 'axios'
import { api } from '../api'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Method', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('calls the correct endpoint', async () => {
    const mockResponse = { data: { result: 'success' } }
    const mockGet = jest.fn().mockResolvedValue(mockResponse)

    mockedAxios.create = jest.fn(() => ({
      get: mockGet,
    })) as any

    jest.isolateModules(async () => {
      const { api: freshApi } = require('../api')
      await freshApi.myMethod()

      expect(mockGet).toHaveBeenCalledWith('/expected/endpoint')
    })
  })
})
```

## Testing Best Practices

### 1. Test Behavior, Not Implementation

❌ **Bad**: Testing internal state
```tsx
expect(component.state.count).toBe(5)
```

✅ **Good**: Testing visible output
```tsx
expect(screen.getByText('Count: 5')).toBeInTheDocument()
```

### 2. Use Accessible Queries

Prefer queries that reflect how users interact:

1. `getByRole` - Best for interactive elements
2. `getByLabelText` - Good for form inputs
3. `getByPlaceholderText` - For inputs with placeholders
4. `getByText` - For text content
5. `getByTestId` - Last resort

### 3. Wait for Async Updates

Always use `waitFor` for async state changes:

```tsx
await waitFor(() => {
  expect(screen.getByText('Loaded!')).toBeInTheDocument()
})
```

### 4. Clean Up Between Tests

- Jest automatically cleans up rendered components
- Clear mocks in `beforeEach`:

```tsx
beforeEach(() => {
  jest.clearAllMocks()
})
```

### 5. Test User Interactions

Use `@testing-library/user-event` instead of `fireEvent`:

```tsx
const user = userEvent.setup()
await user.click(button)
await user.type(input, 'text')
```

### 6. Group Related Tests

Use `describe` blocks to organize tests:

```tsx
describe('MyComponent', () => {
  describe('Initial Render', () => {
    it('displays header', () => { ... })
  })

  describe('User Interactions', () => {
    it('handles click', () => { ... })
  })
})
```

## Common Issues and Solutions

### Issue: "Cannot find module '@/...'"

**Solution**: Path aliases are configured in `jest.config.js`:
```javascript
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
}
```

### Issue: "ReferenceError: fetch is not defined"

**Solution**: Use `jest-environment-jsdom` (already configured in `jest.config.js`)

### Issue: Tests timing out

**Solution**: Increase timeout or check for unresolved promises:
```tsx
await waitFor(() => {
  expect(screen.getByText('Result')).toBeInTheDocument()
}, { timeout: 3000 })
```

### Issue: "Not wrapped in act(...)"

**Solution**: Use `waitFor` or `findBy` queries for async updates:
```tsx
// Use findBy instead of getBy for async content
const element = await screen.findByText('Async content')
```

## Debugging Tests

### View Rendered Output

```tsx
import { render, screen } from '@testing-library/react'

const { debug } = render(<MyComponent />)
debug() // Prints the entire DOM
screen.debug() // Prints current state
```

### Run Single Test

```bash
npm test -- -t "specific test name"
```

### Verbose Output

```bash
npm test -- --verbose
```

## Coverage Goals

Target coverage thresholds (configured in `jest.config.js`):
- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

To view coverage for specific files:
```bash
npm run test:coverage -- --collectCoverageFrom='src/components/ChatInterface.tsx'
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Install dependencies
npm ci

# Run tests with coverage
npm run test:coverage -- --ci --coverage --maxWorkers=2

# Tests should exit with code 0 on success
```

## Additional Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)
- [Common Testing Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [User Event API](https://testing-library.com/docs/user-event/intro)
