from pathlib import Path

p=Path('expedition.js')
text=p.read_text()
required=['function activeGrantCard','function collectingGrantCard','function relocationPorts','function capturePortView','function resupplyAllQuote']
if any(name in text for name in required):
    raise SystemExit('Expected swallowed helper block to be absent before restoration')
needle='  function portVesselDashboardMarkup(resources,ship,quote) {'
if text.count(needle)!=1:
    raise SystemExit(f'portVesselDashboardMarkup marker count={text.count(needle)}')
block=r'''  function activeGrantCard(item) {
    const missing=!eligible(item), projection=missionFoodProjection(item);
    const recovery=!!item.deploymentId,teamPickup=item.missionMode==='staged-recovery';
    return `<article class="arx-card grant"><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${recovery?'RETURN VISIT REQUIRED':missing?'CAPABILITY CURRENTLY MISSING':'READY'} · ${Math.round(item.workHours)} PERSON-HOURS</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p><h4 class="arx-mini-label">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}<h4 class="arx-mini-label">EQUIPMENT USED</h4>${operationEquipmentMarkup(item)}<div class="arx-stats"><span>${item.data} data</span><span>Payment ${cash(item.reward)} on completion</span>${item.iceValueMultiplier>1?`<span>ICE DATA VALUE ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>~${projection.days} field days</span><span>Projected food ${Math.max(0,Math.floor(projection.remaining))}%</span></div><div class="arx-grant-actions"><button class="danger" data-arx-action="drop-grant" data-id="${item.id}" ${recovery&&!teamPickup?'disabled':''}>${recovery?(teamPickup?'DROP RETURN PICKUP':'DEPLOYED EQUIPMENT MUST BE RECOVERED'):'DROP RESEARCH GRANT'}</button></div></article>`;
  }
  function collectingGrantCard(item) {
    const teamPickup=item.recoveryMode==='staged-recovery';
    return `<article class="arx-card grant"><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${teamPickup?'FIELD TEAM ASHORE · RETURN VISIT PENDING':'INSTRUMENT COLLECTING · RETURN VISIT PENDING'}</small></div><em>${Math.max(0,Math.ceil(item.remainingDays||0))} d</em></div><p>${teamPickup?'The shore party is working independently. You can return for them when ready, or hand their pickup to local logistics and drop the return visit.':'Autonomous observations are underway. This research grant continues to occupy one scientist-led grant slot until recovery.'}</p>${teamPickup?`<button class="danger" data-arx-action="abandon-deployment" data-id="${item.id}">DROP RETURN PICKUP</button>`:'<button disabled>RECOVERY WINDOW NOT OPEN YET</button>'}</article>`;
  }

  function relocationPorts(force=false) { const key=`${state.currentVessel}:${Math.floor((state.elapsedDays||0)*2)}`;if(!force&&relocationPortCache.key===key)return relocationPortCache.ports;const ports=(callbacks.getRelocationPorts?.()||[]).map(item=>({...item,id:item.id||slug(item.name)}));relocationPortCache={key,ports};return ports; }
  function emergencyRelocationAllowed() {
    if(playerCareerLevel()>=2||['icebreaker','nuclear'].includes(state.currentVessel))return false;
    const currentId=normalizedPortId(state.port),current=relocationPorts().find(item=>item.id===currentId);
    return !!current?.frozen;
  }
  function relocationUnlocked() { return playerCareerLevel()>=2||emergencyRelocationAllowed(); }
  function relocationPanelMarkup() {
    const ports=relocationPorts(),emergency=playerCareerLevel()<2&&emergencyRelocationAllowed();
    if (!relocationUnlocked()) return '<div class="arx-empty"><b>POSTDOCTORAL CAREER REQUIRED</b><p>Relocating the expedition home port unlocks when the Chief Scientist reaches postdoctoral status.</p></div>';
    const currentId=normalizedPortId(state.port),homeId=state.homePortId||'longyearbyen';
    return `<p class="arx-help">${emergency?'EMERGENCY RELOCATION · Your current port is frozen in, so relocation is temporarily available before postdoctoral status. ':''}Move the entire expedition and vessel to another Arctic home port for ${cash(RELOCATION_COST)}. Frozen destination ports remain selectable only aboard an icebreaker.</p><div class="arx-relocation-list">${ports.map(port=>{const current=port.id===currentId,home=port.id===homeId,frozen=!!port.frozen,available=port.relocationAvailable!==false,poor=state.money<RELOCATION_COST,blocked=frozen&&!available;return `<article class="arx-relocation-row ${blocked?'frozen':''}"><div><b>${escapeHtml(port.name)}</b><small>${escapeHtml(port.country||'Arctic')} ${home?'· CURRENT HOME PORT':''}</small></div><span>${frozen?`FROZEN IN · ${escapeHtml(port.iceLabel||'SEA ICE')}${available?' · ICEBREAKER ACCESS':''}`:escapeHtml(port.iceLabel||'OPEN')}</span><button data-arx-action="relocate-port" data-id="${escapeHtml(port.id)}" ${current||blocked||poor?'disabled':''}>${current?'CURRENT PORT':blocked?'UNAVAILABLE':poor?'INSUFFICIENT CASH':`RELOCATE · ${cash(RELOCATION_COST)}`}</button></article>`;}).join('')}</div>`;
  }
  function relocateHomePort(id) {
    if (!relocationUnlocked()) { toast('POSTDOCTORAL CAREER REQUIRED'); return; }
    const port=relocationPorts().find(item=>item.id===id); if(!port) return;
    if (port.frozen&&port.relocationAvailable===false) { toast(`${port.name.toUpperCase()} · PORT CURRENTLY FROZEN IN`); return; }
    if (state.money<RELOCATION_COST) { toast(`RELOCATION REQUIRES ${cash(RELOCATION_COST)}`); return; }
    const oldMoney=state.money; adjustMoney(-RELOCATION_COST); state.homePortId=id;
    closePort(); relocationPortCache={key:null,ports:[]};
    const moved=callbacks.relocateToPort?.(id);
    if (!moved) { state.money=oldMoney; cashAnimation={from:oldMoney-RELOCATION_COST,to:oldMoney}; toast('RELOCATION FAILED · PORT APPROACH UNAVAILABLE'); changed(); return; }
    addLog(`Home port relocated to ${port.name}, ${port.country||'Arctic'} · ${cash(RELOCATION_COST)}.`);
    toast(`HOME PORT RELOCATED · ${port.name.toUpperCase()}`); callbacks.onStateChange?.();
  }

  function capturePortView() {
    if (!root) return;
    const card=root.querySelector('.arx-port-card'), tabs=card?.querySelector('.arx-tabs');
    if (card) portScrollTop=card.scrollTop;
    if (tabs) portTabsScrollLeft=tabs.scrollLeft;
    const opened=card?.querySelector('[data-arx-store-details][open]');
    openStoreDetail=opened?.dataset.arxStoreDetails || null;
  }
  function resupplyAllQuote(resources,ship=vessel()) {
    const fuelMissing=ship.nuclearFuel?0:Math.max(0,100-resources.fuel);
    const foodMissing=Math.max(0,100-resources.food);
    const supplyMissing=Math.max(0,ship.supplyCapacity-state.supplies);
    return Math.round(fuelMissing/10*fuelStepCost(ship)+foodMissing/10*foodStepCost(ship)+supplyMissing/10*2500);
  }
'''
p.write_text(text.replace(needle,block+needle,1))
print('restored port helper block from 0d1c51c')
