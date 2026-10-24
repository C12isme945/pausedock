"""Small disclosed synthetic sanity check, not an independent benchmark."""
import json,time
from datetime import datetime,timezone
from pathlib import Path
from core import classify

root=Path(__file__).resolve().parent
cases=json.loads((root/'evidence/eval_cases.json').read_text())
results=[]
for case in cases:
    text='\n'.join(n['text'] for n in case['notes'])
    start=time.monotonic()
    try:
        card=classify(text)
        actual={n['id']:n['bucket'] for n in card['notes']}
        rows=[]
        for i,n in enumerate(case['notes']):
            identity=f'N{i+1}'
            # Deliberately weak keyword baseline reveals negation/dependency limitations.
            t=n['text'].lower()
            baseline='done' if any(w in t for w in ['done','finished','already']) else ('waiting' if 'waiting' in t else ('next' if any(w in t for w in ['need','next:']) else 'context'))
            rows.append({'id':identity,'input':n['text'],'expected_editor_label':n['expected'],
                         'model_label':actual[identity],'keyword_baseline':baseline,
                         'model_agrees':actual[identity]==n['expected'],'baseline_agrees':baseline==n['expected']})
        result={'case':case['name'],'status':'SUCCESS','elapsed_seconds':round(time.monotonic()-start,2),
                'restart_id':card['restart_id'],'run':card['run'],'rows':rows,'wording_preserved':all(n['text']==original['text'] for n,original in zip(card['notes'],case['notes']))}
    except Exception as exc:
        result={'case':case['name'],'status':'FAILED','error':str(exc),'elapsed_seconds':round(time.monotonic()-start,2)}
    results.append(result)
    (root/'evidence/evaluation.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'16 hand-authored synthetic notes. Garden example informed prompt refinement; cases are not an independent test set. Labels are editorial judgments.','results':results},indent=2),encoding='utf-8')
    print(json.dumps(result),flush=True)
