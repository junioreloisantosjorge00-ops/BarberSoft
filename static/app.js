const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const toast=(m,ok)=>{const d=document.createElement('div');d.className='toast'+(ok?' ok':'');d.textContent=m;$('#toasts').append(d);setTimeout(()=>d.remove(),5000)};
$('#burger').onclick=()=>$('#menu').classList.toggle('open');
// barra de progreso, nav y botón subir
const nav=$('.nav'),bar=$('#progress'),top_=$('#top');
addEventListener('scroll',()=>{const y=scrollY,h=document.documentElement.scrollHeight-innerHeight;nav.classList.toggle('sm',y>40);bar.style.width=(h>0?y/h*100:0)+'%';top_.classList.toggle('show',y>500)},{passive:true});
top_.onclick=()=>scrollTo({top:0,behavior:'smooth'});
// aparecer al hacer scroll + contadores
const count=el=>{const n=+el.dataset.n,t0=performance.now();(function f(t){const p=Math.min((t-t0)/1200,1);el.textContent=Math.round(n*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(f)})(t0)};
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');if(e.target.dataset.n)count(e.target);io.unobserve(e.target)}}),{threshold:.12});
$$('.card,.post,.stats b,.stats div,.form,.check li').forEach((el,i)=>{if(!el.dataset.n)el.classList.add('reveal');el.style.transitionDelay=(i%5)*70+'ms';io.observe(el)});
// inclinación 3D en tarjetas
$$('a.card').forEach(c=>{c.addEventListener('mousemove',e=>{const r=c.getBoundingClientRect();c.style.setProperty('--ry',((e.clientX-r.left)/r.width-.5)*12+'deg');c.style.setProperty('--rx',(.5-(e.clientY-r.top)/r.height)*12+'deg')});c.addEventListener('mouseleave',()=>{c.style.setProperty('--rx','0deg');c.style.setProperty('--ry','0deg')})});
// parallax del hero
const hero=$('#hero');if(hero)hero.addEventListener('mousemove',e=>{const x=e.clientX/innerWidth-.5,y=e.clientY/innerHeight-.5;$$('.fl').forEach(f=>{const d=+f.dataset.d;f.style.translate=`${x*d}px ${y*d}px`})});
// texto que se escribe solo
const ty=$('#typed');if(ty){const W=['citas','clientes','productos','comisiones','ventas','facturas'];let i=0,j=0,del=false;(function t(){const w=W[i];ty.textContent=w.slice(0,j);if(!del&&j===w.length){del=true;return setTimeout(t,1400)}if(del&&j===0){del=false;i=(i+1)%W.length}j+=del?-1:1;setTimeout(t,del?45:90)})()}
// me gusta y comentarios (se guardan en la base de datos)
const api=async(u,b)=>{const r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b||{})});const d=await r.json().catch(()=>({}));if(r.status===401){toast('Inicia sesión para participar 🔒');setTimeout(()=>location=window.LOGIN,1200)}return r.ok?d:null};
const like=async p=>{const b=$('.like',p),d=await api('/api/like/'+p.dataset.id);if(!d)return;b.classList.toggle('on',d.liked);$('.hi',b).textContent=d.liked?'♥':'♡';$('.ln',b).textContent=d.n;b.classList.remove('pop');void b.offsetWidth;b.classList.add('pop');if(d.liked){const h=$('.heart',p);if(h){h.classList.remove('pop');void h.offsetWidth;h.classList.add('pop')}}};
const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
document.addEventListener('click',async e=>{const p=e.target.closest('.post');if(!p)return;
 if(e.target.closest('.like'))like(p);
 if(e.target.closest('.ctog')){$('.cm',p).classList.toggle('open')}
 if(e.target.closest('.cdel')){const c=e.target.closest('.c'),d=await api('/api/comentario/'+c.dataset.id+'/borrar');if(d){c.remove();const n=$('.cn',p);n.textContent=Math.max(0,+n.textContent-1)}}});
