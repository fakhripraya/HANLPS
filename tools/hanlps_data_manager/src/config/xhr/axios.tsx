import axios from "axios";

export const createAxios = (
  baseUrl: string | undefined
) => {
  return axios.create({
    baseURL: baseUrl,
    timeout: 61000,
    withCredentials: true,
  });
};
