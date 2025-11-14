/**
 * Integration tests for API client with mocked axios
 * Tests the actual API client functions with mocked HTTP responses
 */
import axios from 'axios'
import { api } from '@/lib/api'
import { ChatRequest } from '@/types'

// Mock axios module
jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Client Integration Tests', () => {
  let mockAxiosInstance: any

  beforeEach(() => {
    jest.clearAllMocks()

    // Create a mock axios instance
    mockAxiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
    }

    // Mock axios.create to return our mock instance
    mockedAxios.create = jest.fn(() => mockAxiosInstance)
  })

  describe('Health Check Integration', () => {
    it('successfully makes health check request', async () => {
      const mockResponse = { data: { status: 'healthy' } }
      mockAxiosInstance.get.mockResolvedValueOnce(mockResponse)

      // Re-import api to get fresh instance with mocked axios
      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')
        const result = await freshApi.health()

        expect(result).toEqual({ status: 'healthy' })
        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health')
      })
    })

    it('handles health check errors', async () => {
      mockAxiosInstance.get.mockRejectedValueOnce(new Error('Network error'))

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')

        await expect(freshApi.health()).rejects.toThrow('Network error')
      })
    })
  })

  describe('Chat Message Integration', () => {
    it('sends chat message with correct payload', async () => {
      const request: ChatRequest = {
        message: 'I want to visit Tokyo',
        trip_id: 42,
        user_id: 100,
      }

      const mockResponse = {
        data: {
          message: 'Great! Tokyo is amazing. What interests you?',
          conversation_id: 789,
        },
      }

      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse)

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')
        const result = await freshApi.sendMessage(request)

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/chat/message',
          request
        )
        expect(result).toEqual(mockResponse.data)
        expect(result.conversation_id).toBe(789)
      })
    })

    it('sends message without optional fields', async () => {
      const request: ChatRequest = {
        message: 'Hello',
        user_id: 1,
      }

      const mockResponse = {
        data: {
          message: 'Hi there!',
          conversation_id: 1,
        },
      }

      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse)

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')
        const result = await freshApi.sendMessage(request)

        expect(result).toHaveProperty('message')
        expect(result).toHaveProperty('conversation_id')
      })
    })

    it('handles chat API errors', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        response: {
          status: 500,
          data: { detail: 'Internal server error' },
        },
      })

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')

        await expect(
          freshApi.sendMessage({
            message: 'Test',
            trip_id: 1,
            user_id: 1,
          })
        ).rejects.toMatchObject({
          response: expect.objectContaining({
            status: 500,
          }),
        })
      })
    })
  })

  describe('Trips API Integration', () => {
    it('creates a trip successfully', async () => {
      const tripData = {
        user_id: 1,
        destination: 'Paris, France',
        start_date: '2024-06-01',
        end_date: '2024-06-10',
        budget: 5000,
      }

      const mockResponse = {
        data: {
          id: 1,
          ...tripData,
          status: 'gathering',
          itinerary: null,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
        },
      }

      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse)

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')
        const result = await freshApi.createTrip(tripData)

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/trips/',
          tripData
        )
        expect(result.id).toBe(1)
        expect(result.destination).toBe('Paris, France')
        expect(result.status).toBe('gathering')
      })
    })

    it('retrieves a trip by ID', async () => {
      const mockResponse = {
        data: {
          id: 123,
          user_id: 1,
          destination: 'Tokyo, Japan',
          start_date: '2024-09-01',
          end_date: '2024-09-14',
          budget: 8000,
          status: 'finalized',
          itinerary: { day1: 'Arrive in Tokyo' },
          created_at: '2024-01-10T10:00:00Z',
          updated_at: '2024-01-20T15:00:00Z',
        },
      }

      mockAxiosInstance.get.mockResolvedValueOnce(mockResponse)

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')
        const result = await freshApi.getTrip(123)

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/trips/123')
        expect(result.id).toBe(123)
        expect(result.destination).toBe('Tokyo, Japan')
        expect(result.status).toBe('finalized')
      })
    })

    it('handles trip not found error', async () => {
      mockAxiosInstance.get.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { detail: 'Trip not found' },
        },
      })

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')

        await expect(freshApi.getTrip(99999)).rejects.toMatchObject({
          response: expect.objectContaining({
            status: 404,
          }),
        })
      })
    })

    it('retrieves all trips', async () => {
      const mockResponse = {
        data: [
          {
            id: 1,
            user_id: 1,
            destination: 'Paris',
            start_date: '2024-06-01',
            end_date: '2024-06-10',
            budget: 5000,
            status: 'gathering',
            itinerary: null,
            created_at: '2024-01-15T10:00:00Z',
            updated_at: '2024-01-15T10:00:00Z',
          },
          {
            id: 2,
            user_id: 1,
            destination: 'Barcelona',
            start_date: '2024-07-01',
            end_date: '2024-07-07',
            budget: 3000,
            status: 'finalized',
            itinerary: null,
            created_at: '2024-01-16T10:00:00Z',
            updated_at: '2024-01-16T10:00:00Z',
          },
        ],
      }

      mockAxiosInstance.get.mockResolvedValueOnce(mockResponse)

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')
        const result = await freshApi.getAllTrips()

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/trips/')
        expect(Array.isArray(result)).toBe(true)
        expect(result).toHaveLength(2)
        expect(result[0].destination).toBe('Paris')
        expect(result[1].destination).toBe('Barcelona')
      })
    })

    it('handles empty trips list', async () => {
      mockAxiosInstance.get.mockResolvedValueOnce({ data: [] })

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')
        const result = await freshApi.getAllTrips()

        expect(Array.isArray(result)).toBe(true)
        expect(result).toHaveLength(0)
      })
    })
  })

  // Note: Request configuration tests are skipped because axios.create
  // is called at module load time, making it difficult to test in isolation

  describe('Error Handling', () => {
    it('propagates network errors', async () => {
      const networkError = new Error('Network timeout')
      mockAxiosInstance.get.mockRejectedValueOnce(networkError)

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')

        await expect(freshApi.health()).rejects.toThrow('Network timeout')
      })
    })

    it('handles server errors with response data', async () => {
      const serverError = {
        response: {
          status: 500,
          data: { detail: 'Database connection failed' },
        },
      }
      mockAxiosInstance.post.mockRejectedValueOnce(serverError)

      jest.isolateModules(async () => {
        const { api: freshApi } = require('@/lib/api')

        await expect(
          freshApi.sendMessage({ message: 'Test', user_id: 1 })
        ).rejects.toMatchObject({
          response: expect.objectContaining({
            status: 500,
            data: expect.objectContaining({
              detail: 'Database connection failed',
            }),
          }),
        })
      })
    })
  })
})
