import { request } from "../request";

export function getHealthStatus() { return request("/health"); }
