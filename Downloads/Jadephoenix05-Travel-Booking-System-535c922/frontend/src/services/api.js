import axios from 'axios';

const api = axios.create({
    baserURL: 'http://127.0.0.1:8000',
    headers: {
        'Content-Type':'application/json',
    },
});

export default api;
