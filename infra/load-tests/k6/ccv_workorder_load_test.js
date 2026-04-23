/**
 * Phase E — k6 Load Test: CCV Work Order Service (Phase D)
 * Run: k6 run --vus 20 --duration 60s ccv_workorder_load_test.js
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const errorRate = new Rate("error_rate");
const listDuration = new Trend("list_workorders_ms");

export const options = {
  stages: [
    { duration: "10s", target: 10 },
    { duration: "40s", target: 20 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<800"],
    error_rate: ["rate<0.01"],
  },
};

const BASE_URL = __ENV.WORKORDER_URL || "http://localhost:8042";
const TENANT_ID = __ENV.TENANT_ID || "00000000-0000-0000-0000-000000000001";
const USER_ID = __ENV.USER_ID || "00000000-0000-0000-0000-000000000002";

const HEADERS = {
  "Content-Type": "application/json",
  "X-Tenant-ID": TENANT_ID,
  "X-User-ID": USER_ID,
};

export default function () {
  // Health
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, { "health 200": (r) => r.status === 200 });

  // List work orders
  const listRes = http.get(
    `${BASE_URL}/api/v1/work-orders?page=1&page_size=20`,
    { headers: HEADERS }
  );
  const listOk = check(listRes, {
    "list 200": (r) => r.status === 200,
    "list < 800ms": (r) => r.timings.duration < 800,
  });
  listDuration.add(listRes.timings.duration);
  errorRate.add(!listOk);

  sleep(1);
}
