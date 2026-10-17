function defaults() { return {version:1,services:{source_types:[],sort_by:'domain'},panel:{remember_selection:true,clear_search_on_open:true}}; }
function initial() { return {ready:false,error:'unavailable',services:[],connections:[],config:defaults(),admin_url:''}; }
function reconcile(previous, incoming) {
  var byId = Object.create(null);
  previous.forEach(function(row) { byId[row.id] = row; });
  return incoming.map(function(row) { var old = byId[row.id]; return old && JSON.stringify(old) === JSON.stringify(row) ? old : row; });
}
function receive(previous, result) {
  if (!result || result.ok !== true || !result.state) {
    return {ready:false,config:result && result.config || previous.config,error:result && result.error || 'unavailable',services:previous.services,connections:previous.connections,admin_url:previous.admin_url};
  }
  var s = result.state;
  return {ready:true,config:result.config || previous.config,error:'',services:reconcile(previous.services,s.services),connections:reconcile(previous.connections,s.connections),admin_url:s.admin_url};
}
function canPoll(running) { return !running; }
function delay(failures, opened) { return failures ? Math.min(30000,5000*Math.pow(2,Math.min(failures-1,4))) : opened ? 2000 : 5000; }
function filter(rows, query) { var q = query.toLowerCase(); return rows.filter(function(row) { return (row.domain+' '+row.source_name).toLowerCase().indexOf(q) >= 0; }); }
function selection(rows, id) { for (var i=0;i<rows.length;i++) if (rows[i].id === id) return i; return rows.length ? 0 : -1; }
function sync(list, rows) {
  for (var i=0;i<rows.length;i++) {
    var found = -1;
    for (var j=i;j<list.count;j++) if (list.get(j).id === rows[i].id) { found=j; break; }
    if (found < 0) list.insert(i,rows[i]);
    else {
      if (found !== i) list.move(found,i,1);
      var old = list.get(i);
      Object.keys(rows[i]).forEach(function(key) { if (old[key] !== rows[i][key]) list.setProperty(i,key,rows[i][key]); });
    }
  }
  if (list.count>rows.length) list.remove(rows.length,list.count-rows.length);
}
function message(state) {
  if (state.ready) return 'Zelport: available';
  var messages = {unavailable:'Zelport: unavailable',unauthorized:'Zelport API requires an update',incompatible:'Unsupported integration API',invalid:'Invalid integration response',limit:'Integration data exceeds safe limits',timeout:'Zelport: timed out',invalid_config:'Invalid configuration: check zelport/omarchy.json'};
  return messages[state.error] || 'Zelport: unavailable';
}

function canOpen(state, url) {
  return state.ready && (url === state.admin_url || state.services.some(function(row) { return row.url === url; }));
}

function visibleServices(rows, query, options) {
  options = options || defaults().services;
  var sources = options.source_types;
  var result = filter(rows,query).filter(function(row) { return !sources.length || sources.indexOf(row.source_id)>=0; });
  var key = options.sort_by==='source_type' ? 'source_name' : options.sort_by==='state' ? 'state' : 'domain';
  function compare(a,b) { return a<b ? -1 : a>b ? 1 : 0; }
  return result.sort(function(a,b) { return compare(a[key],b[key]) || compare(a.domain,b.domain) || compare(a.id,b.id); });
}
