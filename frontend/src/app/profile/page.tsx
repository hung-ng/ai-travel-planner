'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Trip } from '@/types';

interface UserProfile {
  id: number;
  name: string;
  email: string;
  avatar?: string;
  preferences: {
    travelStyle: string[];
    budgetRange: string;
    interests: string[];
    dietaryRestrictions: string[];
  };
  stats: {
    totalTrips: number;
    countriesVisited: number;
    totalSpent: number;
  };
}

// Mock trips data - same as dashboard
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
  {
    id: 4,
    user_id: 1,
    destination: 'Ho Chi Minh City, Vietnam',
    start_date: '2023-08-12',
    end_date: '2023-08-20',
    budget: 1800,
    status: 'completed',
    itinerary: { days: 8, activities: 24 },
    created_at: '2023-06-20T10:00:00Z',
    updated_at: '2023-08-21T09:30:00Z',
  },
];

// Calculate stats from trips
const calculateStats = (trips: Trip[]) => {
  const totalTrips = trips.length;
  
  // Extract unique countries from destinations
  const countries = trips.map(trip => {
    // Extract country from "City, Country" format
    const parts = trip.destination.split(',');
    return parts[parts.length - 1].trim();
  });
  const countriesVisited = new Set(countries).size;
  
  // Sum all budgets (handle null values)
  const totalSpent = trips.reduce((sum, trip) => sum + (trip.budget || 0), 0);
  
  return {
    totalTrips,
    countriesVisited,
    totalSpent,
  };
};

//  user data need to be replace with real auth later
const mockUser: UserProfile = {
  id: 1,
  name: 'Jane Doe',
  email: 'jane@example.com',
  avatar: '👤',
  preferences: {
    travelStyle: ['Adventure', 'Cultural', 'Relaxation'],
    budgetRange: '$2000-$5000',
    interests: ['Photography', 'Food & Wine', 'History', 'Nature'],
    dietaryRestrictions: ['Vegetarian'],
  },
  stats: calculateStats(mockTrips), // Calculate from trips data
};

export default function UserProfile() {
  const [user, setUser] = useState<UserProfile>(mockUser);
  const [isEditing, setIsEditing] = useState(false);
  const [editedUser, setEditedUser] = useState<UserProfile>(user);

  const travelStyleOptions = ['Adventure', 'Luxury', 'Budget', 'Cultural', 'Relaxation', 'Family', 'Solo', 'Business'];
  const interestOptions = ['Food & Wine', 'Photography', 'History', 'Nature', 'Shopping', 'Nightlife', 'Art & Museums', 'Sports', 'Beach', 'Mountains'];
  const dietaryOptions = ['None', 'Vegetarian', 'Vegan', 'Gluten-Free', 'Halal', 'Kosher', 'Lactose-Free'];

  const handleSave = () => {
    setUser(editedUser);
    setIsEditing(false);
    // save to API later
    console.log('Saving user profile:', editedUser);
  };

  const handleCancel = () => {
    setEditedUser(user);
    setIsEditing(false);
  };

  const togglePreference = (category: keyof UserProfile['preferences'], value: string) => {
    const currentValues = editedUser.preferences[category] as string[];
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value];
    
    setEditedUser({
      ...editedUser,
      preferences: {
        ...editedUser.preferences,
        [category]: newValues,
      },
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="text-blue-500 hover:text-blue-600 text-base mb-4 inline-block font-bold">
            ← Back to Home
          </Link>
          <div className="flex items-center justify-between">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">My Profile</h1>
            {isEditing ? (
              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  className="bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors font-medium text-lg"
                >
                  Save
                </button>
                <button
                  onClick={handleCancel}
                  className="bg-gray-200 text-gray-700 px-8 py-3 rounded-lg hover:bg-gray-300 transition-colors text-lg"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors font-medium text-lg"
              >
                Edit Profile
              </button>
            )}
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Profile Card */}
          <div className="md:col-span-1">
            <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
              {/* Avatar */}
              <div className="text-center mb-8">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-4xl mx-auto mb-4">
                  {user.avatar}
                </div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedUser.name}
                    onChange={(e) => setEditedUser({ ...editedUser, name: e.target.value })}
                    className="text-xl font-bold text-gray-900 text-center w-full border-b-2 border-blue-500 focus:outline-none"
                  />
                ) : (
                  <h2 className="text-2xl font-bold text-gray-900">{user.name}</h2>
                )}
                {isEditing ? (
                  <input
                    type="email"
                    value={editedUser.email}
                    onChange={(e) => setEditedUser({ ...editedUser, email: e.target.value })}
                    className="text-base text-gray-600 text-center w-full border-b border-gray-300 focus:outline-none mt-1"
                  />
                ) : (
                  <p className="text-base text-gray-600">{user.email}</p>
                )}
              </div>

              {/* Stats */}
              <div className="space-y-4 pt-8 border-t border-gray-200 mb-8">
                <div className="flex items-center justify-between">
                  <span className="text-base text-gray-600">Total Trips</span>
                  <span className="font-semibold text-base text-gray-900">{user.stats.totalTrips}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-base text-gray-600">Countries Visited</span>
                  <span className="font-semibold text-base text-gray-900">{user.stats.countriesVisited}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-base text-gray-600">Total Spent</span>
                  <span className="font-semibold text-base text-gray-900">${user.stats.totalSpent.toLocaleString()}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-6">
                <Link
                  href="/dashboard"
                  className="block w-full text-center bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors text-lg"
                >
                  View My Trips
                </Link>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="md:col-span-2 space-y-6">
            {/* Travel style */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Travel Style</h3>
              <div className="flex flex-wrap gap-2">
                {travelStyleOptions.map((style) => {
                  const isSelected = (isEditing ? editedUser : user).preferences.travelStyle.includes(style);
                  return (
                    <button
                      key={style}
                      onClick={() => isEditing && togglePreference('travelStyle', style)}
                      disabled={!isEditing}
                      className={`px-4 py-2 rounded-full text-base font-medium transition-colors ${
                        isSelected
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      } ${!isEditing && 'cursor-default'}`}
                    >
                      {style}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Interest */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Interests</h3>
              <div className="flex flex-wrap gap-2">
                {interestOptions.map((interest) => {
                  const isSelected = (isEditing ? editedUser : user).preferences.interests.includes(interest);
                  return (
                    <button
                      key={interest}
                      onClick={() => isEditing && togglePreference('interests', interest)}
                      disabled={!isEditing}
                      className={`px-4 py-2 rounded-full text-base font-medium transition-colors ${
                        isSelected
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      } ${!isEditing && 'cursor-default'}`}
                    >
                      {interest}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Budget */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Budget Range</h3>
              {isEditing ? (
                <select
                  value={editedUser.preferences.budgetRange}
                  onChange={(e) => setEditedUser({
                    ...editedUser,
                    preferences: { ...editedUser.preferences, budgetRange: e.target.value }
                  })}
                  className="w-full px-4 py-2 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option>Under $1000</option>
                  <option>$1000-$2000</option>
                  <option>$2000-$5000</option>
                  <option>$5000-$10000</option>
                  <option>$10000+</option>
                </select>
              ) : (
                <p className="text-gray-700 font-medium text-lg">{user.preferences.budgetRange}</p>
              )}
            </div>
          </div>
        </div>

        {/* AI Memory - Full Width */}
        <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🤖</span>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">AI Memory</h3>
              <p className="text-base text-gray-700">
                Your travel AI assistant remembers your preferences and past trips. 
                The more you interact, the better recommendations you'll receive!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}