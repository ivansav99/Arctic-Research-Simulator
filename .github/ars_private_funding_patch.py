from pathlib import Path

path = Path('expedition.js')
text = path.read_text()

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    text = text.replace(old, new, 1)

replace_once(
    "  const RESEARCH_INTERACTION_KM = 10;\n  const PAPER_LEVELS = [",
    "  const RESEARCH_INTERACTION_KM = 10;\n  // StoreKit-ready consumable funding packs. The web build uses a simulated\n  // purchase adapter; an iOS wrapper can provide window.ArcticResearchIAP.purchase(productId).\n  const PRIVATE_FUNDING_PACKAGES = [\n    {id:'funding-1m',productId:'ars.private_funding.1m',gameCash:1000000,price:'$0.99',label:'$1 MILLION'},\n    {id:'funding-10m',productId:'ars.private_funding.10m',gameCash:10000000,price:'$4.99',label:'$10 MILLION'},\n    {id:'funding-50m',productId:'ars.private_funding.50m',gameCash:50000000,price:'$9.99',label:'$50 MILLION'}\n  ];\n  const PAPER_LEVELS = [",
    'funding package constants'
)

marker = "  function renderPort() {\n"
funding_functions = '''  function openPrivateFunding() {
    if (!root||!state.port) return;
    const modal=root.querySelector('#arx-funding-modal');
    modal.innerHTML=`<div class="arx-modal-card arx-funding-card"><button class="arx-close" data-arx-action="close-private-funding" aria-label="Close private funding">×</button><small>PRIVATE RESEARCH BACKING</small><h2>Apply for Private Funding</h2><p>Accelerate the expedition with an unrestricted private research contribution.</p><div class="arx-web-preview"><b>WEB PREVIEW · NO REAL CHARGE</b><span>Purchases are simulated in this browser build. In the iOS app, these same product IDs will be fulfilled through StoreKit.</span></div><div class="arx-funding-balance"><small>CURRENT EXPEDITION CASH</small><b data-arx-cash>${cash(state.money)}</b></div><div class="arx-funding-grid">${PRIVATE_FUNDING_PACKAGES.map((item,index)=>`<article class="${index===1?'featured':''}"><small>${index===0?'STARTER BACKING':index===1?'POPULAR':'MAJOR SPONSOR'}</small><b>${item.label}</b><span>game cash</span><button data-arx-action="buy-private-funding" data-id="${item.id}">${item.price}</button></article>`).join('')}</div><p class="arx-funding-note">Private funding is a consumable purchase: each successful transaction adds the selected amount to expedition cash and does not alter research progress, career level, or vessel requirements.</p></div>`;
    modal.classList.add('open');
  }
  async function purchasePrivateFunding(id,button) {
    const item=PRIVATE_FUNDING_PACKAGES.find(pack=>pack.id===id); if(!item)return;
    const originalLabel=button?.textContent||item.price;
    if(button){button.disabled=true;button.textContent='PROCESSING…';}
    let result={success:true,mode:'web-preview'};
    try {
      const adapter=window.ArcticResearchIAP;
      if(adapter&&typeof adapter.purchase==='function') {
        const response=await adapter.purchase(item.productId);
        if(response===false||response?.success===false) result={success:false,mode:'storekit',message:response?.message||'Purchase was not completed'};
        else result={success:true,mode:'storekit',transactionId:response?.transactionId||null};
      }
    } catch(error) {
      result={success:false,mode:'storekit',message:error?.message||'Purchase failed'};
    }
    if(!result.success){if(button){button.disabled=false;button.textContent=originalLabel;}toast((result.message||'PURCHASE NOT COMPLETED').toUpperCase());return;}
    adjustMoney(item.gameCash);
    addLog(`Private funding received: ${cash(item.gameCash)}${result.mode==='web-preview'?' · web preview transaction':''}.`);
    root.querySelector('#arx-funding-modal')?.classList.remove('open');
    toast(`PRIVATE FUNDING SECURED · ${cash(item.gameCash)}`); changed();
  }

'''
replace_once(marker, funding_functions + marker, 'funding functions')

replace_once(
    '<div class="arx-port-cash"><small>CASH</small><b data-arx-cash>${cash(state.money)}</b></div>',
    '<div class="arx-port-cash"><span><small>CASH</small><b data-arx-cash>${cash(state.money)}</b></span><button data-arx-action="open-private-funding">APPLY FOR PRIVATE FUNDING</button></div>',
    'port cash funding button'
)

