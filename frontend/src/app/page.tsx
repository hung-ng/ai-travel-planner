import Link from, 'next/link';
import Image from 'next/image';
import styles from './page.module.css';

export default function Home() {
    return (
        <main className='min-h-screen p-8'>
            <div className='max-w-6xl mx-auto'>
                <div className="text-center mb-12">
                    <h1 className='text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent'>
                    Welcome to AI Travel Planner
                    </h1>
                    <p className='text-xl text-gray-700'>
                    Plan your trips with AI-powered tools. Discover new places, create itineraries, and get personalized recommendations.
                </p>
            </div>

            <div className='bg-white rounded-2xl shadow-xl p-8 mb-8'>
                <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
                <h2 className='text-3xl font-bold mb-4'>Get Started On Your Journey
                </h2>
                <p className='text-gray-600 mb-6'>
                    Chat with our AI assistant to create personalized itineraries, discover hidden gems, 
                and plan every detail of your perfect trip.
                </p>
                 <ul className='space-y-3 mb-6'>
                <li className='flex items-center text-gray-700'>
                  <span className='mr-3'>🤖</span>
                  AI-powered recommendations
                </li>
                <li className='flex items-center text-gray-700'>
                  <span className='mr-3'>🗺️</span>
                  Personalized itineraries
                </li>
                <li className='flex items-center text-gray-700'>
                  <span className='mr-3'>💰</span>
                  Budget-conscious planning
                </li>
                <li className='flex items-center text-gray-700'>
                  <span className='mr-3'>🎯</span>
                  Tailored to your interests
                </li>
              </ul>
            </div>
            <div>
                <div className='space-y-4'>
                    <Link href='/chat' 
                    className='block w-full text-center bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl'>
                        Start Planning Now
                    </Link>
                    <p className='text-center text-sm text-gray-500'>
                        No credit card required. Get started for free!
                    </p>
                </div>
            </div>
        </div>
        <div className='grid md:grid-cols-3 gap-6'>
          <div className='bg-white p-6 rounded-xl shadow-md'>
            <div className='text-4xl mb-3'>💬</div>
            <h3 className='text-xl font-semibold mb-2'>Conversations</h3>
            <p className='text-gray-600'>
              Chat with AI about your travel preferences and get instant recommendations
            </p>
          </div>

          <div className='bg-white p-6 rounded-xl shadow-md'>
            <div className='text-4xl mb-3'>📍</div>
            <h3 className='text-xl font-semibold mb-2'>Suggestions</h3>
            <p className='text-gray-600'>
              Get personalized suggestions for attractions, restaurants, and activities
            </p>
          </div>

          <div className='bg-white p-6 rounded-xl shadow-md'>
            <div className='text-4xl mb-3'>📅</div>
            <h3 className='text-xl font-semibold mb-2'>Daily Plans</h3>
            <p className='text-gray-600'>
              Receive detailed day-to-day itineraries for your schedule
            </p>
          </div>
        </div>

        <div className='text-center mt-12 text-gray-500 text-sm'>
           <p>Powered by GPT-4.1-nano and intelligent travel planning algorithms</p>
        </div>
      </div>
    </main>
    );
}