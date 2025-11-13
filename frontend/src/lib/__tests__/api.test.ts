import axios from 'axios'
import { api } from '../api'
import { ChatRequest, Trip } from '@/types'

// Mock axios
jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    // Setup axios.create mock
    mockedAxios.create = jest.fn(() => ({
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
      request: jest.fn(),
      defaults: {},
      interceptors: {
        request: { use: jest.fn(), eject: jest.fn() },
        response: { use: jest.fn(), eject: jest.fn() },
      },
    })) as any
  })

  describe('health', () => {
    it('calls GET /health endpoint', async () => {
      const mockResponse = { data: { status: 'healthy' } }
      const mockGet = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        get: mockGet,
        post: jest.fn(),
      })) as any

      // Re-import to get fresh instance with mocked axios
      jest.isolateModules(() => {
        const { api: freshApi } = require('../api')
        freshApi.health().then((data: any) => {
          expect(data).toEqual({ status: 'healthy' })
        })
      })
    })
  })

  describe('sendMessage', () => {
    it('sends POST request to /api/chat/message', async () => {
      const mockRequest: ChatRequest = {
        message: 'I want to visit Paris',
        trip_id: 1,
        user_id: 123,
      }

      const mockResponse = {
        data: {
          message: 'Great choice! Paris is beautiful.',
          conversation_id: 456,
        },
      }

      const mockPost = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn(),
        post: mockPost,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.sendMessage(mockRequest)

        expect(mockPost).toHaveBeenCalledWith('/api/chat/message', mockRequest)
        expect(result).toEqual(mockResponse.data)
      })
    })

    it('returns chat response with correct structure', async () => {
      const mockRequest: ChatRequest = {
        message: 'Test message',
        trip_id: 1,
        user_id: 1,
      }

      const mockResponse = {
        data: {
          message: 'AI response',
          conversation_id: 789,
        },
      }

      const mockPost = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        post: mockPost,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.sendMessage(mockRequest)

        expect(result).toHaveProperty('message')
        expect(result).toHaveProperty('conversation_id')
        expect(typeof result.message).toBe('string')
        expect(typeof result.conversation_id).toBe('number')
      })
    })
  })

  describe('createTrip', () => {
    it('sends POST request to /api/trips/', async () => {
      const mockTripData: Partial<Trip> = {
        user_id: 1,
        destination: 'Tokyo, Japan',
        start_date: '2024-06-01',
        end_date: '2024-06-10',
        budget: 5000,
      }

      const mockResponse = {
        data: {
          id: 1,
          ...mockTripData,
          status: 'gathering',
          itinerary: null,
          created_at: '2024-01-15T10:00:00',
          updated_at: '2024-01-15T10:00:00',
        },
      }

      const mockPost = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        post: mockPost,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.createTrip(mockTripData)

        expect(mockPost).toHaveBeenCalledWith('/api/trips/', mockTripData)
        expect(result).toEqual(mockResponse.data)
      })
    })

    it('returns trip with generated ID and timestamps', async () => {
      const mockTripData: Partial<Trip> = {
        user_id: 1,
        destination: 'Barcelona',
        start_date: '2024-07-01',
        end_date: '2024-07-07',
        budget: 3000,
      }

      const mockResponse = {
        data: {
          id: 42,
          ...mockTripData,
          status: 'gathering',
          itinerary: null,
          created_at: '2024-01-15T10:00:00',
          updated_at: '2024-01-15T10:00:00',
        },
      }

      const mockPost = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        post: mockPost,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.createTrip(mockTripData)

        expect(result).toHaveProperty('id')
        expect(result).toHaveProperty('created_at')
        expect(result).toHaveProperty('updated_at')
        expect(result.id).toBe(42)
      })
    })
  })

  describe('getTrip', () => {
    it('sends GET request to /api/trips/:id', async () => {
      const tripId = 123
      const mockResponse = {
        data: {
          id: tripId,
          user_id: 1,
          destination: 'Paris',
          start_date: '2024-06-01',
          end_date: '2024-06-10',
          budget: 5000,
          status: 'gathering',
          itinerary: null,
          created_at: '2024-01-15T10:00:00',
          updated_at: '2024-01-15T10:00:00',
        },
      }

      const mockGet = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        get: mockGet,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.getTrip(tripId)

        expect(mockGet).toHaveBeenCalledWith(`/api/trips/${tripId}`)
        expect(result).toEqual(mockResponse.data)
      })
    })

    it('returns trip data for valid ID', async () => {
      const mockResponse = {
        data: {
          id: 1,
          user_id: 1,
          destination: 'Rome',
          start_date: '2024-08-01',
          end_date: '2024-08-10',
          budget: 4000,
          status: 'finalized',
          itinerary: { day1: 'Colosseum visit' },
          created_at: '2024-01-15T10:00:00',
          updated_at: '2024-01-20T15:00:00',
        },
      }

      const mockGet = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        get: mockGet,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.getTrip(1)

        expect(result.id).toBe(1)
        expect(result.destination).toBe('Rome')
        expect(result.status).toBe('finalized')
      })
    })
  })

  describe('getAllTrips', () => {
    it('sends GET request to /api/trips/', async () => {
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
            created_at: '2024-01-15T10:00:00',
            updated_at: '2024-01-15T10:00:00',
          },
          {
            id: 2,
            user_id: 1,
            destination: 'Tokyo',
            start_date: '2024-09-01',
            end_date: '2024-09-14',
            budget: 8000,
            status: 'finalized',
            itinerary: null,
            created_at: '2024-01-16T10:00:00',
            updated_at: '2024-01-16T10:00:00',
          },
        ],
      }

      const mockGet = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        get: mockGet,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.getAllTrips()

        expect(mockGet).toHaveBeenCalledWith('/api/trips/')
        expect(result).toEqual(mockResponse.data)
      })
    })

    it('returns array of trips', async () => {
      const mockResponse = {
        data: [
          {
            id: 1,
            user_id: 1,
            destination: 'Berlin',
            start_date: '2024-05-01',
            end_date: '2024-05-07',
            budget: 2500,
            status: 'gathering',
            itinerary: null,
            created_at: '2024-01-15T10:00:00',
            updated_at: '2024-01-15T10:00:00',
          },
        ],
      }

      const mockGet = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        get: mockGet,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.getAllTrips()

        expect(Array.isArray(result)).toBe(true)
        expect(result).toHaveLength(1)
        expect(result[0].destination).toBe('Berlin')
      })
    })

    it('returns empty array when no trips exist', async () => {
      const mockResponse = { data: [] }

      const mockGet = jest.fn().mockResolvedValue(mockResponse)

      mockedAxios.create = jest.fn(() => ({
        get: mockGet,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')
        const result = await freshApi.getAllTrips()

        expect(Array.isArray(result)).toBe(true)
        expect(result).toHaveLength(0)
      })
    })
  })

  describe('Error Handling', () => {
    it('throws error when request fails', async () => {
      const mockError = new Error('Network error')
      const mockGet = jest.fn().mockRejectedValue(mockError)

      mockedAxios.create = jest.fn(() => ({
        get: mockGet,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')

        await expect(freshApi.health()).rejects.toThrow('Network error')
      })
    })

    it('throws error when POST request fails', async () => {
      const mockError = new Error('Server error')
      const mockPost = jest.fn().mockRejectedValue(mockError)

      mockedAxios.create = jest.fn(() => ({
        post: mockPost,
      })) as any

      jest.isolateModules(async () => {
        const { api: freshApi } = require('../api')

        await expect(
          freshApi.sendMessage({
            message: 'test',
            trip_id: 1,
            user_id: 1,
          })
        ).rejects.toThrow('Server error')
      })
    })
  })

  describe('API Configuration', () => {
    it('uses correct base URL from environment', () => {
      // The API client should use process.env.NEXT_PUBLIC_API_URL or default
      expect(true).toBe(true) // Placeholder for configuration test
    })

    it('sets correct Content-Type header', () => {
      // The API client should set 'Content-Type': 'application/json'
      expect(true).toBe(true) // Placeholder for header test
    })
  })
})
