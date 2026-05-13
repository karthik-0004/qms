import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const { pathname } = request.nextUrl;
  const path = pathname.replace('/api/platform', '');
  const searchParams = request.nextUrl.search;
  const url = `${apiUrl}/api/v1${path}${searchParams}`;
  
  console.log('[Platform Proxy] GET', { url, pathname });
  
  const headers = new Headers();
  headers.set('Content-Type', 'application/json');
  
  // Forward all relevant headers
  const authHeader = request.headers.get('authorization');
  if (authHeader) headers.set('authorization', authHeader);
  
  const cookie = request.headers.get('cookie');
  if (cookie) headers.set('cookie', cookie);
  
  const tenantId = request.headers.get('x-tenant-id');
  if (tenantId) headers.set('x-tenant-id', tenantId);
  
  const userId = request.headers.get('x-user-id');
  if (userId) headers.set('x-user-id', userId);
  
  const requestId = request.headers.get('x-request-id');
  if (requestId) headers.set('x-request-id', requestId);
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
    credentials: 'include',
  });
  
  console.log('[Platform Proxy] Response', { status: response.status });
  
  return response;
}

export async function POST(request: NextRequest) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const { pathname } = request.nextUrl;
  const path = pathname.replace('/api/platform', '');
  const searchParams = request.nextUrl.search;
  const url = `${apiUrl}/api/v1${path}${searchParams}`;
  
  const headers = new Headers();
  headers.set('Content-Type', 'application/json');
  
  // Forward authentication headers
  const authHeader = request.headers.get('authorization');
  if (authHeader) headers.set('authorization', authHeader);
  
  const cookie = request.headers.get('cookie');
  if (cookie) headers.set('cookie', cookie);
  
  // Forward CCV service headers
  const tenantId = request.headers.get('x-tenant-id');
  if (tenantId) headers.set('x-tenant-id', tenantId);
  
  const userId = request.headers.get('x-user-id');
  if (userId) headers.set('x-user-id', userId);
  
  const requestId = request.headers.get('x-request-id');
  if (requestId) headers.set('x-request-id', requestId);
  
  const body = await request.text();
  
  const response = await fetch(url, {
    method: 'POST',
    headers,
    credentials: 'include',
    body,
  });
  
  return response;
}

export async function PATCH(request: NextRequest) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const { pathname } = request.nextUrl;
  const path = pathname.replace('/api/platform', '');
  const url = `${apiUrl}/api/v1${path}`;
  
  const headers = new Headers();
  headers.set('Content-Type', 'application/json');
  
  const authHeader = request.headers.get('authorization');
  if (authHeader) headers.set('authorization', authHeader);
  
  const cookie = request.headers.get('cookie');
  if (cookie) headers.set('cookie', cookie);
  
  const tenantId = request.headers.get('x-tenant-id');
  if (tenantId) headers.set('x-tenant-id', tenantId);
  
  const userId = request.headers.get('x-user-id');
  if (userId) headers.set('x-user-id', userId);
  
  const requestId = request.headers.get('x-request-id');
  if (requestId) headers.set('x-request-id', requestId);
  
  const body = await request.text();
  
  const response = await fetch(url, {
    method: 'PATCH',
    headers,
    credentials: 'include',
    body,
  });
  
  return response;
}

export async function DELETE(request: NextRequest) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const { pathname } = request.nextUrl;
  const path = pathname.replace('/api/platform', '');
  const url = `${apiUrl}/api/v1${path}`;
  
  const headers = new Headers();
  headers.set('Content-Type', 'application/json');
  
  const authHeader = request.headers.get('authorization');
  if (authHeader) headers.set('authorization', authHeader);
  
  const cookie = request.headers.get('cookie');
  if (cookie) headers.set('cookie', cookie);
  
  const tenantId = request.headers.get('x-tenant-id');
  if (tenantId) headers.set('x-tenant-id', tenantId);
  
  const userId = request.headers.get('x-user-id');
  if (userId) headers.set('x-user-id', userId);
  
  const requestId = request.headers.get('x-request-id');
  if (requestId) headers.set('x-request-id', requestId);
  
  const response = await fetch(url, {
    method: 'DELETE',
    headers,
    credentials: 'include',
  });
  
  return response;
}
