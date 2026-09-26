// Entry the integration loads on every frontend page (add_extra_js_url).
//
// It runs before the frontend has installed its scoped custom element
// registry, which replaces window.customElements and window.HTMLElement.
// Anything defined or subclassed earlier is lost, and Lit captures
// HTMLElement when it loads. So wait for the app element, then load the card.
customElements.whenDefined("home-assistant").then(() => import("./card"));