document.addEventListener('dblclick',e=>{const p=e.target.closest('.post');if(p&&e.target.closest('.pimg'))like(p)});
document.addEventListener('submit',async e=>{const f=e.target.closest('.cf');if(!f)return;e.preventDefault();const p=f.closest('.post'),i=$('input',f),t=i.value.trim();if(!t)return;
 const d=await api('/api/comentar/'+p.dataset.id,{body:t});if(!d)return;i.value='';
 const c=document.createElement('div');c.className='c';c.dataset.id=d.id;
 c.innerHTML=`<div class="av sm">${esc(d.name)[0]}</div><div class="cb"><b>${esc(d.name)}</b>${d.role==='barbero'?' <em>💈 barbero</em>':''} <small>${d.created}</small><p>${esc(d.body)}</p></div><button class="cdel" title="Borrar">✕</button>`;
 $('.cl',p).append(c);const n=$('.cn',p);n.textContent=+n.textContent+1;toast('Comentario publicado ✅',1)});
// chatbot
const R=[[/hola|buenas|hey/,'¡Hola! Soy BarberBot ✂ Pregúntame por barberos, ofertas, comentarios, cuentas o facturas.'],
[/cuenta|registr|crear/,'Crea tu cuenta de cliente en /registro o de barbero en /admin/registro.'],
[/coment|gust|like/,'En Comunidad puedes dar me gusta y comentar cada publicación (necesitas iniciar sesión).'],
[/barbero|barber[ií]a|ubicaci|donde|cerca/,'En Barberos ves cada barbería con mapa y botón de WhatsApp.'],
[/oferta|promo|descuento/,'Las ofertas están en Comunidad → 🔥 Ofertas, publicadas por los barberos.'],
[/corte|estilo|fade|peinado/,'Mira Comunidad → ✂ Cortes para ver fotos de los trabajos.'],
[/whatsapp|cita|reserv/,'Entra al perfil del barbero y toca “WhatsApp” para reservar tu cita.'],
[/factura|ticket|imprim/,'Los barberos facturan desde su panel: crean, editan, borran e imprimen un ticket pequeño de 80 mm.'],
[/crm/,'El CRM del panel guarda tus clientes e interesados con estado y notas.'],
[/precio|plan|cuesta|costo/,'Los planes y precios se definirán antes del lanzamiento. Escríbenos para una cotización.'],
[/gracias/,'¡Con gusto! 💈']];
const box=$('#botmsgs'),add=(t,c)=>{const d=document.createElement('div');d.className='m '+c;d.textContent=t;box.append(d);box.scrollTop=1e9;return d};
const ask=t=>{add(t,'u');const w=add('','t b');w.innerHTML='<i></i><i></i><i></i>';const r=R.find(x=>x[0].test(t.toLowerCase()));setTimeout(()=>{w.className='m b';w.textContent=r?r[1]:'No estoy seguro 🤔 Prueba con: barberos, ofertas, comentarios, cuenta o factura.'},700)};
['Ofertas','Barberos','Crear cuenta','Facturas'].forEach(t=>{const b=document.createElement('button');b.textContent=t;b.onclick=()=>ask(t);$('#chips').append(b)});
$('#botbtn').onclick=()=>{const b=$('#botbox');b.hidden=!b.hidden;if(!box.children.length)add('¡Hola! Soy BarberBot ✂ ¿En qué te ayudo?','b')};
$('#botx').onclick=()=>$('#botbox').hidden=true;
$('#botform').onsubmit=e=>{e.preventDefault();const t=$('#botin').value.trim();if(!t)return;$('#botin').value='';ask(t)};
// facturas
const rows=$('#rows');if(rows){const calc=()=>{let s=0;$$('.row').forEach(r=>{const i=r.querySelectorAll('input');s+=(+i[1].value||0)*(+i[2].value||0)});if($('[name=itbis]').checked)s*=1.18;$('#tot').textContent=s.toFixed(2)};
 $('#fform').addEventListener('input',calc);$('#addrow').onclick=()=>{rows.append(rows.firstElementChild.cloneNode(true));rows.lastElementChild.querySelectorAll('input').forEach(i=>i.value='')};
 rows.addEventListener('click',e=>{if(e.target.classList.contains('rm')&&rows.children.length>1){e.target.parentElement.remove();calc()}});calc()}

// los videos se reproducen solos (sin sonido) al verse y se pausan al salir
const vio=new IntersectionObserver(es=>es.forEach(e=>{const v=e.target;if(e.isIntersecting&&e.intersectionRatio>.6){v.muted=true;v.play().catch(()=>{})}else v.pause()}),{threshold:[0,.6]});
$$('.pvid video').forEach(v=>vio.observe(v));
