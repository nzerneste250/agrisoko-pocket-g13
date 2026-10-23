import { useCallback, useEffect, useReducer, useRef } from 'react';
import NetInfo from '@react-native-community/netinfo';
import { API_URL } from './api';
import { ApiError, connectivityReducer, initialConnectivity, verifyHealth } from './network';

export function useConnectivity() {
  const [connection, dispatch] = useReducer(connectivityReducer, initialConnectivity);
  const deviceRef = useRef(connection.device);
  const checkRef = useRef<AbortController | null>(null);
  const active = useRef(true);
  const checkBackend = useCallback(async () => {
    checkRef.current?.abort();
    const controller = new AbortController(); checkRef.current = controller;
    dispatch({ type: 'checking' });
    try {
      if (deviceRef.current.isConnected === false) throw new ApiError('offline', 'The device has no network connection. Use the offline directory or reconnect and check API health.');
      await verifyHealth(API_URL, { signal: controller.signal });
      if (active.current && checkRef.current === controller && !controller.signal.aborted) dispatch({ type: 'healthy', checkedAt: Date.now() });
      return !controller.signal.aborted;
    } catch (e) {
      if (active.current && checkRef.current === controller && !controller.signal.aborted) dispatch({ type: 'failed', error: e instanceof ApiError ? e : new ApiError('network', 'API health check failed.') });
      return false;
    }
  }, []);
  const reportFailure = useCallback((error: unknown) => {
    if (error instanceof ApiError && error.kind === 'cancelled') return;
    // Prevent an older health response from erasing a more recent request failure.
    checkRef.current?.abort();
    if (active.current) dispatch({ type: 'failed', error: error instanceof ApiError ? error : new ApiError('network', 'API request failed. Check API health before retrying.') });
  }, []);
  useEffect(() => {
    active.current = true;
    let lastKey = '';
    const unsubscribe = NetInfo.addEventListener(state => {
      const device = { isConnected: state.isConnected, isInternetReachable: state.isInternetReachable, type: state.type };
      const key = JSON.stringify([device, state.details]);
      if (key === lastKey) return;
      lastKey = key; deviceRef.current = device;
      dispatch({ type: 'network', device });
      // Public internet detection is not a prerequisite for a reachable local LAN API.
      void checkBackend();
    });
    return () => { active.current = false; checkRef.current?.abort(); unsubscribe(); };
  }, [checkBackend]);
  return { ...connection, checkBackend, reportFailure };
}
