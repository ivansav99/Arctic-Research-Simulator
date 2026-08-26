(()=>{
  'use strict';
  const PHOTO_BUILD='expedition-23q-photo-integration';
  const KEY='arctic-research-photo-integration-build';
  const SAVE_KEYS=['arctic-research-save-auto-v1','arctic-research-save-slot-1-v1','arctic-research-save-slot-2-v1','arctic-research-save-slot-3-v1'];
  try{
    if(localStorage.getItem(KEY)!==PHOTO_BUILD){
      SAVE_KEYS.forEach(key=>localStorage.removeItem(key));
      localStorage.removeItem('arctic-research-start-new-v1');
      localStorage.setItem(KEY,PHOTO_BUILD);
    }
  }catch(error){}

  // 23ab: Advanced saves created by the previous fallback generator may contain
  // unaccepted professor/postdoc offers with no real equipment. Clear only
  // those stale offer cards during restore so the current port immediately
  // rebuilds them with the equipment-aware generator. Active grants are never
  // touched here.
  addEventListener('DOMContentLoaded',()=>{
    const api=window.ArcticResearch;
    if(!api||api.__equipmentOfferRestorePatch||typeof api.restoreCheckpoint!=='function')return;
    api.__equipmentOfferRestorePatch=true;
    const restore=api.restoreCheckpoint.bind(api);
    const patchedRestore=snapshot=>{
      let next=snapshot;
      try{
        const chief=snapshot?.scientists?.find(item=>item.isPlayer)||snapshot?.scientists?.[0];
        const advanced=chief&&['postdoc','professor'].includes(chief.career);
        const stale=advanced&&(snapshot?.offers||[]).some(item=>String(item?.templateId||'').startsWith('fallback-')&&!(item?.equipment||[]).length);
        if(stale){
          next=JSON.parse(JSON.stringify(snapshot));
          next.offers=[];
          next.grantOfferCycle=null;
        }
      }catch(error){}
      return restore(next);
    };
    api.restoreCheckpoint=patchedRestore;
    api.restoreSnapshot=patchedRestore;
  });
})();
