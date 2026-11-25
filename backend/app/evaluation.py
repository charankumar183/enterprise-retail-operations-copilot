import json,time
from pathlib import Path
from .config import settings
from .rag import retrieve

def measure_retrieval(questions):
    samples=[]
    for item in questions:
        now=time.perf_counter()
        r=retrieve(item['question'],top_k=5)
        got={s['document_name'] for s in r};want=set(item['expected_documents'])
        hits=len(got & want)
        samples.append({'question':item['question'],'precision_at_5':round(hits/max(len(got),1),3),'recall_at_5':round(hits/max(len(want),1),3),'latency_ms':round((time.perf_counter()-now)*1000,2),'expected_documents':list(want),'retrieved_documents':list(got)})
    return {'evaluated_questions':len(samples),'precision_at_5':round(sum(x['precision_at_5'] for x in samples)/max(len(samples),1),3),'recall_at_5':round(sum(x['recall_at_5'] for x in samples)/max(len(samples),1),3),'mean_latency_ms':round(sum(x['latency_ms'] for x in samples)/max(len(samples),1),2),'questions':samples,'answer_accuracy':None,'hallucination_rate':None,'note':'Answer accuracy and hallucination rate require labeled human/LLM assessment; never extrapolate from retrieval metrics.'}
