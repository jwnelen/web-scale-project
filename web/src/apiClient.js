import axios from "axios";

// const baseURL = 'http://localhost:3000/api';
const baseURL = 'https://example.com'

const instance = axios.create({
  baseURL: baseURL,
  timeout: 1000,
});



export const get = (url) => {
  return instance({
    method: 'get',
    url: `${url}`
  })
}

