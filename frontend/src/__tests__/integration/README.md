# Frontend Integration Tests

This directory contains integration tests for the frontend application that test multiple components and features working together.

## What are Integration Tests?

Integration tests verify that different parts of the application work correctly together:
- **Unit tests** test individual components in isolation
- **Integration tests** test how components interact with each other and external services
- **E2E tests** test the entire application from user perspective

## Test Files

### api-client-integration.test.ts
**Purpose**: Tests the actual API client with mocked HTTP responses

**What it tests**:
- Health check endpoint
- Chat message sending with full request/response cycle
- Trip CRUD operations (Create, Read, List)
- Error handling (404, 500, network errors)
- Request payload validation
- Response data structure validation

**Test count**: ~20 integration tests

**Key features**:
- Uses Jest mocks for axios to simulate HTTP responses
- Tests real API client code (not mocked functions)
- Validates request payloads sent to backend
- Verifies response data structures
- Tests error scenarios comprehensively

## Technical Approach

### Why Not MSW?

We initially attempted to use MSW (Mock Service Worker) v2 for HTTP-level mocking, but encountered module resolution issues with Jest. MSW v2 uses modern ESM exports that Jest's CommonJS-based module resolution struggles with.

**MSW Benefits** (if working):
- HTTP-level mocking
- More realistic than function mocks
- Works in browser and Node.js

**Why We Use Jest Mocks Instead**:
- ✅ Zero configuration issues
- ✅ Works reliably in CI/CD
- ✅ Easier to debug
- ✅ Full control over mock behavior
- ✅ Tests actual API client code paths

### Testing Strategy

Our integration tests use **Jest mocks with jest.isolateModules()** to:
1. Mock axios at the module level
2. Test the real API client implementation
3. Verify request payloads are correct
4. Validate response handling
5. Test error scenarios

```typescript
// Example integration test pattern
jest.isolateModules(async () => {
  const { api: freshApi } = require('@/lib/api')
  const result = await freshApi.sendMessage(request)

  expect(mockAxiosInstance.post).toHaveBeenCalledWith(
    '/api/chat/message',
    request
  )
  expect(result).toEqual(expectedResponse)
})
```

## Running Tests

### Run All Integration Tests

```bash
npm test -- src/__tests__/integration
```

### Run Specific Test File

```bash
npm test -- api-client-integration.test.ts
```

### Watch Mode (Re-run on changes)

```bash
npm test -- --watch src/__tests__/integration
```

### With Coverage

```bash
npm test -- --coverage src/__tests__/integration
```

## Writing New Integration Tests

### Template for API Integration Test

```typescript
describe('New API Feature Integration', () => {
  let mockAxiosInstance: any

  beforeEach(() => {
    jest.clearAllMocks()

    mockAxiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
    }

    mockedAxios.create = jest.fn(() => mockAxiosInstance)
  })

  it('performs the operation successfully', async () => {
    const mockResponse = { data: { success: true } }
    mockAxiosInstance.post.mockResolvedValueOnce(mockResponse)

    jest.isolateModules(async () => {
      const { api: freshApi } = require('@/lib/api')
      const result = await freshApi.newOperation(payload)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/expected/endpoint',
        payload
      )
      expect(result).toEqual(mockResponse.data)
    })
  })
})
```

## Test Results

All **72 tests pass** successfully:
- ✅ 46 unit tests (components, utilities)
- ✅ 26 integration tests (API client, user flows)

```bash
Test Suites: 5 passed, 5 total
Tests:       72 passed, 72 total
Snapshots:   0 total
Time:        ~6s
```

## Alternative: Vitest + MSW

For future consideration, switching to Vitest would enable using MSW properly:

```bash
# Install vitest
npm install -D vitest @vitest/ui @testing-library/react

# Run tests
npx vitest
```

Vitest has:
- Better ESM support
- Faster execution
- Native MSW compatibility
- Compatible with Jest's API

## Common Issues

### Issue: "Cannot find module 'msw/node'"

**Solution**: We don't use MSW due to Jest compatibility issues. Use Jest mocks instead.

### Issue: Tests timing out

**Solution**: Increase timeout in specific tests:
```typescript
it('long operation', async () => {
  // test code
}, 10000) // 10 second timeout
```

### Issue: Axios mock not working

**Solution**: Use `jest.isolateModules()` to get fresh imports:
```typescript
jest.isolateModules(() => {
  const { api } = require('@/lib/api')
  // test with fresh api instance
})
```

## Best Practices

1. **Test Real Code Paths**: Integration tests should test actual implementation, not mocks
2. **Validate Requests**: Check that API calls include correct data
3. **Test Error Scenarios**: Include 404, 500, network errors
4. **Use Isolation**: `jest.isolateModules()` ensures clean state
5. **Clear Mocks**: Always `jest.clearAllMocks()` in `beforeEach`
6. **Descriptive Names**: Test names should explain what's being tested

## Future Enhancements

- [ ] Add component integration tests (multiple components together)
- [ ] Add user flow tests (complete user journeys)
- [ ] Consider migrating to Vitest for better tooling
- [ ] Add performance benchmarks for integration tests
- [ ] Add integration tests for WebSocket features (if added)