replace_once(
    "    else if (action==='open-port'&&state.port) renderPort();\n    else if (action==='fuel'||action==='food'||action==='supplies') buyResource(action);",
    "    else if (action==='open-port'&&state.port) renderPort();\n    else if (action==='open-private-funding'&&state.port) openPrivateFunding();\n    else if (action==='close-private-funding') root.querySelector('#arx-funding-modal').classList.remove('open');\n    else if (action==='buy-private-funding') purchasePrivateFunding(id,button);\n    else if (action==='fuel'||action==='food'||action==='supplies') buyResource(action);",
    'funding actions'
)

replace_once(
    '<div id="arx-npc-modal" class="arx-modal"></div><div id="arx-dev-modal" class="arx-modal"></div>',
    '<div id="arx-npc-modal" class="arx-modal"></div><div id="arx-funding-modal" class="arx-modal"></div><div id="arx-dev-modal" class="arx-modal"></div>',
    'funding modal root'
)

replace_once(
    '.arx-port-cash{flex:0 0 auto;display:flex!important;align-items:center;gap:8px;margin:0!important;padding:0 12px!important;border-left:1px solid rgba(166,230,244,.18);white-space:nowrap}.arx-port-cash small,.arx-port-cash b{margin:0!important}',
    '.arx-port-cash{flex:0 0 auto;display:flex!important;align-items:center;gap:9px;margin:0!important;padding:0 12px!important;border-left:1px solid rgba(166,230,244,.18);white-space:nowrap}.arx-port-cash span{display:block}.arx-port-cash small,.arx-port-cash b{display:block;margin:0!important}.arx-port-cash button{padding:6px 8px;border:1px solid rgba(246,211,101,.42);border-radius:6px;background:rgba(246,211,101,.08);color:#f6d365;font-size:6px;font-weight:900;letter-spacing:.08em;cursor:pointer}.arx-funding-card{width:min(720px,100%)}.arx-web-preview{margin:17px 0;padding:10px 12px;border:1px solid rgba(125,211,252,.28);border-radius:8px;background:rgba(20,75,96,.38)}.arx-web-preview b,.arx-web-preview span{display:block}.arx-web-preview b{color:#7dd3fc;font-size:8px;letter-spacing:.1em}.arx-web-preview span{margin-top:4px;color:#9fc6d1;font-size:8px;line-height:1.4}.arx-funding-balance{margin:14px 0;text-align:center}.arx-funding-balance small,.arx-funding-balance b{display:block}.arx-funding-balance small{color:#82afbc;font-size:7px;letter-spacing:.12em}.arx-funding-balance b{margin-top:4px;color:#f6d365;font:800 25px Georgia,serif}.arx-funding-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:17px 0}.arx-funding-grid article{padding:16px 12px;border:1px solid rgba(166,230,244,.18);border-radius:10px;background:rgba(23,67,83,.46);text-align:center}.arx-funding-grid article.featured{border-color:rgba(246,211,101,.55);box-shadow:inset 0 0 0 1px rgba(246,211,101,.12)}.arx-funding-grid small,.arx-funding-grid b,.arx-funding-grid span{display:block}.arx-funding-grid small{color:#7dd3fc;font-size:7px;font-weight:900;letter-spacing:.1em}.arx-funding-grid b{margin:10px 0 2px;color:#fff4bd;font:800 23px Georgia,serif}.arx-funding-grid span{color:#8fb7c2;font-size:8px}.arx-funding-grid button{width:100%;margin-top:13px;padding:10px;border:0;border-radius:7px;background:#f6d365;color:#17323b;font-size:10px;font-weight:900;cursor:pointer}.arx-funding-grid button:disabled{background:#315766;color:#7896a0}.arx-funding-note{color:#789eaa!important;font-size:8px!important;text-align:center}',
    'funding styles'
)

replace_once(
    '@media(max-width:760px){#arx-dev-toggle{right:8px;bottom:8px}.arx-relocation-row{grid-template-columns:1fr}.arx-relocation-row button{width:100%}}',
    '@media(max-width:760px){#arx-dev-toggle{right:8px;bottom:8px}.arx-relocation-row{grid-template-columns:1fr}.arx-relocation-row button{width:100%}.arx-port-navrow{display:block}.arx-port-cash{justify-content:space-between!important;padding:8px 0!important;border-left:0;border-bottom:1px solid rgba(166,230,244,.14)}.arx-funding-grid{grid-template-columns:1fr}}',
    'funding responsive styles'
)

path.write_text(text)

index = Path('index.html')
html = index.read_text()
old = 'expedition.js?v=expedition-22c-visuals'
new = 'expedition.js?v=expedition-22f-funding'
if html.count(old) != 1:
    raise SystemExit(f'cache bust: expected exactly one match, found {html.count(old)}')
index.write_text(html.replace(old, new, 1))
