'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';

interface User {
  id: number;
  name: string;
  email: string;
  avatar: string;
}

// user need to be replace with real auth
const currentUser: User = {
  id: 1,
  name: 'John Traveler',
  email: 'john@example.com',
  avatar: '👤',
};

export default function UserMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const [user] = useState<User>(currentUser);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    // need to actual logout
    console.log('Logging out...');
    alert('Logout functionality will be implemented with real auth');
  };

  return (
    <div className="relative" ref={menuRef}>
      {/* Avatar Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-xl">
          {user.avatar}
        </div>
        <div className="hidden md:block text-left">
          <p className="text-sm font-semibold text-gray-900">{user.name}</p>
          <p className="text-xs text-gray-500">View Profile</p>
        </div>
        <svg 
          className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
          {/* User Info */}
          <div className="p-4 border-b border-gray-200">
            <p className="font-semibold text-gray-900">{user.name}</p>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>

          {/* Menu */}
          <div className="p-2">
            <Link
              href="/profile"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <span className="text-xl">👤</span>
              <div>
                <div className="font-medium">My Profile</div>
                <div className="text-xs text-gray-500">Manage preferences</div>
              </div>
            </Link>

            <Link
              href="/dashboard"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <span className="text-xl">🗺️</span>
              <div>
                <div className="font-medium">My Trips</div>
                <div className="text-xs text-gray-500">View all trips</div>
              </div>
            </Link>

            <Link
              href="/chat"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <span className="text-xl">💬</span>
              <div>
                <div className="font-medium">New Trip</div>
                <div className="text-xs text-gray-500">Plan with AI</div>
              </div>
            </Link>

            <div className="border-t border-gray-200 my-2"></div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors w-full"
            >
              <span className="text-xl">🚪</span>
              <div className="text-left">
                <div className="font-medium">Logout</div>
                <div className="text-xs text-red-400">Sign out of account</div>
              </div>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}