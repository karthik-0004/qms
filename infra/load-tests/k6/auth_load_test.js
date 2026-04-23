/**
 * Phase E — k6 Load Test: Authentication Service
 * Run: k6 run --vus 50 --duration 60s auth_load_test.js
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const errorRate = new Rate("error_rate");
const loginDuration = new Trend("login_duration_ms");

export const options = {
  stages: [
    { duration: "10s", target: 20 },
    { duration: "30s", target: 50 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    error_rate: ["rate<0.01"],
  },
};

const BASE_URL = __ENV.AUTH_URL || "http://localhost:8001";

export default function () {
  const payload = JSON.stringify({
    email: `load_test_${Math.floor(Math.random() * 1000)}@rainer.test`,
    password: "TestPassword123!",
  });

  const params = {
    headers: { "Content-Type": "application/json" },
    timeout: "5s",
  };

  // Login
  const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, payload, params);
  const loginOk = check(loginRes, {
    "login status 200 or 401": (r) => [200, 401].includes(r.status),
    "login response time < 500ms": (r) => r.timings.duration < 500,
  });
  loginDuration.add(loginRes.timings.duration);
  errorRate.add(!loginOk);

  // Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    "health 200": (r) => r.status === 200,
    "health < 50ms": (r) => r.timings.duration < 50,
  });

  sleep(0.5);
}
