# -*- coding: utf-8 -*-
"""Self-contained HTML status page for the ProwlrHub war room."""

STATUS_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ProwlrHub — War Room Status</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{
    background:#0a0a0f;color:#e0e0e0;
    font-family:'SF Mono','Cascadia Code','Fira Code',monospace;
    min-height:100vh;padding:1.5rem;
  }
  a{color:#14b8a6;text-decoration:none}
  a:hover{text-decoration:underline}

  /* Header */
  .header{text-align:center;margin-bottom:2rem}
  .header h1{font-size:1.8rem;color:#14b8a6;letter-spacing:0.15em}
  .header .subtitle{color:#888;font-size:0.85rem;margin-top:0.3rem}

  /* Stats grid */
  .stats{
    display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
    gap:1rem;margin-bottom:2rem;
  }
  .card{
    background:#12121a;border:1px solid #1e1e2e;border-radius:10px;
    padding:1.2rem;text-align:center;
  }
  .card .label{color:#888;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em}
  .card .value{font-size:2rem;color:#14b8a6;font-weight:700;margin:0.3rem 0}
  .card .sub{color:#666;font-size:0.75rem}

  /* Section */
  .section{margin-bottom:2rem}
  .section-title{
    color:#14b8a6;font-size:1rem;margin-bottom:0.8rem;
    border-bottom:1px solid #1e1e2e;padding-bottom:0.4rem;
  }

  /* Agents list */
  .agent-item{
    display:flex;align-items:center;gap:0.8rem;
    padding:0.6rem 0.8rem;background:#12121a;border:1px solid #1e1e2e;
    border-radius:8px;margin-bottom:0.5rem;flex-wrap:wrap;
  }
  .dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
  .dot-idle{background:#22c55e}
  .dot-working{background:#3b82f6;animation:pulse 1.5s infinite}
  .dot-offline{background:#666}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
  .agent-name{font-weight:600;color:#e0e0e0;font-size:0.9rem}
  .tag{
    background:#1e1e2e;color:#14b8a6;font-size:0.65rem;
    padding:0.15rem 0.5rem;border-radius:4px;
  }

  /* Events list */
  .event-item{
    display:flex;gap:0.8rem;align-items:flex-start;
    padding:0.5rem 0.8rem;background:#12121a;border:1px solid #1e1e2e;
    border-radius:8px;margin-bottom:0.4rem;flex-wrap:wrap;
  }
  .event-time{color:#666;font-size:0.75rem;white-space:nowrap;min-width:140px}
  .event-badge{
    font-size:0.65rem;padding:0.1rem 0.5rem;border-radius:4px;
    text-transform:uppercase;font-weight:600;white-space:nowrap;
  }
  .badge-register{background:#14532d;color:#22c55e}
  .badge-claim{background:#1e3a5f;color:#60a5fa}
  .badge-complete{background:#14532d;color:#4ade80}
  .badge-fail{background:#7f1d1d;color:#f87171}
  .badge-broadcast{background:#4a1d6a;color:#c084fc}
  .badge-default{background:#1e1e2e;color:#888}
  .event-desc{color:#ccc;font-size:0.82rem;flex:1;min-width:150px}

  /* Footer */
  .footer{
    text-align:center;color:#444;font-size:0.75rem;
    margin-top:2rem;padding-top:1rem;border-top:1px solid #1e1e2e;
  }

  /* Empty state */
  .empty{color:#555;font-style:italic;font-size:0.85rem;padding:0.5rem 0}

  /* Loading */
  .loading{color:#555;text-align:center;padding:2rem;font-size:0.9rem}
</style>
</head>
<body>

<div class="header">
  <h1>\U0001f43e PROWLRHUB</h1>
  <div class="subtitle">War Room Status &mdash; Auto-refreshes every 5s</div>
</div>

<div id="content">
  <div class="loading">Connecting to war room&hellip;</div>
</div>

<div class="footer">
  <a href="https://github.com/prowlrbot">ProwlrBot</a> &mdash; Always watching. Always ready.
</div>

<script>
(function(){
  var content = document.getElementById('content');

  function clearEl(el){while(el.firstChild)el.removeChild(el.firstChild);}

  function el(tag, cls, text){
    var e = document.createElement(tag);
    if(cls) e.className = cls;
    if(text) e.textContent = text;
    return e;
  }

  function badgeClass(type){
    var map = {register:'badge-register',claim:'badge-claim',complete:'badge-complete',
               fail:'badge-fail',broadcast:'badge-broadcast'};
    return 'event-badge ' + (map[type] || 'badge-default');
  }

  function agentStatus(agent){
    if(agent.status === 'working') return 'dot-working';
    if(agent.status === 'idle') return 'dot-idle';
    return 'dot-offline';
  }

  function buildStats(health, agents, tasks){
    var grid = el('div','stats');

    // Agents card
    var c1 = el('div','card');
    c1.appendChild(el('div','label','Agents'));
    c1.appendChild(el('div','value', String(health.agents || 0)));
    var working = agents.filter(function(a){return a.status==='working';}).length;
    c1.appendChild(el('div','sub', working + ' working'));
    grid.appendChild(c1);

    // Tasks card
    var c2 = el('div','card');
    c2.appendChild(el('div','label','Tasks'));
    c2.appendChild(el('div','value', String(health.tasks || 0)));
    var pending=0, active=0, done=0;
    tasks.forEach(function(t){
      if(t.status==='pending') pending++;
      else if(t.status==='active') active++;
      else if(t.status==='done') done++;
    });
    c2.appendChild(el('div','sub', pending+' pending / '+active+' active / '+done+' done'));
    grid.appendChild(c2);

    // Room card
    var c3 = el('div','card');
    c3.appendChild(el('div','label','Room'));
    c3.appendChild(el('div','value', health.status === 'ok' ? '\\u2714' : '\\u2718'));
    c3.appendChild(el('div','sub', health.room_id ? health.room_id.substring(0,8) : 'unknown'));
    grid.appendChild(c3);

    return grid;
  }

  function buildAgents(agents){
    var sec = el('div','section');
    sec.appendChild(el('div','section-title','Agents'));
    if(!agents.length){
      sec.appendChild(el('div','empty','No agents registered.'));
      return sec;
    }
    agents.forEach(function(a){
      var row = el('div','agent-item');
      var dot = el('span','dot ' + agentStatus(a));
      row.appendChild(dot);
      row.appendChild(el('span','agent-name', a.name || a.agent_id));
      var caps = a.capabilities || [];
      if(typeof caps === 'string'){
        try{caps = JSON.parse(caps);}catch(e){caps=[caps];}
      }
      caps.forEach(function(c){
        row.appendChild(el('span','tag', c));
      });
      sec.appendChild(row);
    });
    return sec;
  }

  function buildEvents(events){
    var sec = el('div','section');
    sec.appendChild(el('div','section-title','Recent Events'));
    if(!events.length){
      sec.appendChild(el('div','empty','No events yet.'));
      return sec;
    }
    events.forEach(function(ev){
      var row = el('div','event-item');
      var ts = ev.timestamp || ev.created_at || '';
      if(ts.length > 19) ts = ts.substring(0,19).replace('T',' ');
      row.appendChild(el('span','event-time', ts));
      row.appendChild(el('span', badgeClass(ev.event_type || ''), ev.event_type || '?'));
      row.appendChild(el('span','event-desc', ev.description || ev.data || ''));
      sec.appendChild(row);
    });
    return sec;
  }

  function refresh(){
    Promise.all([
      fetch('/health').then(function(r){return r.json();}),
      fetch('/agents').then(function(r){return r.json();}),
      fetch('/board').then(function(r){return r.json();}),
      fetch('/events?limit=10').then(function(r){return r.json();})
    ]).then(function(results){
      var health = results[0];
      var agents = (results[1].agents || []);
      var tasks  = (results[2].tasks  || []);
      var events = (results[3].events || []);

      clearEl(content);
      content.appendChild(buildStats(health, agents, tasks));
      content.appendChild(buildAgents(agents));
      content.appendChild(buildEvents(events));
    }).catch(function(err){
      clearEl(content);
      content.appendChild(el('div','loading','Connection error: ' + err.message));
    });
  }

  refresh();
  setInterval(refresh, 5000);
})();
</script>
</body>
</html>
"""
