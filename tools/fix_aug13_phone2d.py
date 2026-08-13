from pathlib import Path
p=Path('tools/ars_aug13_phone2.py')
s=p.read_text()
start="# Random opportunities can still open on arrival without ever becoming the arrow-guided selected grant.\n"
end="# Manual navigation clears a pending popup destination.\n"
a=s.index(start); b=s.index(end,a)
replacement=r'''# Random opportunities can still open on arrival without ever becoming the arrow-guided selected grant.
old_nav="  function updateResearchNavigation(){const target=selectedResearchTarget();if(!target){pendingResearchTargetId=null;research?.updateNavigation?.(null);return;}const item=researchTargetWorld(target),dx=item.w.x-state.x,dy=item.w.y-state.y,bearing=(Math.atan2(dx,dy)*180/Math.PI+360)%360;research?.updateNavigation?.({id:target.id,target,distanceKm:item.distance,bearingDeg:bearing});if(pendingResearchTargetId===target.id&&item.distance<=RESEARCH_INTERACTION_KM&&!research?.isBusy?.()){pendingResearchTargetId=null;state.tx=state.x;state.ty=state.y;state.commandActive=false;state.moving=false;state.ramming=false;research?.openTarget?.(target.id,{distanceKm:item.distance,atSite:true,target});}}"
new_nav="""  function updateResearchNavigation(){
    if(pendingResearchTargetId){const pending=researchTargets().find(item=>item.id===pendingResearchTargetId);if(!pending){pendingResearchTargetId=null;pendingResearchArrival=null;}else if(pendingResearchArrival&&!research?.isBusy?.()){const remaining=Math.hypot(state.x-pendingResearchArrival.x,state.y-pendingResearchArrival.y);if(remaining<=RESEARCH_INTERACTION_KM){pendingResearchTargetId=null;pendingResearchArrival=null;state.tx=state.x;state.ty=state.y;state.commandActive=false;state.moving=false;state.ramming=false;research?.openTarget?.(pending.id,{distanceKm:remaining,atSite:true,target:pending});}}}
    const target=selectedResearchTarget();if(!target){research?.updateNavigation?.(null);return;}const item=researchTargetWorld(target),dx=item.w.x-state.x,dy=item.w.y-state.y,bearing=(Math.atan2(dx,dy)*180/Math.PI+360)%360;research?.updateNavigation?.({id:target.id,target,distanceKm:item.distance,bearingDeg:bearing});
  }"""
g=replace_once(g,old_nav,new_nav,'research navigation arrival')
g=replace_once(g,"pendingResearchTargetId=target.id;setWorldDestination(destination.x,destination.y);","pendingResearchTargetId=target.id;pendingResearchArrival={id:target.id,x:destination.x,y:destination.y};setWorldDestination(destination.x,destination.y);",'pending arrival point')
'''
s=s[:a]+replacement+s[b:]
p.write_text(s)
print('narrowed research navigation patch boundary')
