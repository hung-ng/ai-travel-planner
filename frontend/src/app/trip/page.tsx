'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Trip } from '@/types';
import ExportShare from '@/components/ShareExport';
import BudgetBreakdown from '@/components/BudgetBreakdown';
import ItineraryTimeline from '@/components/ItineraryTimeline';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function TripDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.id as string;
  
  const [trip, setTrip] = useState<Trip | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'chat' | 'itinerary'>('overview');

  useEffect(() => {
    loadTripDetails();
  }, [tripId]);

  const loadTripDetails = async () => {
    try {
      // const tripData = await api.getTrip(tripId);
      // const chatHistory = await api.getTripMessages(tripId);
      
      // Mock
      const mockTrip: Trip = {
        id: parseInt(tripId),
        user_id: 1,
        destination: 'Paris, France',
        start_date: '2024-06-15',
        end_date: '2024-06-22',
        budget: 3500,
        status: 'planning',
        itinerary: {
          days: 7,
          activities: [
            { day: 1, title: 'Arrive in Paris', description: 'Check into hotel, evening walk along Seine', time: '14:00' },
            { day: 1, title: 'Dinner at Le Comptoir', description: 'Traditional French cuisine', time: '19:00' },
            { day: 2, title: 'Visit Eiffel Tower', description: 'Morning visit to avoid crowds', time: '09:00' },
            { day: 2, title: 'Louvre Museum', description: 'Afternoon at the Louvre', time: '14:00' },
            { day: 3, title: 'Montmartre Walking Tour', description: 'Explore Sacré-Cœur and artists square', time: '10:00' },
          ]
        },
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-20T15:30:00Z',
      };

      const mockMessages: Message[] = [
        {
          role: 'user',
          content: 'I want to plan a trip to Paris for 7 days with a budget of $3500',
          timestamp: '2024-01-15T10:00:00Z'
        },
        {
          role: 'assistant',
          content: 'Great choice! Paris is wonderful. Let me create a 7-day itinerary for you within your $3500 budget. I\'ll include visits to major attractions, local dining experiences, and some hidden gems.',
          timestamp: '2024-01-15T10:00:30Z'
        },
        {
          role: 'user',
          content: 'Can you include some good restaurants?',
          timestamp: '2024-01-15T10:05:00Z'
        },
        {
          role: 'assistant',
          content: 'Absolutely! I\'ve added several authentic French restaurants including Le Comptoir for traditional cuisine, L\'As du Fallafel in Le Marais, and a cafe near the Eiffel Tower for breakfast with a view.',
          timestamp: '2024-01-15T10:05:30Z'
        },
      ];

      setTrip(mockTrip);
      setMessages(mockMessages);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load trip:', err);
      setError('Failed to load trip details');
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
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

  const statusColors = {
    planning: 'bg-blue-100 text-blue-700 border-blue-200',
    booked: 'bg-green-100 text-green-700 border-green-200',
    completed: 'bg-gray-100 text-gray-700 border-gray-200',
    cancelled: 'bg-red-100 text-red-700 border-red-200',
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading trip details...</p>
        </div>
      </div>
    );
  }

  if (error || !trip) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 max-w-md text-center">
          <div className="text-5xl mb-4">😮</div>
          <h2 className="text-xl font-semibold text-red-800 mb-2">Trip Not Found</h2>
          <p className="text-red-600 mb-4">{error || 'This trip does not exist'}</p>
          <Link
            href="/dashboard"
            className="inline-block bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link href="/dashboard" className="text-blue-500 hover:text-blue-600 text-sm mb-2 inline-block">
            ← Back to My Trips
          </Link>
          
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{trip.destination}</h1>
              <div className="flex items-center gap-3 text-gray-600">
                <span>📅 {formatDate(trip.start_date)} - {formatDate(trip.end_date)}</span>
                <span>•</span>
                <span>⏱️ {getDuration(trip.start_date, trip.end_date)} days</span>
                {trip.budget && (
                  <>
                    <span>•</span>
                    <span>💰 ${trip.budget.toLocaleString()}</span>
                  </>
                )}
              </div>
            </div>
            
            <div className="flex gap-2">
              <span className={`px-4 py-2 rounded-full text-sm font-semibold border ${statusColors[trip.status as keyof typeof statusColors]}`}>
                {trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}
              </span>
              <ExportShare 
                trip={trip}
                messages={messages.map(m => ({
                  ...m,
                  timestamp: new Date(m.timestamp)
                }))}
              />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-t-xl shadow-md border border-gray-200 border-b-0">
          <div className="flex gap-4 p-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'overview'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              📋 Overview
            </button>
            <button
              onClick={() => setActiveTab('itinerary')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'itinerary'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              📍 Itinerary
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'chat'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              💬 Chat History
            </button>
          </div>
        </div>

        {/*  Content */}
        <div className="bg-white rounded-b-xl shadow-md border border-gray-200 p-6">
          {/* Overview  */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Trip Information</h3>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Destination</span>
                      <span className="font-medium text-gray-900">{trip.destination}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Duration</span>
                      <span className="font-medium text-gray-900">{getDuration(trip.start_date, trip.end_date)} days</span>
                    </div>
                    
                    {trip.budget && (
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-600">Budget</span>
                        <span className="font-medium text-gray-900">${trip.budget.toLocaleString()}</span>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Status</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${statusColors[trip.status as keyof typeof statusColors]}`}>
                        {trip.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
                  
                  <div className="space-y-2">
                    <Link
                      href={`/chat?tripId=${trip.id}`}
                      className="block w-full bg-blue-500 text-white px-4 py-3 rounded-lg hover:bg-blue-600 transition-colors text-center font-medium"
                    >
                      ✏️ Continue Planning
                    </Link>
                    
                    <button className="block w-full bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors text-center font-medium">
                      📅 Add to Calendar
                    </button>
                    
                    <button className="block w-full bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors text-center font-medium">
                      ✉️ Email Itinerary
                    </button>
                  </div>
                </div>
              </div>

              {/* Budget Breakdown */}
              {trip.budget && (
                <div className="pt-6 border-t border-gray-200">
                  <BudgetBreakdown 
                    totalBudget={trip.budget}
                    spent={[
                      { category: 'accommodation', amount: 1200 },
                      { category: 'food', amount: 500 },
                      { category: 'activities', amount: 800 },
                      { category: 'transport', amount: 400 },
                    ]}
                    currency="USD"
                  />
                </div>
              )}

              {trip.itinerary && trip.itinerary.activities && (
                <div className="pt-6 border-t border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Trip Highlights</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    {trip.itinerary.activities.slice(0, 4).map((activity: any, idx: number) => (
                      <div key={idx} className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                        <div className="flex items-start gap-3">
                          <span className="text-2xl">📍</span>
                          <div>
                            <h4 className="font-semibold text-gray-900">{activity.title}</h4>
                            <p className="text-sm text-gray-600">{activity.description}</p>
                            <p className="text-xs text-gray-500 mt-1">Day {activity.day} • {activity.time}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Itinerary */}
          {activeTab === 'itinerary' && (
            <div className="space-y-6">
              {trip.itinerary && trip.itinerary.activities ? (
                <ItineraryTimeline 
                  activities={trip.itinerary.activities.map((activity: any, index: number) => ({
                    id: `activity-${index}`,
                    day: activity.day,
                    time: activity.time,
                    title: activity.title,
                    description: activity.description,
                    location: activity.location,
                    cost: activity.cost,
                    category: activity.category || 'activity',
                    duration: activity.duration,
                  }))}
                  startDate={trip.start_date}
                  currency="USD"
                />
              ) : (
                <div className="text-center py-12">
                  <div className="text-5xl mb-4">📝</div>
                  <p className="text-gray-600">No detailed itinerary yet</p>
                  <Link
                    href={`/chat?tripId=${trip.id}`}
                    className="inline-block mt-4 bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
                  >
                    Continue Planning
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Chat History */}
          {activeTab === 'chat' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Conversation History</h3>
              
              {messages.length > 0 ? (
                <div className="space-y-4">
                  {messages.map((msg, idx) => {
                    const isUser = msg.role === 'user';
                    return (
                      <div key={idx} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                          isUser 
                            ? 'bg-blue-500 text-white rounded-br-none'
                            : 'bg-gray-200 text-gray-900 rounded-bl-none'
                        }`}>
                          <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                          <p className={`text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
                            {new Date(msg.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-5xl mb-4">💬</div>
                  <p className="text-gray-600">No conversation history yet</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}