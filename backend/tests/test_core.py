from datetime import datetime,timedelta
from app.rag import expand_query,split_parents,compress_context,make_chunks
from app.analytics import route_intent
from app.auth import ROLES
from app.config import settings
from app.reporting import make_pdf

def test_intent_sql():
    assert route_intent('Show inventory for Product P100') == 'sql'
    assert route_intent('List delayed purchase orders') == 'sql'

def test_intent_report():
    assert route_intent('Generate daily operations report') == 'report'
    assert route_intent('Generate replenishment checklist') == 'report'

def test_intent_rag():assert route_intent('Explain warehouse receiving procedure') == 'rag'

def test_query_expansion():
    result=expand_query('Product P100 out of stock')
    assert 'Product P100 out of stock' in result
    assert len(result)>=2 and len(set(result))==len(result)

def test_parent_child_chunking():
    old_size=settings.chunk_size
    try:
        settings.chunk_size=140
        chunks=make_chunks([(2,'1. Receiving:\n'+'Verify shipment labels and count cartons. '*16)])
        assert len(chunks)>1
        assert chunks[0]['page']==2
        assert 'Verify shipment' in chunks[0]['parent']
    finally:settings.chunk_size=old_size

def test_context_compression():
    txt='Brand story.\nWarehouse must validate shipment receipt.\nSeparate products.'
    result=compress_context('shipment receipt',txt,90)
    assert 'shipment receipt' in result

def test_auth_roles():assert len(ROLES)==6 and 'Administrator' in ROLES

def test_report_pdf(tmp_path):
    target=tmp_path/'report.pdf'
    assert make_pdf('Daily Report','Check stock','No stock available',[],target)==str(target)
    assert target.stat().st_size>500
