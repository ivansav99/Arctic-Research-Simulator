from pathlib import Path
p=Path('tools/ars_aug13_phone2.py')
s=p.read_text()
start="# Add navigation readouts after the minimap drawing pass.\n"
end="# Expanded mini map behaves like a modal and pauses the simulation.\n"
a=s.index(start); b=s.index(end,a)
replacement=r'''# Add navigation readouts after the minimap drawing pass.
marker=''' + "'''" + r'''    mini.fillStyle='#e84f4f';mini.strokeStyle='rgba(255,240,225,.9)';mini.lineWidth=.7;cityLabels.forEach(city=>{const w=polar(city.lat,city.lon),dot=project(w.x,w.y);if(Math.hypot(dot.x-c,dot.y-c)>radius+3)return;mini.beginPath();mini.arc(dot.x,dot.y,1.8,0,Math.PI*2);mini.fill();mini.stroke();});const p=project(state.x,state.y);mini.fillStyle='#f9d55d';mini.shadowColor='#fff3a4';mini.shadowBlur=7;mini.beginPath();mini.arc(p.x,p.y,3.7,0,Math.PI*2);mini.fill();mini.shadowBlur=0;mini.strokeStyle='#fff';mini.lineWidth=1;mini.stroke();const viewW=Math.min(radius*2,width/scale/worldRadius*radius),viewH=Math.min(radius*2,height/scale/worldRadius*radius);mini.strokeStyle='rgba(255,243,164,.68)';mini.lineWidth=.8;mini.strokeRect(p.x-viewW/2,p.y-viewH/2,viewW,viewH);mini.restore();mini.strokeStyle='rgba(218,247,252,.6)';mini.lineWidth=1;mini.beginPath();mini.arc(c,c,radius,0,Math.PI*2);mini.stroke();
''' + "'''" + r'''
readouts=marker+''' + "'''" + r'''    const currentPos=unpolar(state.x,state.y),ew=currentPos.lon<0?'W':'E',weather=currentWeather(),profile=iceNavigationProfileAt(state.x,state.y),course=state.commandActive?((Math.atan2(state.tx-state.x,state.ty-state.y)*180/Math.PI+360)%360):null;if(ui.miniLocation)ui.miniLocation.textContent=locationName(currentPos.lat,currentPos.lon);if(ui.miniPosition)ui.miniPosition.textContent=`${currentPos.lat.toFixed(2)}°N ${Math.abs(currentPos.lon).toFixed(2)}°${ew}`;if(ui.miniCourse)ui.miniCourse.textContent=course==null?'STOPPED':`${Math.round(course).toString().padStart(3,'0')}°`;if(ui.miniIce)ui.miniIce.textContent=iceStatusText(profile,state.ramming);if(ui.miniWeather)ui.miniWeather.textContent=weather.type==='clear'?'CLEAR':weather.label.toUpperCase();
''' + "'''" + r'''
g=replace_once(g,marker,readouts,'minimap readouts')

'''
s=s[:a]+replacement+s[b:]
p.write_text(s)
print('fixed minimap patch quoting')
