"""Evaluate the real sparse roster; no synthetic facts are added to member data."""
import json
from pathlib import Path
from matching import MemberIndex, load_members

def main():
    index = MemberIndex.build(load_members())
    cases = []
    for m in index.members:
        for q in (m['fullName'], f"Who is {m['fullName']}?", f"Tell me about {m['fullName']}"):
            cases.append((q, m['id']))
    for q in ('weather forecast Kigali', 'quantum gravity', 'pizza delivery', 'football scores', 'book a flight'):
        cases.append((q, None))
    rows = []
    for question, expected in cases:
        result = index.search(question)
        actual = result['member']['id'] if result['matched'] else None
        rows.append({'question': question, 'expected': expected, 'actual': actual, 'correct': expected == actual, 'score': result['confidence']})
    positive = [r for r in rows if r['expected']]
    negative = [r for r in rows if not r['expected']]
    report = {'datasetFingerprint': index.fingerprint, 'threshold': index.threshold,
        'top1': {'correct': sum(r['correct'] for r in positive), 'total': len(positive)},
        'noMatchRejection': {'correct': sum(r['correct'] for r in negative), 'total': len(negative)},
        'limitations': '12 identity paraphrases only: all technical profiles and aliases are pending. This does not measure skill/feature generalization. Synthetic approved fixtures cover those mechanics separately.',
        'errors': [r for r in rows if not r['correct']], 'queries': rows}
    for key in ('top1','noMatchRejection'):
        report[key]['accuracy'] = report[key]['correct'] / report[key]['total']
    path = Path(__file__).resolve().parents[1] / 'docs' / 'AI_EVALUATION.json'
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'queries'}, indent=2))
if __name__ == '__main__': main()
