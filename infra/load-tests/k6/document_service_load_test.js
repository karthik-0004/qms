/**
 * Phase E — k6 Load Test: Document Service (Phase B QMS)
 * Run: k6 run --vus 30 --duration 60s document_service_load_test.js
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const errorRate = new Rate("error_rate");
const listDuration = new Trend("list_documents_ms");
const createDuration = new Trend("create_document_ms");

export const options = {
  stages: [
    { duration: "10s", target: 10 },
    { duration: "40s", target: 30 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<1000"],
    error_rate: ["rate<0.01"],
  },
};

const BASE_URL = __ENV.DOC_URL || "http://localhost:8020";
const TENANT_ID = __ENV.TENANT_ID || "00000000-0000-0000-0000-000000000001";
const USER_ID = __ENV.USER_ID || "00000000-0000-0000-0000-000000000002";

const HEADERS = {
  "Content-Type": "application/json",
  "X-Tenant-ID": TENANT_ID,
  "X-User-ID": USER_ID,
};

export default function () {
  // List documents
  const listRes = http.get(
    `${BASE_URL}/api/v1/documents?page=1&page_size=20`,
    { headers: HEADERS }
  );
  const listOk = check(listRes, {
    "list 200": (r) => r.status === 200,
    "list < 1s": (r) => r.timings.duration < 1000,
  });
  listDuration.add(listRes.timings.duration);
  errorRate.add(!listOk);

  sleep(0.2);

  // Create document
  const payload = JSON.stringify({
    title: `Load Test Doc ${Date.now()}`,
    document_type: "sop",
    version: "1.0",
    content_url: "s3://rainer-dev/load-test/doc.pdf",
  });

  const createRes = http.post(`${BASE_URL}/api/v1/documents`, payload, {
    headers: HEADERS,
  });
  const createOk = check(createRes, {
    "create 201": (r) => r.status === 201,
    "create < 500ms": (r) => r.timings.duration < 500,
  });
  createDuration.add(createRes.timings.duration);
  errorRate.add(!createOk);

  sleep(1);
}
