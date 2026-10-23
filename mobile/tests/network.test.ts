import assert from 'node:assert/strict';
import test from 'node:test';
import { ApiError, Connectivity, connectivityReducer, deviceLabel, backendLabel, initialConnectivity, isPrivateApi, sendRequest, verifyHealth } from '../src/network';
const API = 'http://172.30.114.74:8000';
const jsonFetch = (value: unknown, status = 200): typeof fetch => (async () => new Response(JSON.stringify(value), { status })) as typeof fetch;
const nativeAbortFetch: typeof fetch = ((_input, init) => new Promise((_resolve, reject) => {
  init?.signal?.addEventListener('abort', () => reject(new TypeError('fetch failed: Fetch request has been canceled')), { once: true });
})) as typeof fetch;
const failure = (kind: ApiError['kind']) => (error: unknown) => error instanceof ApiError && error.kind === kind;

test('timer abort is a timeout even when native fetch uses TypeError and cancellation wording', async () => {
  await assert.rejects(sendRequest(API, '/health', undefined, { timeoutMs: 5, fetchImpl: nativeAbortFetch }), error =>
    failure('timeout')(error) && (error as Error).message.includes('private LAN'));
});
test('explicit caller abort is user cancellation, not timeout or backend failure', async () => {
  const controller = new AbortController();
  const response = sendRequest(API, '/ask', { question: 'Erneste' }, { signal: controller.signal, fetchImpl: nativeAbortFetch });
  controller.abort(); await assert.rejects(response, failure('cancelled'));
});
test('pre-canceled requests never call fetch', async () => {
  const controller = new AbortController(); controller.abort(); let called = false;
  await assert.rejects(sendRequest(API, '/health', undefined, { signal: controller.signal, fetchImpl: (async () => { called = true; return new Response('{}'); }) as typeof fetch }), failure('cancelled'));
  assert.equal(called, false);
});
test('native cancellation text without our abort remains an interrupted network request', async () => {
  await assert.rejects(sendRequest(API, '/health', undefined, { fetchImpl: (async () => { throw new TypeError('Fetch request has been canceled'); }) as typeof fetch }), failure('network'));
});
test('HTTP request and server errors retain their status', async () => {
  for (const status of [422, 503]) {
    await assert.rejects(sendRequest(API, '/ask', {}, { fetchImpl: jsonFetch({}, status) }), error => failure('http')(error) && (error as ApiError).status === status);
  }
});
test('explicit Android cleartext denial is a security error', async () => {
  await assert.rejects(sendRequest(API, '/health', undefined, { fetchImpl: (async () => { throw new Error('CLEARTEXT communication not permitted by network security policy'); }) as typeof fetch }), failure('security'));
});
test('invalid configuration and unreadable responses are distinct', async () => {
  await assert.rejects(sendRequest('', '/health'), failure('configuration'));
  await assert.rejects(sendRequest('ftp://example.com', '/health'), failure('configuration'));
  await assert.rejects(sendRequest(API, '/health', undefined, { fetchImpl: (async () => new Response('not json')) as typeof fetch }), failure('response'));
});
test('request preserves POST payload and timeout covers response body decoding', async () => {
  const transport = (async (url, init) => {
    assert.equal(url, `${API}/ask`); assert.equal(init?.method, 'POST');
    assert.deepEqual(JSON.parse(init?.body as string), { question: 'Who is Erneste?' });
    return { ok: true, json: () => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new TypeError('canceled')), { once: true });
    }) } as Response;
  }) as typeof fetch;
  await assert.rejects(sendRequest(API, '/ask', { question: 'Who is Erneste?' }, { timeoutMs: 5, fetchImpl: transport }), failure('timeout'));
});
test('health must be a successful G13 response, not just HTTP 200', async () => {
  for (const value of [{ status: 'ok' }, { status: 'ok', groupCode: 'G99', version: '1' }, { status: 'down', groupCode: 'G13', version: '1' }]) {
    await assert.rejects(verifyHealth(API, { fetchImpl: jsonFetch(value) }), failure('response'));
  }
  assert.equal((await verifyHealth(API, { fetchImpl: jsonFetch({ status: 'ok', groupCode: 'G13', version: '1.0.0' }) })).status, 'ok');
});
test('device mobile internet never implies API reachability', () => {
  const state = connectivityReducer(initialConnectivity, { type: 'network', device: { type: 'cellular', isConnected: true, isInternetReachable: true } });
  assert.match(deviceLabel(state.device), /Mobile data available/);
  assert.equal(state.backend.status, 'unchecked'); assert.equal(backendLabel(state.backend), 'API: not checked');
  assert.equal(connectivityReducer(state, { type: 'checking' }).backend.status, 'checking');
});
test('LAN API can be healthy without public internet and network changes invalidate old health', () => {
  const localOnly = { type: 'wifi', isConnected: true, isInternetReachable: false };
  const state = connectivityReducer(initialConnectivity, { type: 'network', device: localOnly });
  const healthy = connectivityReducer(state, { type: 'healthy', checkedAt: 123 });
  assert.equal(healthy.backend.status, 'reachable'); assert.match(deviceLabel(healthy.device), /Internet: not detected/);
  assert.equal(connectivityReducer(healthy, { type: 'network', device: localOnly }).backend.status, 'unchecked');
});
test('timeout changes backend health but user cancellation preserves it; retry clears failure', () => {
  const healthy: Connectivity = { ...initialConnectivity, backend: { status: 'reachable', checkedAt: 123 } };
  assert.equal(connectivityReducer(healthy, { type: 'failed', error: new ApiError('cancelled', 'Canceled') }), healthy);
  const failed = connectivityReducer(healthy, { type: 'failed', error: new ApiError('timeout', 'Timed out') });
  assert.equal(failed.backend.status, 'unreachable');
  assert.deepEqual(connectivityReducer(failed, { type: 'healthy', checkedAt: 456 }).backend, { status: 'reachable', checkedAt: 456 });
});
test('private address advice covers the configured API without labeling public hosts private', () => {
  assert.equal(isPrivateApi(API), true); assert.equal(isPrivateApi('http://172.31.1.2'), true);
  assert.equal(isPrivateApi('https://172.32.1.2'), false); assert.equal(isPrivateApi('https://example.com'), false);
});
