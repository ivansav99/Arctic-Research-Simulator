from pathlib import Path

game_path=Path('game.js')
index_path=Path('index.html')
game=game_path.read_text()
index=index_path.read_text()

def replace_once(text,old,new,label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    return text.replace(old,new,1)

old_start="""  function startNewGame(){
    if(state.started){try{sessionStorage.setItem(AUTO_NEW_KEY,'1');}catch(error){}location.reload();return;}
    try{localStorage.removeItem(SAVE_KEYS.auto);}catch(error){}menuOpen=false;ui.welcome.classList.add('hidden');analytics.track('new_game');requestExpeditionStart();
  }"""
new_start="""  function beginFreshNewGame(){
    try{localStorage.removeItem(SAVE_KEYS.auto);}catch(error){}
    menuOpen=false;ui.welcome.classList.add('hidden');
    try{requestExpeditionStart();}
    catch(error){console.error('NEW GAME START FAILED',error);menuOpen=true;ui.welcome.classList.remove('hidden');showToast('NEW GAME COULD NOT START · RELOAD AND TRY AGAIN',3600);return false;}
    try{analytics.track('new_game');}catch(error){}
    return true;
  }
  function startNewGame(){
    const params=new URLSearchParams(location.search);
    if(params.get('new')==='1')return beginFreshNewGame();
    try{const url=new URL(location.href);url.searchParams.set('new','1');url.searchParams.set('build','23h');location.replace(url.href);}
    catch(error){beginFreshNewGame();}
  }"""
game=replace_once(game,old_start,new_start,'replace new game startup')

old_auto="  try{if(sessionStorage.getItem(AUTO_NEW_KEY)==='1'){sessionStorage.removeItem(AUTO_NEW_KEY);setTimeout(startNewGame,0);}}catch(error){}"
new_auto="""  try{const params=new URLSearchParams(location.search);if(params.get('new')==='1'){setTimeout(()=>{const clean=new URL(location.href);clean.searchParams.delete('new');clean.searchParams.delete('build');history.replaceState(null,'',clean.pathname+clean.search+clean.hash);beginFreshNewGame();},0);}}catch(error){console.error('AUTO NEW GAME START FAILED',error);}"""
game=replace_once(game,old_auto,new_auto,'replace auto new path')

# Sound should never be able to prevent the New Game handler from running.
old_click="document.getElementById('start-button').addEventListener('click',()=>{sound.unlock();startNewGame();});"
new_click="document.getElementById('start-button').addEventListener('click',()=>{startNewGame();try{sound.unlock();}catch(error){}});"
game=replace_once(game,old_click,new_click,'new game click order')

old_help="document.getElementById('help-start-button').addEventListener('click',()=>{sound.unlock();state.started?resumeGame():startNewGame();});"
new_help="document.getElementById('help-start-button').addEventListener('click',()=>{state.started?resumeGame():startNewGame();try{sound.unlock();}catch(error){}});"
game=replace_once(game,old_help,new_help,'help start click order')

index=index.replace('expedition-23g-port-wildlife','expedition-23h-startup')
if index.count('expedition-23h-startup')<3:
    raise SystemExit('expected cache-bust tags were not updated')

for marker in ['beginFreshNewGame','NEW GAME START FAILED',"url.searchParams.set('new','1')"]:
    if marker not in game: raise SystemExit(f'missing marker {marker}')

game_path.write_text(game)
index_path.write_text(index)
