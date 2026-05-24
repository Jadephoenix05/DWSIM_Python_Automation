import api from './api';

// Matches the views inside your backend/trains/views.py
export const searchTrains = async (fromCity, toCity, travelDate) => {
  const response = await api.get('/trains/', { 
    params: { 
      from: fromCity, 
      to: toCity, 
      date: travelDate 
    } 
  });
  return response.data;
};