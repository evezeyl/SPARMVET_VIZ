import re,subprocess,json,sys
src=open('tmp/2026-11-24/lineage_mockups/data.js').read()
d=json.loads(src[src.index('{'):src.rindex('}')+1].replace("'",'"')) if False else None
# parse data.js by node: simple regex
nodes=re.findall(r"\{id:'([^']+)', kind:'(\w+)', table:'([^']+)', label:'([^']+)'",src)
edges=re.findall(r"\['([^']+)','([^']+)'\]",src)
chi={}
for a,b in edges: chi.setdefault(a,[]).append(b)
dot=['digraph G{rankdir=LR;node [shape=box,style="rounded,filled",fillcolor=white,fontname="sans-serif",fontsize=10,color="#6b7280"];edge [color="#9ca3af",arrowsize=.6];']
for i,k,t,l in nodes:
    res=i not in chi
    dot.append('"%s" [label="%s%s"%s];'%(i,{'DS':'original\\n','T1':'tier 1\\n','T2':'tier 2\\n','T3':''}[k],l,',penwidth=2' if res else ''))
for a,b in edges: dot.append('"%s"->"%s";'%(a,b))
dot.append('}')
svg=subprocess.run(['dot','-Tsvg'],input='\n'.join(dot),capture_output=True,text=True,check=True).stdout
svg=svg[svg.index('<svg'):]
page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="common.css"><script src="data.js"></script><script src="core.js"></script>
<style>svg g.node{cursor:pointer}svg g.node polygon,svg g.node path{fill:#fff}svg g.node.st-selected polygon,svg g.node.st-selected path{fill:#1d4ed8}svg g.node.st-selected text{fill:#fff}svg g.node.st-derived polygon,svg g.node.st-derived path{fill:#dbeafe}svg g.node.st-blocked polygon,svg g.node.st-blocked path{stroke-dasharray:3 3}svg g.node.st-blocked text{fill:#9ca3af}svg g.node.hid{opacity:.12}svg g.edge.hid{opacity:.08}svg{max-width:100%;height:auto}</style>
<div id="holder" style="display:none">'''+svg+'''</div>
<script>
const holder=document.getElementById('holder').innerHTML;
function draw(main){if(!main.querySelector('svg'))main.innerHTML='<p style="font-size:12px;color:#6b7280">The picture below was made once, on the SERVER, by Graphviz (dot). In the real app the server would draw it again after each choice; here a script only recolours it.</p>'+holder;
 main.querySelectorAll('g.node').forEach(g=>{const id=g.querySelector('title').textContent;g.dataset.id=id;g.setAttribute('class','node '+LG.cls(id)+(LG.visible(id)?'':' hid'));g.onclick=()=>LG.select(id);g.onmouseenter=()=>{LG.hover=id;document.getElementById('info').innerHTML=LG.infoHTML(id)};g.onmouseleave=()=>{LG.hover=null;LG.emit()}});
 main.querySelectorAll('g.edge').forEach(g=>{const t=g.querySelector('title').textContent.split('->');g.setAttribute('class','edge'+(LG.visible(t[0])&&LG.visible(t[1])?'':' hid'))})}
LG.mount('H. Server-drawn picture (Graphviz SVG)','<b>What you can do</b>see the whole graph as a fixed picture, click boxes (links in the SVG), hover; works with no layout library in the browser. <br><b>What you cannot</b>fold, zoom smoothly or drag; every change means a new picture from the server (slower, but simple). <br><b>Cost to build</b>M: dot text from the graph, run dot, return SVG with links; add focus colouring on the server. <br><b>Needs</b>the Graphviz program (dot) on the machine: EPL licence, a system package; in the container image yes, on Posit Connect and Galaxy NOT sure (not verified).',draw)
</script>'''
open('tmp/2026-11-24/lineage_mockups/H_graphviz_svg.html','w').write(page)
