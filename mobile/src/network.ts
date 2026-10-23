export type FailureKind = 'configuration' | 'offline' | 'timeout' | 'cancelled' | 'http' | 'security' | 'network' | 'response';
export class ApiError extends Error {
  constructor(public readonly kind: FailureKind, message: string, public readonly status?: number) {
    super(message); this.name = 'ApiError';
  }
}
export const DEFAULT_TIMEOUT_MS = 10000;
export type RequestOptions = { signal?: AbortSignal; timeoutMs?: number; fetchImpl?: typeof fetch };
export function isPrivateApi(baseUrl: string): boolean {
  try { const host = new URL(baseUrl).hostname;
    return /^(10\.|192\.168\.|127\.)/.test(host) || /^172\.(1[6-9]|2\d|3[01])\./.test(host) || host === 'localhost';
  } catch { return false; }
}
export function networkAdvice(baseUrl: string): string {
  return isPrivateApi(baseUrl)
    ? 'This is a private LAN address. Use Wi-Fi or a VPN that can reach the API computer; mobile data alone does not provide that route. Check the server address, port and firewall.'
    : 'Check the API address, server availability and your network connection.';
}
export function errorMessage(error: unknown, baseUrl = ''): string {
  return error instanceof ApiError ? error.message : `The API request could not be completed. ${networkAdvice(baseUrl)}`;
}
export async function sendRequest<T>(baseUrl: string, path: string, body?: object, options: RequestOptions = {}): Promise<T> {
  if (!baseUrl) throw new ApiError('configuration', 'API URL is not configured. The offline directory is available.');
  try { const url = new URL(baseUrl);
    if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) throw new Error();
  } catch { throw new ApiError('configuration', 'The configured API URL is invalid. Use an HTTP or HTTPS server address without credentials, query or fragment.'); }
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  let abortCause: 'timeout' | 'cancelled' | undefined;
  const cancel = () => { if (!abortCause) { abortCause = 'cancelled'; controller.abort(); } };
  options.signal?.addEventListener('abort', cancel, { once: true });
  if (options.signal?.aborted) cancel();
  const timer = setTimeout(() => { if (!abortCause) { abortCause = 'timeout'; controller.abort(); } }, timeoutMs);
  try {
    if (abortCause) throw new Error('Aborted before request');
    const response = await (options.fetchImpl ?? fetch)(`${baseUrl.replace(/\/+$/, '')}${path}`, {
      method: body ? 'POST' : 'GET', headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined, signal: controller.signal,
    });
    if (!response.ok) throw new ApiError('http', `API returned HTTP ${response.status}${response.status >= 500 ? ' (server error)' : ' (request rejected)'}. Try again or use the offline directory.`, response.status);
    try { return await response.json() as T; }
    catch (e) { if (controller.signal.aborted) throw e; throw new ApiError('response', 'The API returned an unreadable response. The offline directory remains available.'); }
  } catch (e) {
    // Native fetch may reject an aborted request with TypeError rather than AbortError.
    // Our own abort cause is authoritative, including during response-body reading.
    if (abortCause === 'timeout') throw new ApiError('timeout', `API request timed out after ${timeoutMs / 1000} seconds. ${networkAdvice(baseUrl)}`);
    if (abortCause === 'cancelled') throw new ApiError('cancelled', 'Request canceled by you. Your last useful result is retained.');
    if (e instanceof ApiError) throw e;
    const detail = e instanceof Error ? e.message : '';
    if (/cleartext.*(not permitted|denied|blocked)|CLEARTEXT_NOT_PERMITTED/i.test(detail)) {
      throw new ApiError('security', 'Android blocked cleartext HTTP. Rebuild and reinstall the controlled preview APK, or configure an HTTPS API.');
    }
    // A native "canceled" string by itself does not prove user cancellation or timeout.
    throw new ApiError('network', `The API could not be reached; the network request failed or was interrupted. ${networkAdvice(baseUrl)}`);
  } finally { clearTimeout(timer); options.signal?.removeEventListener('abort', cancel); }
}
export type Health = { status: string; groupCode: string; version: string };
export async function verifyHealth(baseUrl: string, options: RequestOptions = {}): Promise<Health> {
  const health = await sendRequest<Health>(baseUrl, '/health', undefined, options);
  if (!health || health.status !== 'ok' || health.groupCode !== 'G13' || typeof health.version !== 'string') {
    throw new ApiError('response', 'The server did not return the expected AgriSoko G13 health response. Check the API address.');
  }
  return health;
}
export type DeviceNetwork = { isConnected: boolean | null; isInternetReachable: boolean | null; type: string };
export type BackendStatus = { status: 'unchecked' | 'checking' | 'reachable' | 'unreachable' | 'unconfigured'; checkedAt?: number; message?: string };
export type Connectivity = { device: DeviceNetwork; backend: BackendStatus };
export const initialConnectivity: Connectivity = { device: { isConnected: null, isInternetReachable: null, type: 'unknown' }, backend: { status: 'unchecked' } };
export type ConnectivityEvent =
  | { type: 'network'; device: DeviceNetwork }
  | { type: 'checking' }
  | { type: 'healthy'; checkedAt: number }
  | { type: 'failed'; error: ApiError };
export function connectivityReducer(state: Connectivity, event: ConnectivityEvent): Connectivity {
  switch (event.type) {
    case 'network': return { device: event.device, backend: { status: 'unchecked' } };
    case 'checking': return { ...state, backend: { status: 'checking' } };
    case 'healthy': return { ...state, backend: { status: 'reachable', checkedAt: event.checkedAt } };
    case 'failed': return event.error.kind === 'cancelled' ? state : { ...state, backend: {
      status: event.error.kind === 'configuration' ? 'unconfigured' : 'unreachable', message: event.error.message,
    } };
  }
}
export function deviceLabel(device: DeviceNetwork): string {
  const transport = device.type === 'cellular' ? 'Mobile data' : device.type === 'wifi' ? 'Wi-Fi' : 'Network';
  if (device.isConnected === false) return 'Device: no network connection';
  if (device.isConnected === null) return 'Device: checking network';
  return `${transport} available | Internet: ${device.isInternetReachable === true ? 'available' : device.isInternetReachable === false ? 'not detected' : 'not yet verified'}`;
}
export function backendLabel(backend: BackendStatus): string {
  switch (backend.status) {
    case 'reachable': return 'API: health check passed';
    case 'checking': return 'API: checking health';
    case 'unreachable': return 'API: unavailable';
    case 'unconfigured': return 'API: not configured';
    default: return 'API: not checked';
  }
}
