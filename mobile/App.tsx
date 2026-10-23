import React, { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Alert, BackHandler, Linking, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import bundled from './src/members.json';
import { Member, Result, Source, isMember, localSearch, safeEvidenceUrl, validQuestion } from './src/domain';
import { API_URL, liveDirectory, readDirectory, readProfile, readResult, request, saveDirectory, saveProfile, saveResult } from './src/api';
import { ApiError, backendLabel, deviceLabel, errorMessage, isPrivateApi } from './src/network';
import { useConnectivity } from './src/useConnectivity';

type Screen = 'Home' | 'Ask the Team' | 'AI Result' | 'Member Directory' | 'Member Profile' | 'About and Evidence';
const roster = bundled as Member[];
const PENDING = 'Pending verification';
function Button({ title, onPress, disabled = false, secondary = false }: {
  title: string; onPress: () => void; disabled?: boolean; secondary?: boolean;
}) {
  return <Pressable accessibilityRole="button" accessibilityState={{ disabled }} disabled={disabled} onPress={onPress}
    style={({ pressed }) => [s.button, secondary && s.secondaryButton, (disabled || pressed) && s.dim]}>
    <Text style={[s.buttonText, secondary && s.secondaryButtonText]}>{title}</Text>
  </Pressable>;
}
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return <View style={s.card}><Text accessibilityRole="header" style={s.sectionTitle}>{title}</Text>{children}</View>;
}
function Field({ label, value }: { label: string; value?: string | null }) {
  return <View style={s.field}><Text style={s.fieldLabel}>{label}</Text><Text selectable style={s.fieldValue}>{value || PENDING}</Text></View>;
}
function Evidence({ links }: { links: string[] }) {
  const safeLinks = links.filter(safeEvidenceUrl);
  return <>{safeLinks.length === 0 && <Text style={s.muted}>No verified evidence links supplied.</Text>}{safeLinks.map(url =>
    <Button secondary key={url} title={url} onPress={() => { Linking.openURL(url).catch(() => Alert.alert('Link unavailable', 'The device could not open this HTTPS link.')); }} />)}</>;
}
const profileFields = [
  ['registrationNumber', 'Registration number'], ['githubUsername', 'GitHub username'], ['role', 'Role'],
  ['skills', 'Skills'], ['targetUser', 'Intended users'], ['problem', 'Problem addressed'],
  ['contribution', 'Contribution'], ['feature', 'Feature'], ['outcomeMetric', 'Measured outcome'],
  ['testerFeedback', 'Tester feedback'], ['introductionDraft', 'Introduction'],
] as const;
export default function App() { return <SafeAreaProvider><Content /></SafeAreaProvider>; }
function Content() {
  const [screen, setScreen] = useState<Screen>('Home');
  const [history, setHistory] = useState<Screen[]>([]);
  const [members, setMembers] = useState<Member[]>(roster);
  const [directorySource, setDirectorySource] = useState<Source>('offline bundled');
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<Result | null>(null);
  const [lastUseful, setLastUseful] = useState<{ question: string; result: Result } | null>(null);
  const [resultSource, setResultSource] = useState<Source>('offline bundled');
  const [profile, setProfile] = useState<Member | null>(null);
  const [profileSource, setProfileSource] = useState<Source>('offline bundled');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [model, setModel] = useState<Record<string, unknown> | null>(null);
  const [modelBusy, setModelBusy] = useState(false);
  const { device, backend, checkBackend, reportFailure } = useConnectivity();
  const liveSeen = useRef(false);
  const hasDirectoryCache = useRef(false);
  const cachedProfile = useRef<Member | null>(null);
  const selectionVersion = useRef(0);
  const directoryVersion = useRef(0);
  const askController = useRef<AbortController | null>(null);
  const mounted = useRef(true);
  const go = (next: Screen) => {
    askController.current?.abort(); selectionVersion.current++;
    if (next !== screen) { setHistory(h => [...h, screen]); setScreen(next); }
  };
  const back = () => {
    askController.current?.abort(); selectionVersion.current++;
    setScreen(history[history.length - 1] ?? 'Home'); setHistory(h => h.slice(0, -1));
  };
  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => { if (history.length) { back(); return true; } return false; });
    return () => sub.remove();
  }, [history]);
  useEffect(() => {
    mounted.current = true;
    async function init() {
      const [cached, saved, savedProfile] = await Promise.all([readDirectory(), readResult(), readProfile()]);
      if (!mounted.current) return;
      if (cached && !liveSeen.current) { setMembers(cached); hasDirectoryCache.current = true; setDirectorySource('cached'); }
      setLastUseful(saved); cachedProfile.current = savedProfile;
    }
    void init();
    return () => { mounted.current = false; askController.current?.abort(); directoryVersion.current++; selectionVersion.current++; };
  }, []);
  useEffect(() => {
    const version = ++directoryVersion.current;
    if (backend.status !== 'reachable') {
      setDirectorySource(source => source === 'live' || source === 'cached' ? 'offline cached' : source);
      return;
    }
    async function refreshDirectory() {
      try {
        const data = await liveDirectory();
        if (!mounted.current || directoryVersion.current !== version) return;
        liveSeen.current = true; setMembers(data); setDirectorySource('live');
        await saveDirectory(data).then(() => { hasDirectoryCache.current = true; }).catch(() => setError('Directory loaded; device cache storage is unavailable.'));
      } catch (e) {
        if (!mounted.current || directoryVersion.current !== version) return;
        reportFailure(e); setError(`${errorMessage(e, API_URL)} Showing the saved or bundled directory.`);
      }
    }
    void refreshDirectory();
  }, [backend.status, backend.checkedAt, reportFailure]);
  async function ask() {
    if (!validQuestion(question)) { setError('Enter a question between 1 and 500 characters.'); return; }
    if (askController.current) return;
    const controller = new AbortController(); askController.current = controller;
    setBusy(true); setError('');
    try {
      let answer: Result; let source: Source;
      try {
        if (device.isConnected === false) throw new ApiError('offline', 'The device has no network connection.');
        answer = await request<Result>('/ask', { question: question.trim() }, { signal: controller.signal });
        if (!answer || typeof answer.matched !== 'boolean' || typeof answer.introduction !== 'string' || typeof answer.reason !== 'string'
          || !Array.isArray(answer.evidenceLinks) || !answer.evidenceLinks.every(v => typeof v === 'string')
          || !Number.isFinite(answer.confidence) || (answer.matched && (!answer.member?.id || !answer.member.fullName))) {
          throw new ApiError('response', 'The API returned an invalid search result.');
        }
        source = 'live'; void checkBackend();
      } catch (e) {
        if (controller.signal.aborted || e instanceof ApiError && e.kind === 'cancelled') {
          if (mounted.current) setError('Search canceled. Your last useful result is retained.');
          return;
        }
        reportFailure(e);
        setError(`${errorMessage(e, API_URL)} Using local lookup; you can retry.`);
        answer = localSearch(question, members); source = liveSeen.current || hasDirectoryCache.current ? 'offline cached' : 'offline bundled';
      }
      if (!mounted.current || controller.signal.aborted) return;
      setResult(answer); setResultSource(source);
      if (answer.matched) {
        setLastUseful({ question, result: answer });
        await saveResult(question, answer).catch(() => { if (mounted.current) setError('Result displayed; device cache could not be saved.'); });
      }
      if (mounted.current && !controller.signal.aborted) {
        askController.current = null; go('AI Result');
      }
    } finally {
      if (askController.current === controller) askController.current = null;
      if (mounted.current) setBusy(false);
    }
  }
  async function select(member: Member) {
    go('Member Profile');
    const selection = ++selectionVersion.current;
    const cached = cachedProfile.current?.id === member.id ? cachedProfile.current : null;
    const fallback = directorySource === 'live' ? member : cached ?? member;
    setProfile(fallback); setProfileSource(directorySource === 'live' ? 'live' : cached ? 'cached' : directorySource); setError('');
    if (device.isConnected !== false) {
      try {
        const live = await request<Member>(`/members/${encodeURIComponent(member.id)}`);
        if (!isMember(live) || live.id !== member.id) throw new ApiError('response', 'The API returned an invalid profile.');
        if (!mounted.current || selection !== selectionVersion.current) return;
        setProfile(live); setProfileSource('live'); cachedProfile.current = live;
        await saveProfile(live).catch(() => setError('Profile displayed; device cache could not be saved.'));
        return;
      } catch (e) {
        if (!mounted.current || selection !== selectionVersion.current) return;
        reportFailure(e); setError(`${errorMessage(e, API_URL)} Showing saved or bundled profile facts.`);
        setProfileSource(cached ? 'offline cached' : directorySource === 'live' ? 'offline cached' : directorySource);
      }
    }
    await saveProfile(fallback).catch(() => undefined);
  }
  async function inspectModel() {
    setModelBusy(true); setError('');
    try {
      if (!await checkBackend()) return;
      const info = await request<Record<string, unknown>>('/model-info');
      if (mounted.current) setModel(info);
    } catch (e) { if (mounted.current) { reportFailure(e); setError(errorMessage(e, API_URL)); } }
    finally { if (mounted.current) setModelBusy(false); }
  }
  return <SafeAreaView style={s.safe}><StatusBar style="dark" />
    <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={s.content}>
      <View style={s.masthead}><View style={s.logo}><Text style={s.logoText}>AS</Text></View><View style={s.grow}>
        <Text style={s.brand}>AGRISOKO POCKET</Text><Text style={s.caption}>Group G13 | Version 1.0.0</Text>
      </View>{history.length > 0 && <Button secondary title="Back" onPress={back} />}</View>
      <Text accessibilityRole="header" style={s.title}>{screen}</Text>
      <View style={s.statusPanel}>
        <Text style={s.statusText}>{deviceLabel(device)}</Text>
        <Text accessibilityLiveRegion="polite" style={[s.statusText, backend.status === 'reachable' ? s.healthy : s.muted]}>{backendLabel(backend)}</Text>
      </View>
      {!!error && <View style={s.notice}><Text accessibilityRole="alert" accessibilityLiveRegion="polite" style={s.error}>{error}</Text></View>}
      {screen === 'Home' && <>
        <View style={s.heroCard}><Text style={s.eyebrow}>PEOPLE. KNOWLEDGE. EVIDENCE.</Text><Text style={s.hero}>Know the team.{ '\n' }Find the right person.</Text>
          <Text style={s.heroBody}>Explore the people behind AgriSoko and find supplied member facts with transparent team search.</Text>
          <View style={s.actions}><Button title="Ask the Team" onPress={() => go('Ask the Team')} /><Button secondary title="Browse members" onPress={() => go('Member Directory')} /></View>
        </View>
        <View style={s.stats}><View style={s.stat}><Text style={s.statNumber}>04</Text><Text style={s.caption}>Team members</Text></View><View style={s.stat}><Text style={s.statNumber}>G13</Text><Text style={s.caption}>INES Ruhengeri</Text></View><View style={s.stat}><Text style={s.statNumber}>Local</Text><Text style={s.caption}>Offline lookup</Text></View></View>
        <Section title="Built for team discovery"><Text style={s.body}>A team directory for classmates, assessors and group members in the Integrated Mobile and Artificial Intelligence assignment.</Text><Text style={s.muted}>All four profiles await individual approval. Unknown facts and agricultural outcomes remain pending verification.</Text></Section>
        <Section title="API availability"><Text style={s.body}>{backendLabel(backend)}</Text>{backend.message && <Text style={s.muted}>{backend.message}</Text>}
          <Button secondary disabled={backend.status === 'checking'} title="Check API health" onPress={() => void checkBackend()} />
        </Section>
        {lastUseful && <Button secondary title="Open last useful result (cached)" onPress={() => { setQuestion(lastUseful.question); setResult(lastUseful.result); setResultSource('cached'); go('AI Result'); }} />}
      </>}
      {screen === 'Ask the Team' && <>
        <Section title="Who would you like to find?"><Text style={s.body}>Search by full name, declared alias or role. Online TF-IDF also searches approved skills and features.</Text>
          <Text accessibilityLabel="Question label" style={s.fieldLabel}>YOUR QUESTION</Text><TextInput accessibilityLabel="Question about a team member" placeholder="Who is NZAYISENGA Erneste?" placeholderTextColor="#64766b" multiline value={question} onChangeText={setQuestion} style={s.input} maxLength={501} editable={!busy} />
          <Text style={s.counter}>{question.length}/500 characters</Text><View style={s.actions}><Button title={busy ? 'Searching...' : 'Search team'} disabled={busy} onPress={() => void ask()} />
            {busy && <Button secondary title="Cancel search" onPress={() => askController.current?.abort()} />}</View>
          {busy && <ActivityIndicator accessibilityLabel="Searching team profiles" color="#196344" />}
        </Section>
        <Section title="Available without the API"><Text style={s.muted}>Bundled or cached lookup supports exact names, declared aliases and roles. It does not run TF-IDF on your phone.</Text><Button secondary title="Use member directory" onPress={() => go('Member Directory')} /></Section>
      </>}
      {screen === 'AI Result' && <>
        {result ? <><Section title={result.matched ? 'Team member found' : 'No match found'}><Text style={s.tag}>Source: {resultSource}</Text>
          {result.member && <Text style={s.memberName}>{result.member.fullName}</Text>}
          <Text style={s.body}>{resultSource === 'live' ? `Match score: ${(result.confidence * 100).toFixed(1)}%` : 'Exact local lookup or a saved result'}</Text>
          <Text style={s.muted}>Retrieval scores are not probabilities or proof of contribution.</Text><Text style={s.body}>{result.reason}</Text>
          {!!result.introduction && <Text style={s.body}>{result.introduction}</Text>}
          {result.member && <Button title="View member profile" onPress={() => { const member = members.find(m => m.id === result.member?.id); if (member) void select(member); }} />}
        </Section><Section title="Evidence"><Evidence links={result.evidenceLinks} /></Section></> : <Text style={s.body}>Ask a question to see a result.</Text>}
        <View style={s.actions}><Button disabled={busy || !validQuestion(question)} title="Retry question" onPress={() => void ask()} /><Button secondary title="Browse directory" onPress={() => go('Member Directory')} /></View>
      </>}
      {screen === 'Member Directory' && <>
        <View style={s.sectionHeading}><Text style={s.muted}>Four confirmed roster members</Text><Text style={s.tag}>{directorySource}</Text></View>
        {members.map((member, index) => <View style={s.memberCard} key={member.id}><View style={s.memberHeading}><View style={s.avatar}><Text style={s.avatarText}>{String(index + 1).padStart(2, '0')}</Text></View><View style={s.grow}>
          <Text style={s.directoryName}>{member.fullName}</Text><Text style={s.muted}>{member.role || 'Role pending verification'}</Text></View></View>
          <View style={s.sectionHeading}><Text style={s.caption}>{member.approvalStatus === 'approved' ? 'Profile approved' : 'Profile pending verification'}</Text><Button secondary title="View profile" onPress={() => void select(member)} /></View>
        </View>)}<Button secondary disabled={backend.status === 'checking'} title="Check API and refresh" onPress={() => void checkBackend()} />
      </>}
      {screen === 'Member Profile' && profile && <>
        <Section title="Member overview"><Text style={s.tag}>Source: {profileSource}</Text><Text style={s.memberName}>{profile.fullName}</Text><Text style={s.muted}>{profile.approvalStatus === 'approved' ? 'Profile approved' : 'Profile pending individual verification. Supplied roster facts are shown; technical claims await approval.'}</Text></Section>
        <Section title="Identity and project profile">{profileFields.map(([key, label]) => {
          const allowed = profile.approvalStatus === 'approved' || ['registrationNumber', 'githubUsername', 'role'].includes(key);
          const value = profile[key];
          return <Field key={key} label={label} value={allowed ? Array.isArray(value) ? value.join(', ') : value : PENDING} />;
        })}</Section><Section title="Verified evidence"><Evidence links={profile.approvalStatus === 'approved' ? profile.evidenceLinks : []} /></Section>
      </>}
      {screen === 'About and Evidence' && <>
        <Section title="Project information"><Field label="Application" value="AgriSoko Pocket G13" /><Field label="Assignment" value="INES Ruhengeri | Integrated Mobile and Artificial Intelligence" /><Field label="Group / version" value="G13 / 1.0.0" /></Section>
        <Section title="Group members">{roster.map(m => <Field key={m.id} label={m.role || 'Group member'} value={`${m.fullName}${m.registrationNumber ? ` | ${m.registrationNumber}` : ''}`} />)}<Text style={s.muted}>Roster names are confirmed. Unknown registrations, accounts and individual technical contributions remain pending verification.</Text></Section>
        <Section title="AI matching approach"><Text style={s.body}>Deterministic TF-IDF word unigrams and bigrams with cosine similarity. Exact identifiers take precedence. The default confidence threshold is 0.45.</Text><Text style={s.muted}>Only supplied roster facts and approved technical fields are used. No generative model produces member facts.</Text></Section>
        <Section title="Offline support"><Text style={s.body}>A bundled four-member directory, cached profiles and the last useful result remain available without the API.</Text><Text style={s.muted}>Offline search supports exact names, declared aliases, identifiers and roles. TF-IDF similarity requires the backend.</Text></Section>
        <Section title="API status"><Field label="Configured endpoint" value={API_URL || 'Not configured'} /><Field label="Device network" value={deviceLabel(device)} /><Field label="Backend" value={backendLabel(backend)} />
          {backend.checkedAt && <Field label="Last successful health check" value={new Date(backend.checkedAt).toLocaleTimeString()} />}
          {backend.message && <Text style={s.error}>{backend.message}</Text>}
          {isPrivateApi(API_URL) && <Text style={s.muted}>This API uses a private LAN address. Your phone needs a route to the computer, usually the same Wi-Fi or a suitable VPN. Mobile data alone is not proof of access.</Text>}
          <View style={s.actions}><Button secondary disabled={backend.status === 'checking'} title="Check API health" onPress={() => void checkBackend()} /><Button secondary disabled={modelBusy} title={modelBusy ? 'Reading model...' : 'Read model details'} onPress={() => void inspectModel()} /></View>
          {model && <View style={s.modelDetails}><Field label="Vectorizer" value={typeof model.vectorizerType === 'string' ? model.vectorizerType : null} /><Field label="Threshold" value={typeof model.confidenceThreshold === 'number' ? String(model.confidenceThreshold) : null} /><Field label="Dataset fingerprint" value={typeof model.datasetFingerprint === 'string' ? model.datasetFingerprint : null} /><Field label="Build commit" value={typeof model.buildCommit === 'string' ? model.buildCommit : null} />{Array.isArray(model.limitations) && model.limitations.filter(v => typeof v === 'string').map((v, i) => <Text style={s.muted} key={i}>{v}</Text>)}</View>}
        </Section>
        <Section title="GitHub evidence"><Field label="Required repository" value="agrisoko-pocket-g13" /><Text style={s.muted}>Verified repository, release, member issue, PR and peer-review links have not been supplied in the app. No collaboration evidence is inferred.</Text></Section>
        <Section title="Limitations"><Text style={s.body}>Sparse, pending profiles limit role, skill and feature results. Agricultural users, features and outcome metrics still need verified facts.</Text><Text style={s.muted}>The project owner reports that an APK installed and launched on a physical Android phone. API reachability and this revised interface still require device verification. Member approvals and genuine feedback remain pending.</Text></Section>
      </>}
      <View style={s.footerNav}>{(['Home', 'Ask the Team', 'Member Directory', 'About and Evidence'] as Screen[]).map((next, i) =>
        <Pressable key={next} accessibilityRole="button" accessibilityState={{ selected: next === screen }} onPress={() => go(next)} style={[s.navItem, next === screen && s.navSelected]}><Text style={[s.navText, next === screen && s.navSelectedText]}>{['Home', 'Ask', 'Team', 'About'][i]}</Text></Pressable>)}</View>
    </ScrollView>
  </SafeAreaView>;
}
const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#f2f6f0' }, content: { padding: 18, paddingBottom: 24, width: '100%', maxWidth: 760, alignSelf: 'center' },
  masthead: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 16 }, logo: { width: 42, height: 42, borderRadius: 12, backgroundColor: '#196344', alignItems: 'center', justifyContent: 'center' }, logoText: { fontSize: 17, fontWeight: '800', color: '#fff' },
  grow: { flex: 1, minWidth: 0 }, brand: { color: '#194a34', fontWeight: '800', letterSpacing: 1.4, fontSize: 13 }, caption: { fontSize: 12, color: '#53685b', lineHeight: 18 },
  title: { fontSize: 27, lineHeight: 34, fontWeight: '800', color: '#173c2a', marginBottom: 12 }, statusPanel: { backgroundColor: '#e5eee3', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 9, gap: 3, marginBottom: 14 }, statusText: { fontSize: 12, lineHeight: 18, color: '#354f3f' }, healthy: { color: '#145330', fontWeight: '700' },
  heroCard: { backgroundColor: '#174c34', borderRadius: 18, padding: 20, marginBottom: 14 }, eyebrow: { color: '#c5de9f', fontSize: 11, letterSpacing: 1, fontWeight: '700' }, hero: { fontSize: 29, lineHeight: 36, fontWeight: '800', color: '#fff', marginVertical: 12 }, heroBody: { fontSize: 15, lineHeight: 23, color: '#e5eee3', marginBottom: 10 },
  stats: { flexDirection: 'row', borderRadius: 12, backgroundColor: '#fff', paddingVertical: 12, marginBottom: 14, borderWidth: 1, borderColor: '#dfe8dc' }, stat: { flex: 1, alignItems: 'center', paddingHorizontal: 4 }, statNumber: { fontSize: 21, fontWeight: '800', color: '#1b5d3e', marginBottom: 2 },
  card: { backgroundColor: '#fff', borderRadius: 14, padding: 16, borderWidth: 1, borderColor: '#dfe8dc', marginBottom: 12 }, sectionTitle: { fontSize: 17, fontWeight: '700', color: '#173c2a', marginBottom: 10 }, body: { fontSize: 15, lineHeight: 23, color: '#2b4435', marginBottom: 9 }, muted: { fontSize: 13, lineHeight: 20, color: '#53685b' },
  actions: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginTop: 6 }, button: { alignSelf: 'flex-start', backgroundColor: '#196344', paddingHorizontal: 15, paddingVertical: 10, minHeight: 48, borderRadius: 9, justifyContent: 'center', maxWidth: '100%', marginVertical: 3, borderWidth: 1, borderColor: '#196344' }, buttonText: { color: '#fff', fontSize: 14, fontWeight: '700', lineHeight: 20 }, secondaryButton: { backgroundColor: '#edf4e9', borderColor: '#cedfc8' }, secondaryButtonText: { color: '#174c34' }, dim: { opacity: .55 },
  notice: { backgroundColor: '#fff3e3', borderColor: '#e6caa1', borderWidth: 1, padding: 12, borderRadius: 10, marginBottom: 12 }, error: { color: '#7c3b16', fontSize: 13, lineHeight: 20 },
  field: { paddingVertical: 9, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: '#e2e9df' }, fieldLabel: { fontSize: 11, lineHeight: 17, color: '#53685b', fontWeight: '700', marginBottom: 3 }, fieldValue: { fontSize: 15, lineHeight: 22, color: '#213e2c', flexShrink: 1 },
  input: { backgroundColor: '#f7f9f5', borderColor: '#a9bfaa', borderWidth: 1, borderRadius: 10, minHeight: 100, textAlignVertical: 'top', padding: 12, fontSize: 16, lineHeight: 23, color: '#173c2a', marginTop: 4 }, counter: { fontSize: 12, color: '#53685b', textAlign: 'right', marginTop: 5 },
  sectionHeading: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 8, marginBottom: 8 }, tag: { fontSize: 11, lineHeight: 18, color: '#315d3e', backgroundColor: '#edf4e9', borderRadius: 6, paddingHorizontal: 7, paddingVertical: 3, alignSelf: 'flex-start', marginBottom: 6 }, memberName: { fontSize: 23, lineHeight: 30, fontWeight: '800', color: '#173c2a', marginBottom: 10 },
  memberCard: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#dfe8dc', borderRadius: 14, padding: 14, marginBottom: 10 }, memberHeading: { flexDirection: 'row', gap: 12, alignItems: 'center', marginBottom: 8 }, avatar: { width: 42, height: 42, borderRadius: 12, backgroundColor: '#e4eedc', justifyContent: 'center', alignItems: 'center' }, avatarText: { color: '#315d3e', fontSize: 14, fontWeight: '800' }, directoryName: { fontSize: 16, lineHeight: 23, fontWeight: '700', color: '#173c2a' }, modelDetails: { marginTop: 10 },
  footerNav: { flexDirection: 'row', gap: 4, padding: 5, backgroundColor: '#fff', borderWidth: 1, borderColor: '#dfe8dc', borderRadius: 12, marginTop: 12 }, navItem: { flex: 1, minHeight: 48, paddingVertical: 12, paddingHorizontal: 3, alignItems: 'center', justifyContent: 'center', borderRadius: 8 }, navSelected: { backgroundColor: '#e5eee3' }, navText: { color: '#53685b', fontSize: 13, fontWeight: '600' }, navSelectedText: { color: '#174c34', fontWeight: '800' },
});
