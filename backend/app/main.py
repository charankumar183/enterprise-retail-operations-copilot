import os,time,uuid,hashlib,shutil,traceback,threading,json
from pathlib import Path
from datetime import datetime,timezone
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File,Form,Query,BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from sqlalchemy import select,func,desc
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db,init_db,SessionLocal
from .models import User,Product,Inventory,Warehouse,Store,Supplier,Document,ChatMessage,Report,AuditLog,Feedback,PurchaseOrder
from .auth import current_user,allowed,hash_password,verify_password,make_token,ROLES
from .seed import seed
from .analytics import dashboard,route_intent,analyze
from .rag import retrieve,index_document,delete_document_index,compose_answer
from .reporting import make_pdf
from .evaluation import measure_retrieval

index_status={'state':'not_started','indexed':0,'errors':[]}

def audit(db,user,action,details='',elapsed=None):
    db.add(AuditLog(user_id=user.id if user else None,action=action,details=str(details)[:3500],duration_ms=elapsed))
    db.commit()

def doc_out(d):
    return {'id':d.id,'name':d.name,'doc_type':d.doc_type,'department':d.department,'region':d.region,'version':d.version,'product_category':d.product_category,'store':d.store_code,'warehouse':d.warehouse_code,'supplier':d.supplier_code,'promotion_campaign':d.promotion_campaign,'effective_date':d.effective_date,'indexed':d.indexed,'created_at':d.created_at.isoformat() if d.created_at else None}

def ingest_samples():
    global index_status
    index_status={'state':'running','indexed':0,'errors':[]}
    data_dir=Path(settings.data_dir)/'sample_documents'
    if not data_dir.exists():index_status['state']='missing_sample_data';return
    with SessionLocal() as db:
        for path in sorted(data_dir.iterdir()):
            if path.suffix.lower() not in {'.pdf','.docx','.txt','.csv','.xlsx','.xls'}:continue
            checksum=hashlib.sha256(path.read_bytes()).hexdigest()
            existing=db.scalar(select(Document).where(Document.file_hash==checksum))
            if existing and existing.indexed:continue
            d=existing or Document(name=path.name,path=str(path),doc_type=path.suffix[1:].upper(),department=guess_department(path.name),region='All',version=guess_version(path.name),file_hash=checksum,indexed=False)
            if not existing:db.add(d);db.commit();db.refresh(d)
            try:
                index_document(d);d.indexed=True;db.commit();index_status['indexed']+=1
            except Exception as e:
                d.indexed=False;db.commit();index_status['errors'].append(f'{path.name}: {str(e)[:260]}')
                # If model is unavailable, avoid repeating the same failed download for every document.
                if 'model' in str(e).lower() or 'connect' in str(e).lower():break
    index_status['state']='completed' if not index_status['errors'] else 'completed_with_errors'

def guess_department(name):
    name=name.lower()
    for key,val in [('warehouse','Warehouse'),('inventory','Inventory'),('vendor','Procurement'),('procurement','Procurement'),('pricing','Pricing'),('promotion','Marketing'),('customer','Customer Service'),('logistic','Logistics'),('merchandis','Merchandising'),('supply','Supply Chain')]:
        if key in name:return val
    return 'Operations'

def guess_version(name):
    import re
    m=re.search(r'[vV](\d+)',name)
    return m.group(1) if m else '1'

@asynccontextmanager
async def lifespan(app):
    for attempt in range(20):
        try:
            init_db()
            with SessionLocal() as db:seed(db)
            break
        except Exception:
            if attempt==19:raise
            time.sleep(2)
    if os.environ.get('AUTO_INDEX_SAMPLES','true').lower()=='true':
        threading.Thread(target=ingest_samples,daemon=True,name='sample-indexer').start()
    yield

app=FastAPI(title='Enterprise AI Retail Operations Copilot',version='1.0.0',description='Retail SQL Analytics + Advanced RAG + Agentic Router. Synthetic demonstration data.')
app.router.lifespan_context=lifespan
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(',')],allow_methods=['*'],allow_headers=['*'])

class Login(BaseModel): email:str; password:str
class Register(BaseModel):email:str; password:str=Field(min_length=10);role:str='Store Manager'
class ChatRequest(BaseModel):question:str=Field(min_length=2,max_length=2500);session_id:Optional[str]=None;filters:dict[str,str]={}
class ReportRequest(BaseModel): title:str='Retail Operations Report';question:str='Generate a daily operations report for Store 105';kind:str='operations'
class FeedbackRequest(BaseModel):question:str;rating:int=Field(ge=1,le=5);comment:str=''
class UserRoleChange(BaseModel):role:str
class DocumentMetadataUpdate(BaseModel):
    department:Optional[str]=None
    region:Optional[str]=None
    version:Optional[str]=None
    product_category:Optional[str]=None
    store:Optional[str]=None
    warehouse:Optional[str]=None
    supplier:Optional[str]=None
    promotion_campaign:Optional[str]=None
    effective_date:Optional[str]=None

@app.get('/health')
def health():return {'status':'ok','mode':'llm' if settings.openai_api_key else 'extractive/sql','indexing':index_status}

@app.post('/api/auth/login')
def login(payload:Login,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==payload.email))
    if not user or not verify_password(payload.password,user.password_hash) or not user.active:
        audit(db,None,'login_failed',payload.email);raise HTTPException(401,'Invalid credentials')
    token=make_token(user);audit(db,user,'login')
    return {'access_token':token,'token_type':'bearer','user':{'id':user.id,'email':user.email,'role':user.role}}

@app.get('/api/auth/me')
def me(user:User=Depends(current_user)):
    return {'id':user.id,'email':user.email,'role':user.role}

@app.post('/api/auth/register')
def register(payload:Register,db:Session=Depends(get_db),admin:User=Depends(allowed('Administrator'))):
    if payload.role not in ROLES:raise HTTPException(400,'Unknown role')
    if db.scalar(select(User.id).where(User.email==payload.email)):raise HTTPException(409,'Email already exists')
    u=User(email=payload.email,role=payload.role,password_hash=hash_password(payload.password));db.add(u);db.commit();db.refresh(u)
    audit(db,admin,'create_user',u.email)
    return {'id':u.id,'email':u.email,'role':u.role}

@app.get('/api/dashboard')
def get_dashboard(db:Session=Depends(get_db),user:User=Depends(current_user)):
    result=dashboard(db);result['indexed_documents']=db.scalar(select(func.count(Document.id)).where(Document.indexed==True)) or 0
    result['total_documents']=db.scalar(select(func.count(Document.id))) or 0
    result['reports']=db.scalar(select(func.count(Report.id))) or 0
    result['indexing']=index_status
    return result

@app.get('/api/products')
def products(q:str='',limit:int=Query(30,ge=1,le=100),db:Session=Depends(get_db),user:User=Depends(current_user)):
    stmt=select(Product,Supplier.name).outerjoin(Supplier,Product.supplier_id==Supplier.id)
    if q:stmt=stmt.where(Product.name.ilike(f'%{q}%')|Product.sku.ilike(f'%{q}%')|Product.category.ilike(f'%{q}%'))
    return [{'sku':p.sku,'name':p.name,'category':p.category,'price':p.price,'supplier':name} for p,name in db.execute(stmt.limit(limit))]

@app.get('/api/inventory')
def inventory(q:str='',low_only:bool=False,limit:int=Query(100,ge=1,le=400),db:Session=Depends(get_db),user:User=Depends(current_user)):
    stmt=select(Product.sku,Product.name,Inventory.quantity,Inventory.reorder_point,Warehouse.code,Store.code).join(Product,Inventory.product_id==Product.id).outerjoin(Warehouse,Warehouse.id==Inventory.warehouse_id).outerjoin(Store,Store.id==Inventory.store_id)
    if q:stmt=stmt.where(Product.sku.ilike(f'%{q}%')|Product.name.ilike(f'%{q}%'))
    if low_only:stmt=stmt.where(Inventory.quantity<Inventory.reorder_point)
    return [{'sku':sku,'name':name,'quantity':qty,'reorder_point':rp,'location':wh or f'Store {st}','low_stock':qty<rp} for sku,name,qty,rp,wh,st in db.execute(stmt.limit(limit))]

@app.get('/api/documents')
def documents(db:Session=Depends(get_db),user:User=Depends(current_user)):
    return [doc_out(d) for d in db.scalars(select(Document).order_by(desc(Document.created_at))).all()]

@app.get('/api/documents/indexing-status')
def indexing_status(user:User=Depends(current_user)):return index_status

@app.post('/api/documents/index-samples')
def index_samples(background:BackgroundTasks,user:User=Depends(allowed('Administrator'))):
    if index_status['state']=='running':return {'message':'Indexing already in progress','status':index_status}
    background.add_task(ingest_samples)
    return {'message':'Sample indexing requested','status':index_status}

@app.post('/api/documents/upload')
async def upload_document(file:UploadFile=File(...),department:str=Form('Operations'),region:str=Form('All'),version:str=Form('1'),product_category:str=Form(''),store:str=Form(''),warehouse:str=Form(''),supplier:str=Form(''),promotion_campaign:str=Form(''),effective_date:str=Form(''),db:Session=Depends(get_db),user:User=Depends(allowed('Administrator','Procurement Manager'))):
    suffix=Path(file.filename or '').suffix.lower()
    if suffix not in {'.pdf','.docx','.txt','.csv','.xlsx','.xls'}:raise HTTPException(415,'Unsupported file type')
    data=await file.read((settings.max_upload_mb+1)*1024*1024)
    if len(data)>settings.max_upload_mb*1024*1024:raise HTTPException(413,'File too large')
    if not data:raise HTTPException(400,'Empty file')
    checksum=hashlib.sha256(data).hexdigest()
    duplicate=db.scalar(select(Document).where(Document.file_hash==checksum))
    if duplicate:raise HTTPException(409,f'Duplicate content: document #{duplicate.id}')
    safe_name=Path(file.filename or 'document').name
    path=Path(settings.uploads_dir)/(uuid.uuid4().hex+suffix);path.write_bytes(data)
    d=Document(name=safe_name,path=str(path),file_hash=checksum,doc_type=suffix[1:].upper(),department=department,region=region,version=version,product_category=product_category,store_code=store,warehouse_code=warehouse,supplier_code=supplier,promotion_campaign=promotion_campaign,effective_date=effective_date,indexed=False)
    db.add(d);db.commit();db.refresh(d)
    try:index_document(d);d.indexed=True;db.commit()
    except Exception as exc:
        audit(db,user,'document_index_failed',str(exc));raise HTTPException(503,f'File stored, but indexing failed: {str(exc)[:260]}')
    audit(db,user,'document_uploaded',f'{safe_name} id={d.id}')
    return doc_out(d)

@app.patch('/api/documents/{document_id}')
def update_document_metadata(document_id:int,body:DocumentMetadataUpdate,db:Session=Depends(get_db),user:User=Depends(allowed('Administrator','Procurement Manager'))):
    d=db.get(Document,document_id)
    if not d:raise HTTPException(404,'Document not found')
    fields={'department':'department','region':'region','version':'version','product_category':'product_category','store':'store_code','warehouse':'warehouse_code','supplier':'supplier_code','promotion_campaign':'promotion_campaign','effective_date':'effective_date'}
    for field,value in body.model_dump(exclude_none=True).items():
        if field in fields:setattr(d,fields[field],value)
    db.commit();index_document(d);d.indexed=True;db.commit();audit(db,user,'document_metadata_updated',d.name)
    return doc_out(d)

@app.put('/api/documents/{document_id}')
async def replace_document(document_id:int,file:UploadFile=File(...),version:str=Form('2'),db:Session=Depends(get_db),user:User=Depends(allowed('Administrator','Procurement Manager'))):
    d=db.get(Document,document_id)
    if not d:raise HTTPException(404,'Document not found')
    ext=Path(file.filename or '').suffix.lower()
    if ext not in {'.pdf','.docx','.txt','.csv','.xlsx','.xls'}:raise HTTPException(415,'Unsupported file type')
    data=await file.read((settings.max_upload_mb+1)*1024*1024)
    if not data or len(data)>settings.max_upload_mb*1024*1024:raise HTTPException(413,'Invalid upload size')
    previous=d.path
    new_path=Path(settings.uploads_dir)/(uuid.uuid4().hex+ext)
    new_path.write_bytes(data)
    d.path=str(new_path);d.name=Path(file.filename or 'document').name;d.version=version;d.doc_type=ext[1:].upper();d.file_hash=hashlib.sha256(data).hexdigest();d.indexed=False;db.commit()
    try:
        index_document(d);d.indexed=True;db.commit()
    except Exception as exc:
        d.path=previous;db.commit();new_path.unlink(missing_ok=True)
        raise HTTPException(503,f'Reindex failed, original retained: {exc}')
    previous_path=Path(previous)
    if previous_path.is_file() and Path(settings.uploads_dir) in previous_path.parents:previous_path.unlink()
    audit(db,user,'document_replaced',f'{document_id} v{version}')
    return doc_out(d)

@app.delete('/api/documents/{document_id}')
def delete_document(document_id:int,db:Session=Depends(get_db),user:User=Depends(allowed('Administrator'))):
    d=db.get(Document,document_id)
    if not d:raise HTTPException(404,'Document not found')
    delete_document_index(d.id)
    file_path=Path(d.path)
    # Sample files remain intact on disk so the bundled seed corpus can be restored.
    if file_path.is_file() and Path(settings.uploads_dir) in file_path.parents:file_path.unlink()
    name=d.name;db.delete(d);db.commit();audit(db,user,'document_deleted',name)
    return {'deleted':document_id}

@app.post('/api/documents/{document_id}/reindex')
def reindex_document(document_id:int,db:Session=Depends(get_db),user:User=Depends(allowed('Administrator','Procurement Manager'))):
    d=db.get(Document,document_id)
    if not d:raise HTTPException(404,'Document not found')
    chunks=index_document(d);d.indexed=True;db.commit();audit(db,user,'document_reindexed',f'{d.name}: {chunks} chunks')
    return {'document':doc_out(d),'chunks':chunks}

@app.get('/api/search/filters')
def filters(db:Session=Depends(get_db),user:User=Depends(current_user)):
    docs=db.scalars(select(Document)).all()
    return {k:sorted({getattr(d,k) for d in docs if getattr(d,k)}) for k in ('department','doc_type','region','version','product_category','store_code','warehouse_code','supplier_code','promotion_campaign','effective_date')}

@app.post('/api/search')
def search(body:ChatRequest,user:User=Depends(current_user),db:Session=Depends(get_db)):
    started=time.perf_counter()
    try:rows=retrieve(body.question,body.filters)
    except Exception as e:raise HTTPException(503,f'Retrieval unavailable: {str(e)[:250]}')
    audit(db,user,'rag_search',json.dumps({'query':body.question,'documents':[x['document_id'] for x in rows]}),round((time.perf_counter()-started)*1000,2))
    return {'sources':rows,'count':len(rows)}

@app.post('/api/agents/route')
def route(body:ChatRequest,user:User=Depends(current_user)):
    return {'intent':route_intent(body.question),'supported_paths':['rag','sql','report']}

@app.post('/api/chat')
def chat(body:ChatRequest,db:Session=Depends(get_db),user:User=Depends(current_user)):
    t=time.perf_counter();sid=body.session_id or uuid.uuid4().hex;intent=route_intent(body.question)
    history=[{'role':r,'content':c} for r,c in db.execute(select(ChatMessage.role,ChatMessage.content).where(ChatMessage.user_id==user.id,ChatMessage.session_id==sid).order_by(ChatMessage.id.desc()).limit(6))][::-1]
    sources=[];sql_data=None
    try:
        if intent=='sql':
            sql_data=analyze(db,body.question)
            # Rich narrative combines SQL records and procedures where relevant.
            if any(w in body.question.lower() for w in ['why','procedure','policy','replenishment']):
                try:sources=retrieve(body.question,body.filters,top_k=3)
                except Exception:sources=[]
        elif intent=='report':
            sql_data=analyze(db,body.question)
            sources=retrieve(body.question,body.filters,top_k=4)
        else:sources=retrieve(body.question,body.filters,top_k=6)
        if intent in ('sql','report') and sql_data is None and not sources:sources=retrieve(body.question,body.filters,top_k=5)
        answer,mode=compose_answer(body.question,sources,sql_data,history)
    except Exception as exc:
        audit(db,user,'chat_error',str(exc),round((time.perf_counter()-t)*1000,2))
        raise HTTPException(503,f'AI retrieval temporarily unavailable: {str(exc)[:220]}')
    db.add_all([ChatMessage(user_id=user.id,session_id=sid,role='user',content=body.question),ChatMessage(user_id=user.id,session_id=sid,role='assistant',content=answer)])
    db.commit();latency=round((time.perf_counter()-t)*1000,2)
    audit(db,user,'chat',json.dumps({'intent':intent,'query':body.question,'sql':str(sql_data)[:700],'sources':[x['document_name'] for x in sources],'mode':mode,'sql_query_type':intent}),latency)
    return {'session_id':sid,'answer':answer,'intent':intent,'mode':mode,'sources':[{k:v for k,v in s.items() if k!='context'} for s in sources],'sql_data':sql_data,'latency_ms':latency}

@app.get('/api/chat/history')
def history(session_id:Optional[str]=None,db:Session=Depends(get_db),user:User=Depends(current_user)):
    stmt=select(ChatMessage).where(ChatMessage.user_id==user.id)
    if session_id:stmt=stmt.where(ChatMessage.session_id==session_id)
    return [{'id':m.id,'session_id':m.session_id,'role':m.role,'content':m.content,'created_at':m.created_at.isoformat()} for m in db.scalars(stmt.order_by(ChatMessage.id.desc()).limit(150)).all()][::-1]

@app.delete('/api/chat/history')
def clear_history(db:Session=Depends(get_db),user:User=Depends(current_user)):
    from sqlalchemy import delete
    db.execute(delete(ChatMessage).where(ChatMessage.user_id==user.id));db.commit();audit(db,user,'history_cleared')
    return {'deleted':True}

@app.post('/api/reports/generate')
def create_report(body:ReportRequest,db:Session=Depends(get_db),user:User=Depends(current_user)):
    # Route through normal chat logic; uses actual SQL and retrieved evidence, not fabricated metrics.
    c=chat(ChatRequest(question=body.question),db,user)
    filename=f'report-{uuid.uuid4().hex[:12]}.pdf';path=Path(settings.reports_dir)/filename
    make_pdf(body.title,body.question,c['answer'],c['sources'],path)
    rec=Report(title=body.title,kind=body.kind,file_path=str(path),user_id=user.id);db.add(rec);db.commit();db.refresh(rec)
    audit(db,user,'report_generated',filename)
    return {'id':rec.id,'title':rec.title,'kind':rec.kind,'download_url':f'/api/reports/{rec.id}/download'}

@app.get('/api/reports')
def list_reports(db:Session=Depends(get_db),user:User=Depends(current_user)):
    stmt=select(Report).order_by(Report.created_at.desc())
    if user.role!='Administrator':stmt=stmt.where(Report.user_id==user.id)
    return [{'id':r.id,'title':r.title,'kind':r.kind,'created_at':r.created_at.isoformat(),'download_url':f'/api/reports/{r.id}/download'} for r in db.scalars(stmt).all()]

@app.get('/api/reports/{report_id}/download')
def download_report(report_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    rep=db.get(Report,report_id)
    if not rep or (rep.user_id!=user.id and user.role!='Administrator'):raise HTTPException(404,'Report not found')
    path=Path(rep.file_path)
    if not path.exists():raise HTTPException(404,'Report file missing')
    return FileResponse(path,media_type='application/pdf',filename=path.name)

@app.post('/api/feedback')
def feedback(body:FeedbackRequest,db:Session=Depends(get_db),user:User=Depends(current_user)):
    db.add(Feedback(user_id=user.id,question=body.question,rating=body.rating,comment=body.comment));db.commit();audit(db,user,'feedback',f'rating={body.rating}')
    return {'saved':True}

@app.get('/api/admin/dashboard')
def admin_dashboard(db:Session=Depends(get_db),user:User=Depends(allowed('Administrator'))):
    return {'users':db.scalar(select(func.count(User.id))),'documents':db.scalar(select(func.count(Document.id))),'chat_messages':db.scalar(select(func.count(ChatMessage.id))),'reports':db.scalar(select(func.count(Report.id))),'audit_logs':db.scalar(select(func.count(AuditLog.id))),'indexing':index_status}

@app.get('/api/admin/users')
def admin_users(db:Session=Depends(get_db),user:User=Depends(allowed('Administrator'))):
    return [{'id':u.id,'email':u.email,'role':u.role,'active':u.active} for u in db.scalars(select(User)).all()]

@app.patch('/api/admin/users/{user_id}/role')
def admin_set_role(user_id:int,body:UserRoleChange,db:Session=Depends(get_db),user:User=Depends(allowed('Administrator'))):
    if body.role not in ROLES:raise HTTPException(400,'Unknown role')
    target=db.get(User,user_id)
    if not target:raise HTTPException(404,'User not found')
    target.role=body.role;db.commit();audit(db,user,'role_changed',f'{user_id}: {body.role}')
    return {'id':target.id,'role':target.role}

@app.get('/api/admin/audit-logs')
def audit_logs(db:Session=Depends(get_db),user:User=Depends(allowed('Administrator'))):
    return [{'id':a.id,'user_id':a.user_id,'action':a.action,'details':a.details,'duration_ms':a.duration_ms,'created_at':a.created_at.isoformat()} for a in db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(150)).all()]

@app.post('/api/evaluation/run')
def evaluate(db:Session=Depends(get_db),user:User=Depends(allowed('Administrator','Supply Chain Analyst'))):
    path=Path(settings.data_dir)/'evaluation'/'test_questions.json'
    questions=json.loads(path.read_text(encoding='utf8'))
    result=measure_retrieval(questions)
    result_path=Path(settings.reports_dir)/'retrieval_evaluation.json'
    result_path.write_text(json.dumps(result,indent=2))
    audit(db,user,'evaluation_completed',f"{result['evaluated_questions']} questions")
    return result
