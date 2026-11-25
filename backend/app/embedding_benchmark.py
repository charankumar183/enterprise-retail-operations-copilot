"""Compare two embedding models on the same fixed sample documents and questions."""
import json,time,csv
from pathlib import Path
from collections import defaultdict
from .config import settings
from .rag import get_embedder,text_pages,make_chunks

def benchmark():
    root=Path(settings.data_dir)
    questions=json.loads((root/'evaluation'/'test_questions.json').read_text())
    corpus=[];names=[]
    for p in sorted((root/'sample_documents').iterdir()):
        if p.suffix.lower() not in {'.pdf','.docx','.txt','.csv','.xlsx','.xls'}:continue
        for c in make_chunks(text_pages(p)):
            corpus.append(c['child']);names.append(p.name)
    if not corpus:raise ValueError('No test corpus')
    from sentence_transformers import util
    output=[]
    for model_name in [settings.embedding_model,settings.comparison_embedding_model]:
        t=time.perf_counter();model=get_embedder(model_name)
        docs=model.encode(corpus,normalize_embeddings=True,convert_to_tensor=True)
        qry=model.encode([q['question'] for q in questions],normalize_embeddings=True,convert_to_tensor=True)
        sims=util.cos_sim(qry,docs)
        precisions=[];recalls=[]
        for row,q in zip(sims,questions):
            ranked=list(dict.fromkeys(names[int(i)] for i in row.argsort(descending=True).tolist()))[:5]
            target=set(q['expected_documents']);hits=len(set(ranked)&target)
            precisions.append(hits/max(1,len(ranked)));recalls.append(hits/max(1,len(target)))
        output.append({'model':model_name,'precision_at_5':round(sum(precisions)/len(precisions),3),'recall_at_5':round(sum(recalls)/len(recalls),3),'elapsed_s':round(time.perf_counter()-t,2),'queries':len(questions),'chunks':len(corpus)})
    outdir=Path(settings.reports_dir);outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'embedding_comparison.json').write_text(json.dumps(output,indent=2))
    with (outdir/'embedding_comparison.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=output[0].keys());writer.writeheader();writer.writerows(output)
    return output

if __name__=='__main__':print(json.dumps(benchmark(),indent=2))
