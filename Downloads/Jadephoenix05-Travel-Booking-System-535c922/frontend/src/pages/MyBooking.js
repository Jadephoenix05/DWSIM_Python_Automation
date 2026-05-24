import React, { useState, useEffect } from 'react';
import { getUserBookings } from '../services/bookingService';

function MyBooking() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUserBookings()
      .then(data => {
        setBookings(data);
        setLoading(false);
      })
      .catch(err => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="text-center mt-10 text-gray-600">Loading your bookings...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">My Bookings</h1>

      {bookings.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded text-center text-yellow-700">
          You haven't booked any trips yet!
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div key={booking.id} className="border p-5 rounded-lg shadow-sm bg-white border-gray-200 flex justify-between items-center">
              <div>
                {/* Visual badge for type of travel */}
                <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded font-semibold uppercase mb-2">
                  {booking.travel_type || 'Trip'} 
                </span>
                <h3 className="text-xl font-semibold text-gray-700">
                  {booking.source} ➔ {booking.destination}
                </h3>
                <p className="text-sm text-gray-500 mt-1">Date: {booking.travel_date}</p>
                <p className="text-sm text-gray-500">Status: <span className="text-green-600 font-medium">{booking.status || 'Confirmed'}</span></p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">Total Paid</p>
                <p className="text-2xl font-bold text-gray-800">${booking.total_price}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyBooking;