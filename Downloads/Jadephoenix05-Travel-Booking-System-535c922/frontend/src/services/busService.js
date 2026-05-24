import api from './api';


export const searchBuses = async (fromCity, toCity, travelDate) => {
  const response = await api.get('/buses/', { 
    params: { 
      from: fromCity, 
      to: toCity, 
      date: travelDate 
    } 
  });
  return response.data;
};