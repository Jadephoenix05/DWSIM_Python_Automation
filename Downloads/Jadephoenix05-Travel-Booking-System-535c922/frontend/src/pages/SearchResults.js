import React, { useState, useEffect } from 'react';
import { searchBuses } from '../services/busService';

function SearchResults() {
  const [buses, setBuses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    searchBuses('Mumbai', 'Goa')
      .then(data => {
        setBuses(data); 
        setLoading(false);
      })
      .catch(err => {
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="text-center mt-5">Loading available buses...</p>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Available Buses</h2>
      {buses.length === 0 ? (
        <p>No buses found for this route.</p>
      ) : (
        <div className="grid gap-4">
          {buses.map((bus) => (
            // Assuming your Django Bus model has 'id', 'name', and 'price' fields
            <div key={bus.id} className="border p-4 rounded shadow bg-white flex justify-between">
              <div>
                <h3 className="font-semibold text-lg">{bus.name}</h3>
                <p className="text-gray-600">{bus.source} ➔ {bus.destination}</p>
              </div>
              <div className="text-right">
                <span className="text-xl font-bold text-green-600">${bus.price}</span>
                <button className="block mt-2 bg-blue-600 text-white px-4 py-1 rounded">Book Now</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchResults;