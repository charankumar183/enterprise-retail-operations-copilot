"""Generate capstone slides from requirements. No invented performance figures."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_THEME_COLOR

OUT=Path(__file__).parent/'presentation'/'Retail_Operations_Copilot_Capstone.pptx'
prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
NAVY=RGBColor(13,33,59);BLUE=RGBColor(34,103,232);WHITE=RGBColor(255,255,255);MUTED=RGBColor(119,141,165);PALE=RGBColor(242,247,253);TEAL=RGBColor(13,150,138)

def rect(sl,x,y,w,h,fill,rad=False):
    sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rad else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=fill;sh.line.fill.background();return sh

def txt(sl,text,x,y,w,h,size=18,color=NAVY,bold=False):
    box=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame;tf.word_wrap=True
    for i,line in enumerate(text.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.space_after=Pt(11)
        for r in p.runs:r.font.name='Aptos';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=color
    return box

def base(num,title,kicker='ENTERPRISE AI RETAIL OPERATIONS COPILOT'):
    sl=prs.slides.add_slide(prs.slide_layouts[6]);rect(sl,0,0,13.333,7.5,WHITE);rect(sl,0,0,13.333,.11,BLUE)
    txt(sl,kicker,.7,.35,11,.28,10,BLUE,True);txt(sl,title,.7,.85,12,1,32,NAVY,True)
    rect(sl,.7,7.12,11.95,.013,RGBColor(217,228,239))
    txt(sl,'SYNTHETIC DEMONSTRATION DATA · CAPSTONE PROJECT',.7,7.17,9,.2,9,MUTED);txt(sl,f'{num:02}',12.14,7.15,.48,.2,9,MUTED)
    return sl

def box(sl,x,y,w,h,heading,body,accent=BLUE):
    rect(sl,x,y,w,h,PALE,True);rect(sl,x,y,.08,h,accent)
    txt(sl,heading,x+.26,y+.22,w-.45,.35,16,NAVY,True);txt(sl,body,x+.26,y+.77,w-.45,h-1,13,RGBColor(68,93,121))

sl=prs.slides.add_slide(prs.slide_layouts[6]);rect(sl,0,0,13.333,7.5,NAVY);rect(sl,.78,.98,.13,5.2,BLUE)
txt(sl,'ACADEMIC CAPSTONE · ADVANCED RAG',1.2,1.02,11,.4,12,RGBColor(112,175,252),True)
txt(sl,'Enterprise AI Retail\nOperations & Supply Chain\nCopilot',1.2,1.72,11,3.1,38,WHITE,True)
txt(sl,'Document intelligence  ·  SQL analytics  ·  Source-backed decisions',1.2,5.64,11,.6,17,RGBColor(168,194,220))
txt(sl,'Synthetic retail enterprise · Demonstration project',1.2,6.9,11,.3,11,RGBColor(112,175,252))

sl=base(2,'The enterprise problem')
box(sl,.75,2.18,3.7,3.4,'Fragmented knowledge','Inventory SOPs, policies, procurement guides and vendor contracts live in separate systems.')
box(sl,4.82,2.18,3.7,3.4,'Slow business decisions','Store teams spend time switching between documents, dashboards and purchase-order records.',TEAL)
box(sl,8.89,2.18,3.7,3.4,'Auditable answers needed','Operational recommendations must cite the underlying document, section and page where available.')

sl=base(3,'Project objectives')
box(sl,.75,2.12,5.7,1.7,'Advanced RAG','Retrieve answer evidence from enterprise retail documents.')
box(sl,6.85,2.12,5.7,1.7,'SQL analytics','Analyze inventory, supplier, sales and purchase-order records.',TEAL)
box(sl,.75,4.17,5.7,1.7,'Operational reports','Generate report PDFs and replenishment guidance.')
box(sl,6.85,4.17,5.7,1.7,'Cloud-ready enterprise portal','JWT roles, audit logs, React UI, Docker and Nginx.',TEAL)

sl=base(4,'Architecture — intelligent intent routing')
for x,label in [(1,'User question'),(4.65,'FastAPI / JWT'),(8.3,'Intent detection')]:
    rect(sl,x,2.16,3.1,.73,PALE,True);txt(sl,label,x+.13,2.35,2.85,.3,16,NAVY,True)
for x,label,accent in [(1.01,'RAG Search',BLUE),(5.1,'SQL Analytics',TEAL),(9.1,'Report Generator',BLUE)]:
    rect(sl,x,4.08,3.17,1.1,accent,True);txt(sl,label,x+.23,4.44,2.9,.35,17,WHITE,True)
txt(sl,'Intent-driven orchestration without LangGraph',2.9,5.7,7.8,.5,18,NAVY,True)

sl=base(5,'Advanced RAG — retrieval stages')
items=[('1','Document loading','PDF · DOCX · TXT · CSV · XLSX'),('2','Intelligent chunking','Metadata-based parent–child sections'),('3','Query expansion','Multiple lexical query variations'),('4','Hybrid retrieval','Chroma vector + BM25 keyword'),('5','Re-ranking','RRF + optional cross-encoder'),('6','Compression & citation','Relevant context with original references')]
for i,(num,title,body) in enumerate(items):
    x=.74+(i%3)*4.14;y=2.1+(i//3)*2.2
    box(sl,x,y,3.76,1.9,f'{num}. {title}',body,TEAL if i%2 else BLUE)

sl=base(6,'Synthetic enterprise retail dataset')
box(sl,.75,2.1,5.8,3.85,'Structured SQL records','120 products, 5 stores, 4 warehouses, suppliers, purchase orders, inventory, sales, returns, customer complaints, prices and forecasts.')
box(sl,6.8,2.1,5.8,3.85,'Unstructured knowledge','18 bundled synthetic documents across PDF, DOCX, TXT, CSV and Excel; Promotion Policy v3 and v5; 30 labeled retrieval questions.',TEAL)

sl=base(7,'Functional product experience')
items=[('Dashboard','SQL KPI cards & stock alerts'),('AI Copilot','Policy/SQL routing, chat history & citations'),('Inventory','Store and warehouse stock search'),('Document library','Upload, index, version, reindex, delete'),('Reports','Source-backed PDF report download'),('Administration','RBAC users, logs and evaluation')]
for i,(name,detail) in enumerate(items):
    x=.74+(i%2)*6.15;y=2.0+(i//2)*1.44
    box(sl,x,y,5.75,1.24,name,detail,TEAL if i%2 else BLUE)

sl=base(8,'Security and operational controls')
box(sl,.75,2.2,3.73,3.45,'Access management','JWT auth · Argon2 hashing · six role types · backend-enforced permissions')
box(sl,4.8,2.2,3.73,3.45,'Data and retrieval','No arbitrary generated SQL · source evidence · upload validation · prompt-injection aware design',TEAL)
box(sl,8.85,2.2,3.73,3.45,'Observability','Chat and document events · SQL usage audit · failure handling · response latency')

sl=base(9,'Evaluation — measured only after execution')
box(sl,.75,2.1,5.8,3.76,'Retrieval evaluation','30 labeled questions\nPrecision@5 / Recall@5\nMeasured response latency\nTwo embedding model comparison')
box(sl,6.8,2.1,5.8,3.76,'Evidence-based reporting','Answer accuracy and hallucination rate need human or LLM evaluation. No metrics are invented in the packaged code.',TEAL)

sl=base(10,'Deployment and reproducibility')
box(sl,.75,2.12,3.8,3.55,'Local demo','Docker Compose starts PostgreSQL, FastAPI and Nginx-powered React application.')
box(sl,4.8,2.12,3.8,3.55,'Cloud requirement','Deploy to AWS/Azure/GCP with TLS and a public URL using your own cloud account.',TEAL)
box(sl,8.85,2.12,3.8,3.55,'Evidence','Swagger/OpenAPI · unit tests · generated reports · local deployment logs · Git-ready source')

sl=base(11,'Expected business impact — to validate')
box(sl,.75,2.1,5.8,3.8,'Search efficiency','Potential reduction in policy lookup time and fewer manual document searches. Measure against staff baseline.')
box(sl,6.8,2.1,5.8,3.8,'Supply-chain decisions','Faster visibility into stockouts, pending POs and replenishment procedures. Quantify outcomes after pilot.',TEAL)

sl=base(12,'Submission checklist and next steps')
box(sl,.75,2.05,5.8,3.8,'Included in project ZIP','Working source · Docker images config · architecture · API docs · synthetic data · evaluation scripts · technical docs · presentation')
box(sl,6.8,2.05,5.8,3.8,'Requires your execution','Publish GitHub repo · provision public cloud deployment · capture 10–15 minute demo video · run metrics and upload results.',TEAL)

OUT.parent.mkdir(parents=True,exist_ok=True);prs.save(str(OUT));print('Presentation:',OUT, 'slides:',len(prs.slides))
