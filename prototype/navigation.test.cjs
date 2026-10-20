const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
test('navigation blocks a thin wall along a route with valid endpoints',()=>{
 assert.ok(fs.existsSync(__dirname+'/navigation.js'),'navigation adapter is missing');
 const {createNavigation}=require('./navigation.js');
 const nav=createNavigation({world:{width:200,height:120},collision:{actorRadius:9,ySquash:.5,solids:[{shape:'rect',x:99,y:0,w:1,h:120}]},layers:[],objects:[]});
 assert.equal(nav.isValid({x:50,y:60}),true);assert.equal(nav.isValid({x:150,y:60}),true);
 assert.equal(nav.segmentClear({x:50,y:60},{x:150,y:60}),false);assert.equal(nav.findPath({x:50,y:60},{x:150,y:60}),null);
});
test('beach spawn and wet sand are connected; invalid legacy positions restore safely',()=>{
 assert.ok(fs.existsSync(__dirname+'/navigation.js'),'navigation adapter is missing');
 const {createNavigation}=require('./navigation.js'),bundle=require('../assets/scenes/beach-v1/map-bundle.json'),nav=createNavigation(bundle);
 assert.equal(nav.isValid({x:640,y:610}),true);assert.deepEqual(nav.restore({x:-10,y:-10}),{x:640,y:610});
 assert.deepEqual(nav.restore({x:640,y:610}),{x:640,y:610});
 assert.ok(nav.findPath({x:640,y:610},{x:640,y:480}));
});
