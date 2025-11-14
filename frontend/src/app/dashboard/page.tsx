'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Trip } from '@/types';
import { api } from '@/lib/api';

// You'll need to add this to your @/lib/api.ts:
/*
export const api = {
  // ... your existing functions
  
  async getTrips(userId: number): Promise<Trip[]> {
    const response = await fetch(`${API_BASE_URL}/trips?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to fetch trips');
    return response.json();
  },
};
*/

const statusConfig = {
  planning: { 
    color: 'bg-blue-100 text-blue-700 border-blue-200',
    icon: '📝',
    label: 'Planning'
  },
  booked: { 
    color: 'bg-green-100 text-green-700 border-green-200',
    icon: '✅',
    label: 'Booked'
  },
  completed: { 
    color: 'bg-gray-100 text-gray-700 border-gray-200',
    icon: '🎉',
    label: 'Completed'
  },
  cancelled: { 
    color: 'bg-red-100 text-red-700 border-red-200',
    icon: '❌',
    label: 'Cancelled'
  },
} as const;

export default function TripDashboard() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'budget' | 'destination'>('date');

  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      // Mock data - Uncomment this if backend is not running
      /*
      const mockTrips: Trip[] = [
        {
          id: 1,
          user_id: 1,
          destination: 'Paris, France',
          start_date: '2024-06-15',
          end_date: '2024-06-22',
          budget: 3500,
          status: 'planning',
          itinerary: { days: 7, activities: 21 },
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-20T15:30:00Z',
        },
        {
          id: 2,
          user_id: 1,
          destination: 'Tokyo, Japan',
          start_date: '2024-03-10',
          end_date: '2024-03-20',
          budget: 4200,
          status: 'booked',
          itinerary: { days: 10, activities: 35 },
          created_at: '2023-12-01T09:00:00Z',
          updated_at: '2024-01-05T11:20:00Z',
        },
        {
          id: 3,
          user_id: 1,
          destination: 'Bali, Indonesia',
          start_date: '2023-11-05',
          end_date: '2023-11-15',
          budget: 2800,
          status: 'completed',
          itinerary: { days: 10, activities: 28 },
          created_at: '2023-09-10T14:00:00Z',
          updated_at: '2023-11-16T08:45:00Z',
        },
      ];
      setTrips(mockTrips);
      */

      // real
      const data = await api.getAllTrips(); 
      setTrips(data);

      setLoading(false);
    } catch (err) {
      console.error('Failed to load trips:', err);
      setError('Failed to load trips. Please try again.');
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getDuration = (start: string, end: string) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  const filteredTrips = trips
    .filter(trip => 
      (filterStatus === 'all' || trip.status === filterStatus) &&
      (searchQuery === '' || trip.destination.toLowerCase().includes(searchQuery.toLowerCase()))
    )
    .sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.start_date).getTime() - new Date(a.start_date).getTime();
      } else if (sortBy === 'budget') {
        return (b.budget || 0) - (a.budget || 0);
      } else {
        return a.destination.localeCompare(b.destination);
      }
    });

  const stats = {
    total: trips.length,
    planning: trips.filter(t => t.status === 'planning').length,
    booked: trips.filter(t => t.status === 'booked').length,
    completed: trips.filter(t => t.status === 'completed').length,
    totalBudget: trips.reduce((sum, t) => sum + (t.budget || 0), 0),
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your trips...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 max-w-md text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Trips</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadTrips}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">My Trips</h1>
              <p className="text-gray-600 mt-1">Manage and view all your travel plans</p>
            </div>
            <Link 
              href="/chat"
              className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              <span>+</span> New Trip
            </Link>
          </div>

          <Link href="/" className="text-blue-500 hover:text-blue-600 text-sm">
            ← Back to Home
          </Link>
        </div>

        {/* Stats  */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Trips</p>
                <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="text-4xl">🌍</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Planning</p>
                <p className="text-3xl font-bold text-blue-600">{stats.planning}</p>
              </div>
              <div className="text-4xl">📝</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Booked</p>
                <p className="text-3xl font-bold text-green-600">{stats.booked}</p>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-3xl font-bold text-purple-600">{stats.completed}</p>
              </div>
              <div className="text-4xl">🎉</div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-xl shadow-md border border-gray-200 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search destinations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Status Filter */}
            <div className="flex gap-2 flex-wrap">
              {['all', 'planning', 'booked', 'completed'].map(status => (
                <button
                  key={status}
                  onClick={() => setFilterStatus(status)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    filterStatus === status
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {status === 'all' ? 'All' : statusConfig[status as keyof typeof statusConfig].label}
                </button>
              ))}
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="date">Sort by Date</option>
              <option value="budget">Sort by Budget</option>
              <option value="destination">Sort by Name</option>
            </select>
          </div>
        </div>

        {/* Trips Grid */}
        {filteredTrips.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md border border-gray-200 p-12 text-center">
            <div className="text-6xl mb-4">🗺️</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No trips found</h3>
            <p className="text-gray-600 mb-6">
              {searchQuery ? 'Try adjusting your search' : 'Start planning your next adventure!'}
            </p>
            <Link 
              href="/chat"
              className="inline-block bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
            >
              Create Your First Trip
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTrips.map(trip => {
              const status = statusConfig[trip.status as keyof typeof statusConfig];
              const duration = getDuration(trip.start_date, trip.end_date);

              return (
                <div 
                  key={trip.id}
                  className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden hover:shadow-xl transition-shadow cursor-pointer group"
                >
                  {/* Card Header with gradient */}
                  <div className="h-32 bg-gradient-to-br from-blue-400 via-purple-400 to-pink-400 relative">
                    <div className="absolute top-3 right-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${status.color}`}>
                        {status.icon} {status.label}
                      </span>
                    </div>
                    <div className="absolute bottom-3 left-4 text-white">
                      <h3 className="text-2xl font-bold drop-shadow-lg">{trip.destination}</h3>
                    </div>
                  </div>

                  {/* Card Content */}
                  <div className="p-5">
                    <div className="space-y-3">
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="mr-2">📅</span>
                        <span>{formatDate(trip.start_date)} - {formatDate(trip.end_date)}</span>
                      </div>

                      <div className="flex items-center text-sm text-gray-600">
                        <span className="mr-2">⏱️</span>
                        <span>{duration} days</span>
                      </div>

                      {trip.budget && (
                        <div className="flex items-center text-sm text-gray-600">
                          <span className="mr-2">💵</span>
                          <span>${trip.budget.toLocaleString()}</span>
                        </div>
                      )}

                      {trip.itinerary && (
                        <div className="flex items-center text-sm text-gray-600">
                          <span className="mr-2">📍</span>
                          <span>{trip.itinerary.activities} activities planned</span>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="mt-5 pt-4 border-t border-gray-200">
                      <Link
                        href={`/chat?tripId=${trip.id}`}
                        className="block w-full bg-blue-500 text-white px-4 py-2 rounded-lg text-center text-sm font-medium hover:bg-blue-600 transition-colors"
                      >
                        Continue Planning
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}