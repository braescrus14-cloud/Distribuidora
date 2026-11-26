"""HU-16–20 integration. Uses disposable databases, never the Render Atlas store."""
import hashlib
import hmac
import json
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from http.client import HTTPConnection
from io import BytesIO
from pathlib import Path
from threading import Thread
from uuid import uuid4

import app
from commerce import COLOMBIA, all_records, find, nit_digit, products, save
from commerce_seed import seed


def check():
    password="Finanzas!2026"
    with app.database() as db:
        app.initialize_schema(db)
        for i in range(1,11):
            app.run_db(db,"admin_add","INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",(f"fin{i}",f"Finanzas {i}",app.password_hash(password),f"{i:02}"))
        app.run_db(db,"admin_add","INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",("other-fin-client","Otro cliente",app.password_hash(password),"10"))
        seed(db)
        customer=find(db,"clientes","alto-verde");save(db,"clientes",{**customer,"credit":1_000_000_000})
        other=app.run_db(db,"user_by_username","SELECT * FROM users WHERE username=?",("other-fin-client",)).fetchone()
        c=find(db,"clientes","la-pradera");save(db,"clientes",{**c,"account":other["id"]})
        item=products(db)["VIL-CAN-15"]
        # Snapshot fixtures represent previously picked and delivered orders.
        def fixture(key,quantity=5,price=65_000_000,credit=True,partial=None):
            line={"sku":item["sku"],"name":item["name"],"quantity":quantity,"price":price,"picked":True,
                  "reservations":[{"lot":"L-VIL-CAN-15","location":"Bodega principal","quantity":quantity,"expiry":(datetime.now(COLOMBIA).date()+timedelta(days=300)).isoformat()}]}
            row={"id":key,"number":"PV-TEST-"+key,"customer":"alto-verde","customer_name":customer["name"],"status":"ENTREGADO","credit":credit,
                 "date":datetime.now(COLOMBIA).isoformat(),"lines":[line],"total":quantity*price,"advisor":customer["advisor"],"created_by":customer["advisor"]}
            if partial is not None:row["delivered_lines"]=[{**line,"quantity":partial}]
            save(db,"pedidos",row);return row
        for key in ("invoice-one","cash-one","cash-two","return-damaged","return-credit","return-before-invoice","bad-order","partial"):
            fixture(key,credit=key not in {"cash-one","cash-two"},partial=3 if key=="partial" else None)
        save(db,"pedidos",{**find(db,"pedidos","bad-order"),"status":"CONFIRMADO"})
        driver=app.run_db(db,"user_by_username","SELECT * FROM users WHERE username=?",("fin8",)).fetchone()
        save(db,"pedidos",{**find(db,"pedidos","partial"),"status":"EN_RUTA"})
        save(db,"rutas",{"id":"partial-route","number":"RT-PARTIAL","status":"EN_RUTA","driver":driver["id"],"vehicle":"PART","orders":["partial"],"stops":[]})
        fixture("cash-exact",price=96_000_000,credit=False)
        save(db,"rutas",{"id":"exact-route","number":"RT-EXACT","status":"FINALIZADA","vehicle":"EXA","driver":driver["id"],"orders":["cash-exact"],"stops":[]})
        fixture("analytics",price=3_700_000_000)
        fixture("clean-client",price=100_000)
        clean=find(db,"pedidos","clean-client");save(db,"pedidos",{**clean,"customer":"la-pradera","customer_name":"Veterinaria La Pradera"})
        save(db,"rutas",{"id":"cash-route","number":"RT-TEST","status":"FINALIZADA","vehicle":"DEM321","driver":1,"orders":["cash-one","cash-two"],"stops":[]})
    server=app.ThreadingHTTPServer(("127.0.0.1",0),app.Handler)
    def start():
        server.origin=f"http://localhost:{server.server_port}";worker=Thread(target=server.serve_forever,daemon=True);worker.start();return worker
    worker=start();cookies={}
    def call(path,role=None,data=None,status=200,headers=None,raw=None):
        conn=HTTPConnection("127.0.0.1",server.server_port,timeout=25)
        try:
            body=raw if raw is not None else json.dumps(data).encode() if data is not None else None
            conn.request("POST" if body is not None else "GET",path,body,{"Host":f"localhost:{server.server_port}","Origin":server.origin,"Cookie":cookies.get(role,""),"Content-Type":"application/json",**(headers or {})})
            response=conn.getresponse();payload=response.read();result=json.loads(payload) if 'application/json' in response.getheader('Content-Type','') else payload
            assert response.status==status,(path,status,response.status,str(result)[:500])
            return result,response.getheader('Set-Cookie','').split(';')[0]
        finally:conn.close()
    def api(kind,role='09',data=None,status=200):return call('/api/finanzas/'+kind,role,data,status)[0]
    nit='901763482';valid_nit=nit+'-'+str(nit_digit(nit));due=(datetime.now(COLOMBIA).date()-timedelta(days=45)).isoformat()
    def emit(key,**extra):return api('facturas',data={'order':key,'nit':valid_nit,'email':'cliente@example.com','due':due,**extra})
    def pay(key,amount,**extra):return api('pagos',data={'invoice':key,'amount':amount,'method':'TRANSFERENCIA','reference':'ENSAYO','request_id':str(uuid4()),**extra})
    try:
        for role,name in [(f'{i:02}',f'fin{i}') for i in range(1,11)]+[('other','other-fin-client')]:cookies[role]=call('/api/login',data={'username':name,'password':password})[1]
        call('/api/finanzas/facturas',status=401)
        allowed={'facturas':{'01','09','10'},'pagos':{'09','10'},'cartera':{'01','09'},'liquidaciones':{'07'},'devoluciones':{'03'},'indicadores':{'01'},'bandeja':{'09'},'cortes':{'01'}}
        for endpoint,roles in allowed.items():
            for i in range(1,11):api(endpoint,f'{i:02}',status=200 if f'{i:02}' in roles else 403)
        api('facturas','01',{'order':'invoice-one'},403)
        api('facturas',data={'order':'bad-order','nit':valid_nit,'email':'cliente@example.com','due':due},status=409)
        rejected=emit('invoice-one',nit='123-0');assert rejected['status']=='RECHAZADA'
        first=emit('invoice-one');assert first['number']==rejected['number'] and first['status']=='EMITIDA' and first['total']==325_000_000 and first['cufe'].startswith('DEMO-')
        assert emit('invoice-one')['number']==first['number']
        from PIL import Image
        import base64
        image=BytesIO();Image.new("RGB",(120,80),(25,100,50)).save(image,"PNG");proof="data:image/png;base64,"+base64.b64encode(image.getvalue()).decode()
        partial_payload={"id":"partial","result":"ENTREGADO","request_id":str(uuid4()),"lat":7.1,"lng":-73.1,"signature":proof,"photo":proof,"returned_lines":[{"sku":"VIL-CAN-15","lot":"L-VIL-CAN-15","location":"Bodega principal","quantity":2}]}
        call('/api/logistica/deliveries','08',partial_payload);call('/api/logistica/deliveries','08',partial_payload)
        partial=emit('partial');assert partial['total']==195_000_000 and partial['lines'][0]['quantity']==3
        assert api('documento?id=invoice-one&format=pdf')[0:5]==b'%PDF-'
        xml=api('documento?id=invoice-one&format=xml');assert b'AcademicInvoice' in xml and b'fiscalValidity="none"' in xml
        assert len(api('bandeja')['rows'][0]['attachments'])==2
        api('documento?id=invoice-one&format=pdf','other',status=404)
        assert api('facturas','other')['rows']==[]
        assert any(r['bucket']=='31–60' for r in api('cartera')['rows'] if r['id']=='invoice-one')
        payment=pay('invoice-one',125_000_000)
        assert api('facturas')['rows'][0]['id'] # Verify below by id, independent of sort.
        current=next(r for r in api('facturas')['rows'] if r['id']=='invoice-one');assert current['balance']==200_000_000 and current['status']=='PAGO_PARCIAL'
        api('pagos',data={'invoice':'invoice-one','amount':250_000_000,'method':'EFECTIVO','reference':'EXCESO','request_id':str(uuid4())},status=409)
        assert pay('invoice-one',125_000_000,request_id=payment['id'])['id']==payment['id']
        intent=api('pse','10',{'action':'start','invoice':'invoice-one','amount':200_000_000})
        api('pse','other',{'action':'simulate','id':intent['id']},404)
        event=json.dumps({'intent':intent['id'],'amount':200_000_000,'result':'CONFIRMADO'}).encode();stamp=str(int(time.time()))
        call('/api/finanzas/pse-webhook',raw=event,headers={'X-PSE-Timestamp':stamp,'X-PSE-Signature':'wrong'},status=401)
        with app.database() as db:secret=find(db,'finance_secrets','pse')['key']
        signature=hmac.new(secret.encode(),stamp.encode()+b'.'+event,hashlib.sha256).hexdigest()
        for _ in range(2):call('/api/finanzas/pse-webhook',raw=event,headers={'X-PSE-Timestamp':stamp,'X-PSE-Signature':signature})
        old=str(int(time.time())-1000);old_sig=hmac.new(secret.encode(),old.encode()+b'.'+event,hashlib.sha256).hexdigest()
        call('/api/finanzas/pse-webhook',raw=event,headers={'X-PSE-Timestamp':old,'X-PSE-Signature':old_sig},status=401)
        current=next(r for r in api('facturas')['rows'] if r['id']=='invoice-one');assert current['balance']==0 and current['status']=='PAGADA'
        with app.database() as db:assert find(db,'pedidos','invoice-one')['status']=='CERRADO'
        # A concurrent same-key retry applies one receipt.
        common=str(uuid4())
        results=list(ThreadPoolExecutor(max_workers=2).map(lambda _:pay('partial',10_000_000,request_id=common),range(2)))
        assert results[0]['id']==results[1]['id']
        emit('cash-exact')
        assert api('liquidaciones','07',{'id':'exact-route','received':480_000_000})['difference']==0
        for key in ['cash-one','cash-two']:emit(key)
        api('liquidaciones','07',{'id':'cash-route','received':645_000_000,'statement':''},409)
        settled=api('liquidaciones','07',{'id':'cash-route','received':645_000_000,'statement':'Acta de ensayo: faltante de $50.000, responsable de ruta.'})
        assert settled['difference']==5_000_000 and settled['expected']==650_000_000
        assert api('liquidaciones','07',{'id':'cash-route','received':645_000_000})['id']=='cash-route'
        assert sum(r['amount'] for r in api('pagos')['payments'] if r['source']=='route' and r['invoice'] in {'cash-one','cash-two'})==645_000_000
        # Fully collected route requires no difference statement.
        with app.database() as db:save(db,'rutas',{'id':'paid-route','number':'RT-PAGADA','status':'FINALIZADA','vehicle':'TST','driver':1,'orders':['invoice-one'],'stops':[]})
        assert api('liquidaciones','07',{'id':'paid-route','received':0})['difference']==0
        def returned(key,decision,quantity=2):
            row=api('devoluciones','03',{'action':'report','order':key,'request_id':str(uuid4()),'sku':'VIL-CAN-15','lot':'L-VIL-CAN-15','origin_location':'Bodega principal','quantity':quantity,'note':'Devolución de ensayo'})
            return api('devoluciones','03',{'action':'inspect','id':row['id'],'decision':decision,'location':'Retornos ensayo','reason':'Avería en transporte' if decision=='MERMA' else 'Bultos íntegros'})
        emit('return-credit');before=None
        with app.database() as db:
            before=sum(r['quantity'] for r in app.run_db(db,'commerce_lots','SELECT * FROM lots WHERE product_id=? ORDER BY expiry,lot,location',(item['id'],)))
        returned_credit=returned('return-credit','REINGRESO');assert returned_credit['credit_note'].startswith('NC-DEMO')
        again=api('devoluciones','03',{'action':'inspect','id':returned_credit['id'],'decision':'REINGRESO','location':'Retornos ensayo','reason':'Reintento'});assert again['id']==returned_credit['id']
        invoice=next(r for r in api('facturas')['rows'] if r['id']=='return-credit');assert invoice['balance']==195_000_000
        with app.database() as db:assert sum(r['quantity'] for r in app.run_db(db,'commerce_lots','SELECT * FROM lots WHERE product_id=? ORDER BY expiry,lot,location',(item['id'],)))==before+2
        emit('return-damaged');returned('return-damaged','MERMA',1)
        with app.database() as db:assert sum(r['quantity'] for r in app.run_db(db,'commerce_lots','SELECT * FROM lots WHERE product_id=? ORDER BY expiry,lot,location',(item['id'],)))==before+2
        returned('return-before-invoice','REINGRESO',2);assert emit('return-before-invoice')['total']==195_000_000
        pay('return-credit',195_000_000)
        with app.database() as db:assert find(db,'pedidos','return-credit')['status']=='CERRADO'
        # Opening balances remain collectible and keep legacy debt separate.
        legacy=pay('opening-monte-claro',5_000_000)
        assert pay('opening-monte-claro',5_000_000,request_id=legacy['id'])['id']==legacy['id']
        with app.database() as db:assert find(db,'clientes','monte-claro')['balance']==15_000_000
        # Other overdue invoices still block credit; a fully paid isolated customer is released.
        call('/api/comercio/pedidos','06',{'action':'create','customer':'alto-verde','credit':True,'request_id':str(uuid4()),'lines':[{'sku':'VIL-CAN-15','quantity':1}]},status=409)
        emit('clean-client');intent2=api('pse','09',{'action':'start','invoice':'clean-client','amount':500_000});api('pse','09',{'action':'simulate','id':intent2['id']})
        with app.database() as db:assert find(db,'clientes','la-pradera')['balance']==0 and find(db,'clientes','la-pradera')['due']==''
        call('/api/comercio/pedidos','06',{'action':'create','customer':'la-pradera','credit':True,'request_id':str(uuid4()),'lines':[{'sku':'VIL-CAN-15','quantity':1}]})
        assert api('nota-credito?id='+returned_credit['id'],'03').startswith(b'%PDF-')
        assert api('acta-ruta?id=exact-route','07').startswith(b'%PDF-')
        # Fixed-period reporting, prior calendar month, zero/missing base, export fidelity.
        emit('analytics')
        with app.database() as db:
            invoice=find(db,'facturas','analytics');save(db,'facturas',{**invoice,'issued_at':'2026-10-15T10:00:00-05:00'})
            item2=app.run_db(db,'product_add','INSERT INTO products(sku,barcode,name,brand,species,presentation,price_cents,minimum) VALUES(?,?,?,?,?,?,?,?) RETURNING id',('REORDER','2050000001999','Producto mínimo','Villali','Aves','40 kg',10000,20)).fetchone()
            app.run_db(db,'commerce_lot_add','INSERT INTO lots(product_id,lot,expiry,location,quantity,reserved) VALUES(?,?,?,?,?,?)',(item2['id'],'REORD',(datetime.now(COLOMBIA).date()+timedelta(days=100)).isoformat(),'A',8,0))
        query='indicadores?from=2026-10-01&to=2026-10-31&customer=alto-verde&zone=Norte&sku=VIL-CAN-15'
        report=api(query,'01');assert report['sales']==18_500_000_000 and report['previous_from']=='2026-09-01' and report['previous_to']=='2026-09-30' and report['variation'] is None
        assert api(query.replace('zone=Norte','zone=NO-EXISTE'),'01')['sales']==0
        full=api('indicadores','01');assert next(r for r in full['stock'] if r['sku']=='REORDER')['shortage']==12
        from openpyxl import load_workbook
        book=load_workbook(BytesIO(api(query+'&format=xlsx','01')),data_only=True);assert 'Inventario' in book.sheetnames and book['Ventas filtradas']['B4'].value==report['sales'];assert book['Ventas filtradas'].max_row==6
        assert api(query+'&format=pdf','01').startswith(b'%PDF-')
        cut_data={'action':'snapshot','request_id':str(uuid4()),'from':'2026-10-01','to':'2026-10-31','customer':'alto-verde','zone':'Norte','sku':'VIL-CAN-15'}
        cut=api('indicadores','01',cut_data);assert api('indicadores','01',cut_data)['id']==cut['id']
        with app.database() as db:save(db,'facturas',{**find(db,'facturas','analytics'),'issued_at':'2026-11-15T10:00:00-05:00'})
        assert api(query,'01')['sales']==0
        assert api('indicadores?cut='+cut['id'],'01')['sales']==18_500_000_000
        frozen=load_workbook(BytesIO(api('indicadores?cut='+cut['id']+'&format=xlsx','01')),data_only=True);assert frozen['Ventas filtradas']['B4'].value==18_500_000_000
        with app.database() as db:save(db,'facturas',{**find(db,'facturas','analytics'),'issued_at':'2026-10-15T10:00:00-05:00'})
        api('indicadores?from=2026-12-01&to=2026-01-01','01',status=400)
        with app.database() as db:
            product=products(db)['VIL-CAN-15']
            app.run_db(db,'commerce_lot_add','INSERT INTO lots(product_id,lot,expiry,location,quantity,reserved) VALUES(?,?,?,?,?,?)',(product['id'],'EXPIRED-FIN','2020-01-01','Cuarentena',3,0))
        expiry={'action':'expiry','request_id':str(uuid4()),'sku':'VIL-CAN-15','lot':'EXPIRED-FIN','location':'Cuarentena','quantity':2,'reason':'Vencimiento inspeccionado'}
        loss=api('devoluciones','03',expiry);assert api('devoluciones','03',expiry)['id']==loss['id']
        expired=api('devoluciones','03')['expired'];assert next(r for r in expired if r['lot']=='EXPIRED-FIN')['quantity']==1
        api('devoluciones','03',{**expiry,'request_id':str(uuid4()),'quantity':2},409)
        assert any(r['id']==loss['id'] for r in api('indicadores','01')['losses'])
        api('indicadores?customer=alto-verde&zone=Norte','01')
        server.shutdown();server.server_close();worker.join()
        with app.database() as db:app.initialize_schema(db)
        server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler);worker=start()
        assert next(r for r in api('facturas')['rows'] if r['id']=='invoice-one')['status']=='PAGADA'
        assert len(api('liquidaciones','07')['rows'])==3
        assert api('documento?id=invoice-one&format=xml','10').startswith(b'<?xml')
        print('HU-16–20 PASS: roles, rejected retry, net delivered invoice, PDF/XML, outbox, aging, partial/excess payments, signed PSE replay, route reconciliation, credit notes, stock/waste, filtered exports, restart persistence.')
        if os.environ.get('VILLALI_TEST_PREVIEW'):
            print('PREVIEW '+server.origin,flush=True);worker.join()
    finally:server.shutdown();server.server_close();worker.join()


if __name__=='__main__':
    with tempfile.TemporaryDirectory() as temporary:
        app.DB=Path(temporary)/'finance.sqlite3';check()
