import api from './api';


export const searchFlights = async (fromCity, toCity, travelDate) => {
  const response = await api.get('/flights/', { 
    params: { 
      from: fromCity, 
      to: toCity, 
      date: travelDate 
    } 
  });
  return response.data;
};