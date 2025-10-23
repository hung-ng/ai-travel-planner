'use client';

import { useState, useEffect } from 'react';
import ChatInterface from '@/components/ChatInterface';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function ChatPage() {
  const [tripId, setTripId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    initializeTrip();
  }, []);

  const initializeTrip = async () => {
    try {
      const trip = await api.createTrip({
        user_id: 1,
        destination: 'Planning',
        start_date: new Date().toISOString(),
        end_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
        budget: null,
      });

      setTripId(trip.id);
      setLoading(false);
    } catch (err) {
      console.error('Failed to create trip:', err);
      setError('Failed to connect. Make sure server is running.');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Starting chat...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 max-w-md text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-red-800 mb-2">Connection Error</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <div className="space-y-2 text-sm text-gray-600 text-left bg-white p-4 rounded">
            <p className="font-semibold">To fix this:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Make sure Docker is running</li>
              <li>Run: <code className="bg-gray-100 px-1">docker-compose -f docker-compose.backend.yml up</code></li>
              <li>Verify backend is at: <code className="bg-gray-100 px-1">http://localhost:8000</code></li>
            </ol>
          </div>

          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
          >
            Try Again!
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-4xl mx-auto">

        <div className="mb-6 flex items-center justify-between">
          <div>
            <Link
              href="/"
              className="text-blue-500 hover:text-blue-600 text-sm mb-2 inline-block"
            >
              Back to Home
            </Link>
            <h1 className="text-3xl font-bold">Plan Your Trip</h1>
            <p className="text-gray-600">Trip ID: {tripId}</p>
          </div>
        </div>

        {tripId && <ChatInterface tripId={tripId} userId={1} />}

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Tips for better results:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Tell me your destination and travel dates</li>
            <li>• Share your budget and interests</li>
            <li>• What is your preferred travel pace (relaxed, moderate, fast-paced)?</li>
            <li>• Any specific recommendations (restaurants, museums, hidden gems)?</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
