"""Generate plainly labelled PDF drafts without requiring a document service."""
from pathlib import Path
import textwrap
ROOT = Path(__file__).resolve().parents[1]

def pdf(source, target):
    lines=[]
    for line in source.splitlines():
        lines.extend(textwrap.wrap(line, width=94, replace_whitespace=False) or [''])
    pages=[lines[i:i+49] for i in range(0,len(lines),49)]
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>', b'', b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids=[]
    for n, lines in enumerate(pages,1):
        page_id=len(objects)+1; stream_id=page_id+1; kids.append(f'{page_id} 0 R')
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {stream_id} 0 R >>'.encode())
        text=['BT /F1 10 Tf 13 TL 40 802 Td']
        for line in lines:
            line=line.encode('cp1252',errors='replace').decode('cp1252').replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
            text.append(f'({line}) Tj T*')
        text.extend(['ET', f'BT /F1 9 Tf 40 25 Td (DRAFT - pending evidence / page {n} of {len(pages)}) Tj ET'])
        stream='\n'.join(text).encode('cp1252')
        objects.append(f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream')
    objects[1]=f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(kids)} >>'.encode()
    output=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'); offsets=[0]
    for i,obj in enumerate(objects,1):
        offsets.append(len(output));output.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
    xref=len(output);output.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:output.extend(f'{offset:010d} 00000 n \n'.encode())
    output.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    target.write_bytes(output)

if __name__=='__main__':
    for source,target in [('docs/REPORT_DRAFT.md','docs/COMBO_A3_G13_REPORT.pdf'),('evidence/CONTRIBUTIONS_DRAFT.md','evidence/CONTRIBUTIONS.pdf'),('evidence/TEST_LOG_DRAFT.md','evidence/TEST_LOG.pdf'),('evidence/FEEDBACK_DRAFT.md','evidence/FEEDBACK.pdf')]:
        pdf((ROOT/source).read_text(encoding='utf-8'),ROOT/target)
        print(target)
