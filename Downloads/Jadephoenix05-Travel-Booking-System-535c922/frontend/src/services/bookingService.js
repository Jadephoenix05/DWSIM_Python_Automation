import api from './api';

export const getUserBookings = async () => {
  try {
    const response = await api.get('/bookings/');
    return response.data; 
  } catch (error) {
    console.error("Error fetching bookings:", error);
    throw error;
  }
};