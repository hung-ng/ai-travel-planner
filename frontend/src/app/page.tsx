import Link from 'next/link';

export default function Home() {
    return (
        <main className="min-h-screen p-8 bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-24">
                    <h1 className="text-6xl font-bold mb-8 bg-gradient-to-r from-blue-700 to-purple-700 bg-clip-text text-transparent">
                        Your Perfect Trip Starts Here
                    </h1>
                    <p className="text-xl text-gray-600 mb-24">
                        Tell us where you want to go, and our AI assistant will plan the perfect trip for you.
                    </p>
                </div>

                <div className="bg-white rounded-2xl shadow-xl p-12 mb-8">
                    <div className="mb-20">
                        <div className="grid md:grid-cols-2 gap-8 mb-16 max-w-4xl mx-auto mt-12">
                            <div className="flex items-start gap-4">
                                <span className="text-3xl mt-1">🤖</span>
                                <div>
                                    <h3 className="font-bold text-gray-800 text-xl mb-1">Smart AI Travel Assistant</h3>
                                    <p className="text-base text-gray-600">Conversational trip planning</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-4">
                                <span className="text-3xl mt-1">📅</span>
                                <div>
                                    <h3 className="font-bold text-gray-800 text-xl mb-1">Day-by-Day Itineraries</h3>
                                    <p className="text-base text-gray-600">Detailed schedules with activities</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-4">
                                <span className="text-3xl mt-1">💰</span>
                                <div>
                                    <h3 className="font-bold text-gray-800 text-xl mb-1">Automatic Budget Tracking</h3>
                                    <p className="text-base text-gray-600">Stay within spending limits</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-4">
                                <span className="text-3xl mt-1">💬</span>
                                <div>
                                    <h3 className="font-bold text-gray-800 text-xl mb-1">Personalized Suggestions</h3>
                                    <p className="text-base text-gray-600">Matches your travel style</p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4 max-w-md mx-auto">
                            <Link href='/chat' 
                                className="block w-full text-center bg-gradient-to-r from-blue-500 to-blue-600 text-white px-10 py-5 rounded-xl font-semibold text-xl hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl">
                                Start Planning Your Next Trip Now!
                            </Link>
                            
                            <div className="flex gap-4 pt-4">
                                <Link href='/signup' 
                                    className="w-full text-center bg-white border-2 border-purple-500 text-purple-500 px-6 py-3 rounded-xl font-semibold text-lg hover:bg-purple-50 transition-all">
                                    Sign Up
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
