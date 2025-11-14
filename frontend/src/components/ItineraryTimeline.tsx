'use client';

import { useState } from 'react';

interface Activity {
  id: string;
  day: number;
  time: string;
  title: string;
  description: string;
  location?: string;
  cost?: number;
  category: 'accommodation' | 'food' | 'activity' | 'transport';
  duration?: string;
}

interface ItineraryTimelineProps {
  activities: Activity[];
  startDate: string;
  currency?: string;
}

export default function ItineraryTimeline({ 
  activities, 
  startDate,
  currency = 'USD'
}: ItineraryTimelineProps) {
  const [selectedDay, setSelectedDay] = useState<number | null>(null);

  // group  by day
  const groupedActivities = activities.reduce((acc, activity) => {
    if (!acc[activity.day]) {
      acc[activity.day] = [];
    }
    acc[activity.day].push(activity);
    return acc;
  }, {} as Record<number, Activity[]>);

  const sortedDays = Object.keys(groupedActivities)
    .map(Number)
    .sort((a, b) => a - b);

  // calc date for each day
  const getDateForDay = (day: number) => {
    const date = new Date(startDate);
    date.setDate(date.getDate() + (day - 1));
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const categoryConfig = {
    accommodation: { icon: '🏨', color: 'bg-purple-100 text-purple-700 border-purple-300' },
    food: { icon: '🍽️', color: 'bg-orange-100 text-orange-700 border-orange-300' },
    activity: { icon: '🎯', color: 'bg-blue-100 text-blue-700 border-blue-300' },
    transport: { icon: '🚗', color: 'bg-green-100 text-green-700 border-green-300' },
  };

  // calc total cost per day
  const getDayCost = (day: number) => {
    return groupedActivities[day]
      .reduce((sum, activity) => sum + (activity.cost || 0), 0);
  };

  // total trip cost
  const totalCost = activities.reduce((sum, activity) => sum + (activity.cost || 0), 0);

  return (
    <div className="space-y-6">
      {/* Summary  */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Trip Overview</h3>
            <p className="text-sm text-gray-600">
              {sortedDays.length} days • {activities.length} activities
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Estimated Total</p>
            <p className="text-2xl font-bold text-blue-600">
              ${totalCost.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Day Selector */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => setSelectedDay(null)}
          className={`px-4 py-2 rounded-full font-medium whitespace-nowrap transition-colors ${
            selectedDay === null
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Days
        </button>
        {sortedDays.map(day => (
          <button
            key={day}
            onClick={() => setSelectedDay(day)}
            className={`px-4 py-2 rounded-full font-medium whitespace-nowrap transition-colors ${
              selectedDay === day
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Day {day}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="space-y-6">
        {sortedDays
          .filter(day => selectedDay === null || selectedDay === day)
          .map(day => (
            <div key={day} className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              {/* Day */}
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-xl font-bold">Day {day}</h4>
                    <p className="text-sm text-blue-100">{getDateForDay(day)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-blue-100">Daily Cost</p>
                    <p className="text-lg font-bold">${getDayCost(day).toLocaleString()}</p>
                  </div>
                </div>
              </div>

              {/* Activities */}
              <div className="p-4 space-y-4">
                {groupedActivities[day]
                  .sort((a, b) => a.time.localeCompare(b.time))
                  .map((activity, idx) => {
                    const config = categoryConfig[activity.category];
                    return (
                      <div key={activity.id} className="flex gap-4">
                        {/* Time */}
                        <div className="flex flex-col items-center">
                          <div className="w-16 text-center">
                            <p className="text-sm font-semibold text-gray-900">{activity.time}</p>
                            {activity.duration && (
                              <p className="text-xs text-gray-500">{activity.duration}</p>
                            )}
                          </div>
                          {idx < groupedActivities[day].length - 1 && (
                            <div className="flex-1 w-0.5 bg-gray-200 my-2"></div>
                          )}
                        </div>

                        {/* Activity */}
                        <div className="flex-1 mb-2">
                          <div className="bg-gray-50 rounded-lg p-4 hover:shadow-md transition-shadow border border-gray-200">
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-2xl">{config.icon}</span>
                                  <h5 className="font-semibold text-gray-900">{activity.title}</h5>
                                </div>
                                <p className="text-sm text-gray-600 mb-2">{activity.description}</p>
                                
                                <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                                  {activity.location && (
                                    <span className="flex items-center gap-1">
                                      📍 {activity.location}
                                    </span>
                                  )}
                                  {activity.cost && (
                                    <span className="flex items-center gap-1 font-medium text-green-600">
                                      💵 ${activity.cost}
                                    </span>
                                  )}
                                  <span className={`px-2 py-1 rounded-full border ${config.color}`}>
                                    {activity.category}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          ))}
      </div>

      {/* Empty */}
      {activities.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <div className="text-6xl mb-4">📅</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Activities Yet</h3>
          <p className="text-gray-600">
            Start chatting with AI to build your personalized itinerary
          </p>
        </div>
      )}
    </div>
  );
}