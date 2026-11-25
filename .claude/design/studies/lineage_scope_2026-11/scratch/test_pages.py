import sys,glob,os
from playwright.sync_api import sync_playwright
d=os.path.abspath('tmp/2026-11-24/lineage_mockups')
sels={'A_outline':'.ln input','B_cytoscape_dagre':None,'C_elk_orthogonal':'.nd','D_column_browser':'.it[data-id]','E_matrix':'th.rh','F_path_view':'.chip','G_hybrid':'.r','H_graphviz_svg':'g.node'}
with sync_playwright() as p:
    b=p.chromium.launch();
    for n,s in sels.items():
        pg=b.new_page(viewport={'width':1200,'height':800});errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        pg.set_default_timeout(8000);pg.goto('file://%s/%s.html'%(d,n),wait_until='domcontentloaded');pg.wait_for_timeout(1500)
        if s:
            try:
                pg.locator(s).nth(1 if n=='A_outline' else 2 if n!='F_path_view' else 0).click(force=True)
            except Exception as e: errs.append('click:'+str(e)[:80])
        pg.wait_for_timeout(500)
        pg.screenshot(path='tmpAI/panel/lineage_scope/scratch/shot_%s.png'%n)
        print(n,errs[:3],flush=True)
    b.close()
