export default function Home() {
    return (
        <main className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Deli Admin</h1>
                    <p className="text-gray-600">Manage your knowledge quizzes</p>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Stats Cards */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500">Pending Review</h3>
                        <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500">Total Quizzes</h3>
                        <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500">Last Sync</h3>
                        <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
                    </div>
                </div>

                {/* Inbox Section */}
                <section className="mt-8">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Inbox</h2>
                    <div className="bg-white rounded-lg shadow">
                        <div className="p-8 text-center text-gray-500">
                            <p>No pending items</p>
                            <p className="text-sm mt-2">
                                Connect your Notion workspace to start generating quizzes
                            </p>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    );
}
