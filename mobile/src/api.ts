import AsyncStorage from '@react-native-async-storage/async-storage';
import { Member, Result, isMember } from './domain';
import { ApiError, RequestOptions, sendRequest } from './network';
export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? '').trim().replace(/\/+$/, '');
export function request<T>(path: string, body?: object, options: RequestOptions = {}): Promise<T> {
  return sendRequest<T>(API_URL, path, body, options);
}
const DIRECTORY = 'g13.directory.v1', RESULT = 'g13.result.v1', PROFILE = 'g13.profile.v1';
export async function readDirectory(): Promise<Member[] | null> {
  try { const raw = await AsyncStorage.getItem(DIRECTORY); const data: unknown = raw ? JSON.parse(raw) : null;
    return Array.isArray(data) && data.length > 0 && data.every(isMember) ? data : null;
  } catch { return null; }
}
export async function saveDirectory(members: Member[]) { await AsyncStorage.setItem(DIRECTORY, JSON.stringify(members)); }
export async function saveResult(question: string, result: Result) {
  if (result.matched) await AsyncStorage.setItem(RESULT, JSON.stringify({ question, result }));
}
export async function readResult(): Promise<{question: string; result: Result} | null> {
  try { const raw = await AsyncStorage.getItem(RESULT); const v = raw ? JSON.parse(raw) : null;
    return typeof v?.question === 'string' && v?.result?.matched === true && typeof v.result.member?.id === 'string'
      && typeof v.result.introduction === 'string' && Array.isArray(v.result.evidenceLinks) ? v : null;
  } catch { return null; }
}
export async function saveProfile(member: Member) { await AsyncStorage.setItem(PROFILE, JSON.stringify(member)); }
export async function readProfile(): Promise<Member | null> {
  try { const raw = await AsyncStorage.getItem(PROFILE); const v: unknown = raw ? JSON.parse(raw) : null; return isMember(v) ? v : null; } catch { return null; }
}
export async function liveDirectory(): Promise<Member[]> {
  const directory = await request<{id: string}[]>('/members');
  if (!Array.isArray(directory) || !directory.length) throw new ApiError('response', 'The API returned an invalid member directory.');
  const profiles = await Promise.all(directory.map(m => request<Member>(`/members/${encodeURIComponent(m.id)}`)));
  if (!profiles.every(isMember)) throw new ApiError('response', 'The API returned invalid member profiles.');
  return profiles;
}
