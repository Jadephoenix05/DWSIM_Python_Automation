import { useState } from "react";

function Home() {
  const [type, setType] = useState("train");

  return (
    <div className="min-h-screen bg-blue-50 flex flex-col items-center pt-20">

      <h1 className="text-4xl font-bold text-blue-700 mb-10">
        Travel Booking
      </h1>

      <div className="bg-white shadow-lg rounded-lg p-8 w-[700px]">

        {/* Transport Type */}
        <div className="flex justify-center gap-6 mb-6">

          <button
            onClick={() => setType("train")}
            className={`px-4 py-2 rounded ${
              type === "train" ? "bg-blue-600 text-white" : "bg-gray-200"
            }`}
          >
            🚆 Train
          </button>

          <button
            onClick={() => setType("flight")}
            className={`px-4 py-2 rounded ${
              type === "flight" ? "bg-blue-600 text-white" : "bg-gray-200"
            }`}
          >
            ✈️ Flight
          </button>

          <button
            onClick={() => setType("bus")}
            className={`px-4 py-2 rounded ${
              type === "bus" ? "bg-blue-600 text-white" : "bg-gray-200"
            }`}
          >
            🚌 Bus
          </button>

        </div>

        {/* Search Form */}
        <div className="flex gap-4">

          <input
            type="text"
            placeholder="From"
            className="border p-2 rounded w-full"
          />

          <input
            type="text"
            placeholder="To"
            className="border p-2 rounded w-full"
          />

          <input
            type="date"
            className="border p-2 rounded"
          />

          <input
            type="number"
            placeholder="Passengers"
            min="1"
            className="border p-2 rounded w-24"
          />

          <button className="bg-blue-600 text-white px-5 rounded hover:bg-blue-700">
            Search
          </button>

        </div>

      </div>

    </div>
  );
}

export default Home;