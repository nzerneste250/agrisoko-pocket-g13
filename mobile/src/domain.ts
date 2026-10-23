export type Member = {
  id: string; fullName: string; registrationNumber?: string | null; aliases: string[];
  githubUsername?: string | null; role?: string | null; skills: string[];
  targetUser?: string | null; problem?: string | null; contribution?: string | null;
  feature?: string | null; outcomeMetric?: string | null; evidenceLinks: string[];
  testerFeedback?: string | null; introductionDraft?: string | null; approvalStatus: string;
};
export type Result = { matched: boolean; member: Partial<Member> & Pick<Member, 'id' | 'fullName'> | null;
  confidence: number; reason: string; introduction: string; evidenceLinks: string[];
  modelVersion: string; groupCode: string };
export type Source = 'live' | 'cached' | 'offline bundled' | 'offline cached';
export const normalize = (s: string) => s.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const contains = (q: string, value: string) => !!normalize(value) && ` ${q} `.includes(` ${normalize(value)} `);
export function localSearch(question: string, members: Member[]): Result {
  const q = normalize(question);
  const member = members.find(m => [m.fullName, ...m.aliases, m.registrationNumber, m.githubUsername].some(v => v && contains(q, v)))
    ?? members.find(m => m.role && contains(q, m.role));
  return { matched: !!member, member: member ?? null, confidence: member ? 1 : 0,
    reason: member ? 'Offline exact identifier or role lookup; no TF-IDF similarity runs on device.' : 'No exact offline match. Try a full name, declared alias or role, or select the directory.',
    introduction: member ? `${member.fullName}. ${member.role ?? ''} Profile status: ${member.approvalStatus}.` : '',
    evidenceLinks: member?.approvalStatus === 'approved' ? member.evidenceLinks : [], modelVersion: '1.0.0', groupCode: 'G13' };
}
export function safeEvidenceUrl(value: string): boolean {
  try { const u = new URL(value); return u.protocol === 'https:' && !!u.hostname && !u.username && !u.password; } catch { return false; }
}
export function validQuestion(value: string): boolean { return value.trim().length > 0 && value.length <= 500; }
export function isMember(value: unknown): value is Member {
  if (!value || typeof value !== 'object') return false;
  const m = value as Member;
  return typeof m.id === 'string' && typeof m.fullName === 'string' && ['pending','approved'].includes(m.approvalStatus)
    && ['aliases','skills','evidenceLinks'].every(k => Array.isArray(m[k as keyof Member]) && (m[k as keyof Member] as unknown[]).every(v => typeof v === 'string'));
}
