'use strict';
const $=id=>document.getElementById(id);
const sample=`Finished comparing the two watering schedules.
The weekend plan uses the smaller pot.
Still need to check whether the balcony gets four hours of sun.
Waiting for the soil mix to arrive on Tuesday.
The seed tray measurements are already written down.
Next: sketch where the three pots will fit.`;
const categories={next:'Still to do',waiting:'Can wait',done:'Already done',context:'Keep in mind'};
let card=null,busy=false,unsaved=false;
const storeKey='pausedock.saved.v1';
function status(text,error=false){$('status').textContent=text;$('status').classList.toggle('error',error);}
function count(){const n=$('notes').value.split('\n').filter(x=>x.trim()).length;$('count').textContent=`${n} notes`;}
function loadSample(){if(busy)return;$('notes').value=sample;$('title').value='Balcony garden plan';count();}
function resetCard(){card=null;$('card').hidden=true;$('empty').hidden=false;}
function setRestart(){const note=card.notes.find(n=>n.id===card.restart_id);$('restart-text').textContent=note?note.text:'No unfinished step found. You can put this down.';$('restart-source').textContent=note?`Original note ${note.id}`:'No new task invented';}
function render(){
 $('empty').hidden=true;$('card').hidden=false;$('card-title').textContent=card.title;setRestart();$('groups').replaceChildren();
 for(const [bucket,label] of Object.entries(categories)){
  const notes=card.notes.filter(n=>n.bucket===bucket);if(!notes.length)continue;
  const group=document.createElement('section');group.className='group';const h=document.createElement('h4');h.textContent=`${label} · ${notes.length}`;group.append(h);
  for(const note of notes){
   const row=document.createElement('div');row.className='note-row';const id=document.createElement('span');id.className='note-id';id.textContent=note.id;
   const text=document.createElement('span');text.className='note-text';text.textContent=note.text;
   if(bucket==='next'&&note.id!==card.restart_id){const pick=document.createElement('button');pick.className='text-button pick-step';pick.textContent='Start here';pick.setAttribute('aria-label',`Start with ${note.id}`);pick.addEventListener('click',()=>{card.restart_id=note.id;card.reviewed_by_user=true;render();status('Return step updated. Save again to keep this choice.');});text.append(' ',pick);}
   const select=document.createElement('select');select.setAttribute('aria-label',`Category for ${note.id}`);
   for(const [value,name] of Object.entries(categories)){const option=document.createElement('option');option.value=value;option.textContent=name;option.selected=note.bucket===value;select.append(option);}
   select.addEventListener('change',()=>{note.bucket=select.value;if(!card.notes.some(n=>n.id===card.restart_id&&n.bucket==='next'))card.restart_id=card.notes.find(n=>n.bucket==='next')?.id??null;card.reviewed_by_user=true;render();status('Category updated. Save again to keep this change.');});
   row.append(id,text,select);group.append(row);
  }$('groups').append(group);
 }
 $('run-detail').textContent=`Local Qwen2.5 · ${card.run?.elapsed_seconds??'?'} seconds · input wording preserved`;
 $('save').textContent='Save on this browser';
}
function readSaved(){try{const value=JSON.parse(localStorage.getItem(storeKey)||'[]');return Array.isArray(value)?value.filter(c=>c&&Array.isArray(c.notes)&&typeof c.title==='string'&&c.notes.every(n=>typeof n.id==='string'&&typeof n.text==='string'&&n.text.length<=500&&Object.hasOwn(categories,n.bucket))).slice(0,8):[];}catch{return [];}}
function renderSaved(){const items=readSaved();$('saved-section').hidden=!items.length;$('saved-list').replaceChildren();for(const item of items){const wrap=document.createElement('div');wrap.className='saved-item';const open=document.createElement('button');open.textContent=item.title;open.addEventListener('click',()=>{if(busy)return;card=item;$('title').value=item.title;$('notes').value=item.notes.map(n=>n.text).join('\n');count();render();status('Opened a card saved on this browser.');});const remove=document.createElement('button');remove.textContent='×';remove.setAttribute('aria-label',`Delete saved card ${item.title}`);remove.addEventListener('click',()=>{try{localStorage.setItem(storeKey,JSON.stringify(readSaved().filter(c=>c.saved_id!==item.saved_id)));renderSaved();status('Saved copy deleted from this browser.');}catch{status('This browser could not update its saved cards.',true);}});wrap.append(open,remove);$('saved-list').append(wrap);}}
$('example').addEventListener('click',loadSample);$('notes').addEventListener('input',count);
$('park').addEventListener('click',async()=>{
 if(busy)return;busy=true;$('park').disabled=true;$('notes').disabled=true;$('example').disabled=true;$('title').disabled=true;resetCard();let seconds=0;
 status('Sorting your notes on this device…');const timer=setInterval(()=>{seconds++;status(`Sorting your notes on this device… ${seconds}s. First runs can take longer.`);},1000);
 try{const response=await fetch('/api/park',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({notes:$('notes').value})});const result=await response.json();if(!response.ok)throw new Error(result.error||'The local run did not finish.');card={...result,title:$('title').value.trim()||'A place to return',created_at:new Date().toISOString(),saved_id:crypto.randomUUID()};render();status('Your place is kept in this tab. Review the categories, then take a break.');}
 catch(error){status(error.message,true);}
 finally{clearInterval(timer);busy=false;$('park').disabled=false;$('notes').disabled=false;$('example').disabled=false;$('title').disabled=false;}
});
$('download').addEventListener('click',()=>{if(!card)return;let text=`# ${card.title}\n\nPauseDock return card\n\n`;const note=card.notes.find(n=>n.id===card.restart_id);text+=`## When I return\n${note?`[${note.id}] ${note.text}`:'No unfinished task identified.'}\n\n`;for(const [bucket,name]of Object.entries(categories)){text+=`## ${name}\n`;text+=card.notes.filter(n=>n.bucket===bucket).map(n=>`- [${n.id}] ${n.text}`).join('\n')+'\n\n';}text+='AI classified these notes; original wording is preserved. Review categories before relying on them.\n';const url=URL.createObjectURL(new Blob([text],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='pausedock-return-card.md';a.click();URL.revokeObjectURL(url);status('Card downloaded. No copy was saved by the server.');});
$('save').addEventListener('click',()=>{if(!card)return;try{localStorage.setItem(storeKey,JSON.stringify([card,...readSaved().filter(c=>c.saved_id!==card.saved_id)].slice(0,8)));renderSaved();$('save').textContent='Saved here ✓';status('Saved on this browser. Use × below to delete a saved copy.');}catch{status('This browser cannot save the card. Download it instead.',true);}});
$('clear').addEventListener('click',()=>{if(busy)return;$('notes').value='';$('title').value='';resetCard();count();status('This session is clear. Saved cards remain below until you delete them.');});
loadSample();renderSaved();
