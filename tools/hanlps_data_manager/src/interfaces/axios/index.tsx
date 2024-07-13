/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  AxiosRequestConfig,
  AxiosRequestHeaders,
} from "axios";

export interface IRequestConfig {
  endpoint?: string;
  headers?: AxiosRequestHeaders;
  url?: string;
  params?: AxiosRequestConfig["params"];
  data?: AxiosRequestConfig["data"];
}

export interface IResponseObject {
  responseData?: any;
  responseStatus?: number;
  responseError: boolean;
  errorContent: string;
}
