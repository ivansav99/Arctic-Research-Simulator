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
})();
