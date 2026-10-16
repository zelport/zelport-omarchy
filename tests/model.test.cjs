const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = path.join(__dirname, '../Model.js');
const model = {};
if (fs.existsSync(source)) vm.runInNewContext(fs.readFileSync(source, 'utf8'), model);
test('reconciliation retains unchanged objects and updates only changed rows', () => {
  assert.equal(typeof model.reconcile, 'function');
  const a = {id:'a', domain:'alpha.localhost', state:'configured'};
  const b = {id:'b', domain:'beta.localhost', state:'configured'};
  const result = model.reconcile([a,b], [{...a},{...b,state:'stale'}]);
  assert.equal(result[0], a); assert.notEqual(result[1], b); assert.equal(result[1].state, 'stale');
});
test('failure disables launch and retains last verified snapshot; reconnect updates data', () => {
  assert.equal(typeof model.receive, 'function');
  let state = model.initial();
  state = model.receive(state, {ok:true,state:{services:[{id:'x'}],connections:[],admin_url:'http://localhost:8080/'}});
  assert.equal(state.ready,true);
  const rows = state.services;
  state = model.receive(state,{ok:false,error:'unauthorized'});
  assert.equal(state.ready,false); assert.equal(state.services, rows); assert.equal(state.error,'unauthorized');
  state = model.receive(state,{ok:true,state:{services:[{id:'y'}],connections:[],admin_url:'http://localhost:8080/'}});
  assert.equal(state.services[0].id,'y'); assert.equal(state.ready,true);
});
test('poll gate forbids overlap and backoff is bounded', () => {
  assert.equal(typeof model.canPoll, 'function');
  assert.equal(model.canPoll(true),false); assert.equal(model.canPoll(false),true);
  assert.equal(model.delay(0,false),5000); assert.equal(model.delay(0,true),2000);
  assert.equal(model.delay(20,false),30000);
});
test('search is case insensitive and stable selection survives reorder', () => {
  assert.equal(typeof model.filter, 'function');
  const rows = [{id:'a',domain:'demo.localhost',source_name:'Remote'},{id:'b',domain:'local.localhost',source_name:'Local'}];
  assert.equal(model.filter(rows,'REMOTE')[0].id,'a');
  assert.equal(model.selection([rows[1],rows[0]],'a'),1);
});
test('list synchronization preserves nodes across unchanged polls and reordering', () => {
  assert.equal(typeof model.sync, 'function');
  const rows = [{id:'a',state:'configured'},{id:'b',state:'configured'}];
  const list = {rows, get count(){return this.rows.length}, get(i){return this.rows[i]}, insert(i,r){this.rows.splice(i,0,{...r})}, move(a,b){this.rows.splice(b,0,this.rows.splice(a,1)[0])}, remove(i,n){this.rows.splice(i,n)}, setProperty(i,k,v){this.rows[i][k]=v}};
  const a=rows[0],b=rows[1];
  model.sync(list,[{id:'b',state:'stale'},{id:'a',state:'configured'}]);
  assert.equal(list.get(0),b); assert.equal(list.get(1),a); assert.equal(b.state,'stale');
  model.sync(list,[{id:'a',state:'configured'}]); assert.equal(list.count,1); assert.equal(list.get(0),a);
});
test('data flow updates one existing row without replacing unchanged rows', () => {
  const previous = [{id:'a',data_flow:'Aux port 3000'},{id:'b',data_flow:'Aux port 4000'}];
  const incoming = [{id:'a',data_flow:'Aux port 3001'},{id:'b',data_flow:'Aux port 4000'}];
  const reconciled = model.reconcile(previous,incoming);
  assert.notEqual(reconciled[0],previous[0]);
  assert.equal(reconciled[1],previous[1]);
  const list = {rows:previous.slice(), get count(){return this.rows.length}, get(i){return this.rows[i]}, insert(){assert.fail('unexpected insert')}, move(){assert.fail('unexpected move')}, remove(){assert.fail('unexpected remove')}, setProperty(i,k,v){this.rows[i][k]=v}};
  model.sync(list,reconciled);
  assert.equal(list.get(0),previous[0]);
  assert.equal(list.get(0).data_flow,'Aux port 3001');
  assert.equal(model.selection(list.rows,'b'),1);
});
test('gateway availability does not depend on relay modules or their connection state', () => {
  for (const connections of [[], [{id:'ports_over_relay',label:'Ports over Relay',state:'disconnected'}], [{id:'relay',label:'Built-in Relay',state:'stopped'}]]) {
    const state = model.receive(model.initial(), {ok:true,state:{services:[],connections,admin_url:'http://localhost:8080'}});
    assert.equal(state.ready,true);
    assert.equal(model.message(state),'Zelport: available');
    assert.equal(model.receive(state,{ok:false,error:'unavailable'}).ready,false);
  }
});
test('unsupported routes cannot open while the gateway remains available', () => {
  const state = {ready:true,admin_url:'http://localhost:8080',services:[{url:'http://missing.localhost:8080',state:'unsupported'},{url:'http://active.localhost:8080',state:'configured'}]};
  assert.equal(model.canOpen(state,state.services[0].url),false);
  assert.equal(model.canOpen(state,state.services[1].url),true);
  assert.equal(model.canOpen(state,state.admin_url),true);
  assert.equal(model.canOpen({...state,ready:false},state.admin_url),false);
  assert.equal(model.canOpen(state,'https://elsewhere.invalid'),false);
});
test('configured source filtering and deterministic sorting preserve row objects', () => {
  const a={id:'a',domain:'z.localhost',source_id:'remote_http',source_name:'Remote HTTP',state:'configured'};
  const b={id:'b',domain:'a.localhost',source_id:'local_ports',source_name:'Local Ports',state:'ready'};
  assert.deepEqual(Array.from(model.visibleServices([a,b],'',{source_types:[],sort_by:'domain'})),[b,a]);
  assert.deepEqual(Array.from(model.visibleServices([a,b],'',{source_types:['remote_http'],sort_by:'state'})),[a]);
  assert.equal(model.visibleServices([a,b],'remote',{source_types:[],sort_by:'source_type'})[0],a);
  assert.equal(a.domain,'z.localhost');
});
test('configuration survives temporary failure without enabling launch', () => {
  const s=model.receive(model.initial(),{ok:false,error:'unavailable',config:{panel:{remember_selection:false}}});
  assert.equal(s.ready,false);assert.equal(s.config.panel.remember_selection,false);
});
