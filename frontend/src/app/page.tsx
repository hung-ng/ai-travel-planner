import Link from 'next/link';

export default function Home() {
    return (
        <main className="min-h-screen p-8 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-24">
                    <h1 className="text-6xl font-bold mb-8 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Welcome to AI Travel Planner
                    </h1>
                    <p className="text-xl text-gray-600 mb-24">
                        Plan your trips with AI-powered tools. Discover new places, create itineraries, and get personalized recommendations.
                    </p>

                    <div className="grid md:grid-cols-3 gap-8 mb-24">
                        <div className="bg-white p-8 rounded-xl shadow-md">
                            <div className="text-4xl mb-4">💬</div>
                            <h3 className="text-xl font-semibold mb-3">Conversations</h3>
                            <p className="text-gray-600 text-base">
                                Chat with AI about your travel preferences and get instant recommendations
                            </p>
                        </div>

                        <div className="bg-white p-8 rounded-xl shadow-md">
                            <div className="text-4xl mb-4">📍</div>
                            <h3 className="text-xl font-semibold mb-3">Suggestions</h3>
                            <p className="text-gray-600 text-base">
                                Get personalized suggestions for attractions, restaurants, and activities
                            </p>
                        </div>

                        <div className="bg-white p-8 rounded-xl shadow-md">
                            <div className="text-4xl mb-4">📅</div>
                            <h3 className="text-xl font-semibold mb-3">Daily Plans</h3>
                            <p className="text-gray-600 text-base">
                                Receive detailed day-to-day itineraries for your schedule
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-xl p-12 mb-8">
                    <div className="mb-20">
                        <h2 className="text-4xl font-bold mb-8 text-center">Get Started On Your Journey
                        </h2>
                        <p className="text-lg text-gray-600 mb-12 text-center max-w-3xl mx-auto">
                            Chat with our AI assistant to create personalized itineraries, discover hidden gems, 
                            and plan every detail of your perfect trip.
                        </p>
                        <div className="grid md:grid-cols-2 gap-8 mb-16 max-w-4xl mx-auto">
                            <ul className="space-y-4">
                                <li className="flex items-center text-gray-700 text-lg">
                                    <span className="mr-4 text-2xl">🤖</span>
                                    AI-powered recommendations
                                </li>
                                <li className="flex items-center text-gray-700 text-lg">
                                    <span className="mr-4 text-2xl">🗺️</span>
                                    Personalized itineraries
                                </li>
                            </ul>
                            <ul className="space-y-4">
                                <li className="flex items-center text-gray-700 text-lg">
                                    <span className="mr-4 text-2xl">💰</span>
                                    Budget-conscious planning
                                </li>
                                <li className="flex items-center text-gray-700 text-lg">
                                    <span className="mr-4 text-2xl">🎯</span>
                                    Tailored to your interests
                                </li>
                            </ul>
                        </div>

                        <div className="space-y-4 max-w-md mx-auto">
                            <Link href='/chat' 
                                className="block w-full text-center bg-gradient-to-r from-blue-500 to-blue-600 text-white px-10 py-5 rounded-xl font-semibold text-xl hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl">
                                Start Planning Your Next Trip Now!
                            </Link>
                        </div>
                    </div>

                    <div className="text-center mt-12 text-gray-500 text-sm">
                        <p>Powered by GPT-4.1-nano and intelligent travel planning algorithms</p>
                    </div>
                </div>
            </div>
        </main>
    );
}
