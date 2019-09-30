const ClientEntry = require('../src/Main.purs');
const path = window.location.pathname;
const dims = {w: window.innerWidth, h: window.innerHeight};
const state = window.__puxLastState || ClientEntry.initialState;
const app = ClientEntry.main(path)(dims)(state)()

app.state.subscribe(function (state) {
 window.__puxLastState = state;
});

// If hot-reloading, hook into each state change and re-render using the last
// state.
if (module.hot) {
  module.hot.accept();
}
