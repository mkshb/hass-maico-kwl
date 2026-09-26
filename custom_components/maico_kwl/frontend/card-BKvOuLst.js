function t(t,e,s,o){var r,a=arguments.length,l=a<3?e:null===o?o=Object.getOwnPropertyDescriptor(e,s):o;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)l=Reflect.decorate(t,e,s,o);else for(var c=t.length-1;c>=0;c--)(r=t[c])&&(l=(a<3?r(l):a>3?r(e,s,l):r(e,s))||l);return a>3&&l&&Object.defineProperty(e,s,l),l}"function"==typeof SuppressedError&&SuppressedError;const e=globalThis,s=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,o=Symbol(),r=new WeakMap;let a=class n{constructor(t,e,s){if(this._$cssResult$=!0,s!==o)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(s&&void 0===t){const s=void 0!==e&&1===e.length;s&&(t=r.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&r.set(e,t))}return t}toString(){return this.cssText}};const l=(t,...e)=>{const s=1===t.length?t[0]:e.reduce((e,s,o)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[o+1],t[0]);return new a(s,t,o)},c=s?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return(t=>new a("string"==typeof t?t:t+"",void 0,o))(e)})(t):t,{is:d,defineProperty:h,getOwnPropertyDescriptor:u,getOwnPropertyNames:p,getOwnPropertySymbols:f,getPrototypeOf:_}=Object,g=globalThis,m=g.trustedTypes,$=m?m.emptyScript:"",v=g.reactiveElementPolyfillSupport,b=(t,e)=>t,x={toAttribute(t,e){switch(e){case Boolean:t=t?$:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},w=(t,e)=>!d(t,e),C={attribute:!0,type:String,converter:x,reflect:!1,useDefault:!1,hasChanged:w};Symbol.metadata??=Symbol("metadata"),g.litPropertyMetadata??=new WeakMap;let A=class y extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=C){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const s=Symbol(),o=this.getPropertyDescriptor(t,s,e);void 0!==o&&h(this.prototype,t,o)}}static getPropertyDescriptor(t,e,s){const{get:o,set:r}=u(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:o,set(e){const a=o?.call(this);r?.call(this,e),this.requestUpdate(t,a,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??C}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;const t=_(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){const t=this.properties,e=[...p(t),...f(t)];for(const s of e)this.createProperty(s,t[s])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,s]of e)this.elementProperties.set(t,s)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const s=this._$Eu(t,e);void 0!==s&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(c(t))}else void 0!==t&&e.push(c(t));return e}static _$Eu(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,o)=>{if(s)t.adoptedStyleSheets=o.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const s of o){const o=document.createElement("style"),r=e.litNonce;void 0!==r&&o.setAttribute("nonce",r),o.textContent=s.cssText,t.appendChild(o)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){const s=this.constructor.elementProperties.get(t),o=this.constructor._$Eu(t,s);if(void 0!==o&&!0===s.reflect){const r=(void 0!==s.converter?.toAttribute?s.converter:x).toAttribute(e,s.type);this._$Em=t,null==r?this.removeAttribute(o):this.setAttribute(o,r),this._$Em=null}}_$AK(t,e){const s=this.constructor,o=s._$Eh.get(t);if(void 0!==o&&this._$Em!==o){const t=s.getPropertyOptions(o),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:x;this._$Em=o;const a=r.fromAttribute(e,t.type);this[o]=a??this._$Ej?.get(o)??a,this._$Em=null}}requestUpdate(t,e,s,o=!1,r){if(void 0!==t){const a=this.constructor;if(!1===o&&(r=this[t]),s??=a.getPropertyOptions(t),!((s.hasChanged??w)(r,e)||s.useDefault&&s.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(a._$Eu(t,s))))return;this.C(t,e,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:o,wrapped:r},a){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,a??e??this[t]),!0!==r||void 0!==a)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),!0===o&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,s]of t){const{wrapped:t}=s,o=this[e];!0!==t||this._$AL.has(e)||void 0===o||this.C(e,void 0,s,o)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[b("elementProperties")]=new Map,A[b("finalized")]=new Map,v?.({ReactiveElement:A}),(g.reactiveElementVersions??=[]).push("2.1.2");const M=globalThis,E=t=>t,O=M.trustedTypes,P=O?O.createPolicy("lit-html",{createHTML:t=>t}):void 0,U="$lit$",T=`lit$${Math.random().toFixed(9).slice(2)}$`,j="?"+T,N=`<${j}>`,V=document,D=()=>V.createComment(""),B=t=>null===t||"object"!=typeof t&&"function"!=typeof t,K=Array.isArray,W="[ \t\n\f\r]",F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,q=/-->/g,G=/>/g,J=RegExp(`>|${W}(?:([^\\s"'>=/]+)(${W}*=${W}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),X=/'/g,Y=/"/g,Q=/^(?:script|style|textarea|title)$/i,tt=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),et=tt(1),it=tt(2),st=Symbol.for("lit-noChange"),ot=Symbol.for("lit-nothing"),nt=new WeakMap,rt=V.createTreeWalker(V,129);function at(t,e){if(!K(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==P?P.createHTML(e):e}const lt=(t,e)=>{const s=t.length-1,o=[];let r,a=2===e?"<svg>":3===e?"<math>":"",l=F;for(let e=0;e<s;e++){const s=t[e];let c,d,h=-1,u=0;for(;u<s.length&&(l.lastIndex=u,d=l.exec(s),null!==d);)u=l.lastIndex,l===F?"!--"===d[1]?l=q:void 0!==d[1]?l=G:void 0!==d[2]?(Q.test(d[2])&&(r=RegExp("</"+d[2],"g")),l=J):void 0!==d[3]&&(l=J):l===J?">"===d[0]?(l=r??F,h=-1):void 0===d[1]?h=-2:(h=l.lastIndex-d[2].length,c=d[1],l=void 0===d[3]?J:'"'===d[3]?Y:X):l===Y||l===X?l=J:l===q||l===G?l=F:(l=J,r=void 0);const p=l===J&&t[e+1].startsWith("/>")?" ":"";a+=l===F?s+N:h>=0?(o.push(c),s.slice(0,h)+U+s.slice(h)+T+p):s+T+(-2===h?e:p)}return[at(t,a+(t[s]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),o]};class S{constructor({strings:t,_$litType$:e},s){let o;this.parts=[];let r=0,a=0;const l=t.length-1,c=this.parts,[d,h]=lt(t,e);if(this.el=S.createElement(d,s),rt.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(o=rt.nextNode())&&c.length<l;){if(1===o.nodeType){if(o.hasAttributes())for(const t of o.getAttributeNames())if(t.endsWith(U)){const e=h[a++],s=o.getAttribute(t).split(T),l=/([.?@])?(.*)/.exec(e);c.push({type:1,index:r,name:l[2],strings:s,ctor:"."===l[1]?I:"?"===l[1]?L:"@"===l[1]?z:H}),o.removeAttribute(t)}else t.startsWith(T)&&(c.push({type:6,index:r}),o.removeAttribute(t));if(Q.test(o.tagName)){const t=o.textContent.split(T),e=t.length-1;if(e>0){o.textContent=O?O.emptyScript:"";for(let s=0;s<e;s++)o.append(t[s],D()),rt.nextNode(),c.push({type:2,index:++r});o.append(t[e],D())}}}else if(8===o.nodeType)if(o.data===j)c.push({type:2,index:r});else{let t=-1;for(;-1!==(t=o.data.indexOf(T,t+1));)c.push({type:7,index:r}),t+=T.length-1}r++}}static createElement(t,e){const s=V.createElement("template");return s.innerHTML=t,s}}function ct(t,e,s=t,o){if(e===st)return e;let r=void 0!==o?s._$Co?.[o]:s._$Cl;const a=B(e)?void 0:e._$litDirective$;return r?.constructor!==a&&(r?._$AO?.(!1),void 0===a?r=void 0:(r=new a(t),r._$AT(t,s,o)),void 0!==o?(s._$Co??=[])[o]=r:s._$Cl=r),void 0!==r&&(e=ct(t,r._$AS(t,e.values),r,o)),e}class R{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:s}=this._$AD,o=(t?.creationScope??V).importNode(e,!0);rt.currentNode=o;let r=rt.nextNode(),a=0,l=0,c=s[0];for(;void 0!==c;){if(a===c.index){let e;2===c.type?e=new k(r,r.nextSibling,this,t):1===c.type?e=new c.ctor(r,c.name,c.strings,this,t):6===c.type&&(e=new Z(r,this,t)),this._$AV.push(e),c=s[++l]}a!==c?.index&&(r=rt.nextNode(),a++)}return rt.currentNode=V,o}p(t){let e=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,o){this.type=2,this._$AH=ot,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=o,this._$Cv=o?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=ct(this,t,e),B(t)?t===ot||null==t||""===t?(this._$AH!==ot&&this._$AR(),this._$AH=ot):t!==this._$AH&&t!==st&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>K(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==ot&&B(this._$AH)?this._$AA.nextSibling.data=t:this.T(V.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:s}=t,o="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=S.createElement(at(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===o)this._$AH.p(e);else{const t=new R(o,this),s=t.u(this.options);t.p(e),this.T(s),this._$AH=t}}_$AC(t){let e=nt.get(t.strings);return void 0===e&&nt.set(t.strings,e=new S(t)),e}k(t){K(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,o=0;for(const r of t)o===e.length?e.push(s=new k(this.O(D()),this.O(D()),this,this.options)):s=e[o],s._$AI(r),o++;o<e.length&&(this._$AR(s&&s._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=E(t).nextSibling;E(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class H{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,o,r){this.type=1,this._$AH=ot,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=r,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=ot}_$AI(t,e=this,s,o){const r=this.strings;let a=!1;if(void 0===r)t=ct(this,t,e,0),a=!B(t)||t!==this._$AH&&t!==st,a&&(this._$AH=t);else{const o=t;let l,c;for(t=r[0],l=0;l<r.length-1;l++)c=ct(this,o[s+l],e,l),c===st&&(c=this._$AH[l]),a||=!B(c)||c!==this._$AH[l],c===ot?t=ot:t!==ot&&(t+=(c??"")+r[l+1]),this._$AH[l]=c}a&&!o&&this.j(t)}j(t){t===ot?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class I extends H{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===ot?void 0:t}}class L extends H{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==ot)}}class z extends H{constructor(t,e,s,o,r){super(t,e,s,o,r),this.type=5}_$AI(t,e=this){if((t=ct(this,t,e,0)??ot)===st)return;const s=this._$AH,o=t===ot&&s!==ot||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==ot&&(s===ot||o);o&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class Z{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){ct(this,t)}}const dt=M.litHtmlPolyfillSupport;dt?.(S,k),(M.litHtmlVersions??=[]).push("3.3.3");const ht=globalThis;class i extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,s)=>{const o=s?.renderBefore??e;let r=o._$litPart$;if(void 0===r){const t=s?.renderBefore??null;o._$litPart$=r=new k(e.insertBefore(D(),t),t,void 0,s??{})}return r._$AI(t),r})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return st}}i._$litElement$=!0,i.finalized=!0,ht.litElementHydrateSupport?.({LitElement:i});const ut=ht.litElementPolyfillSupport;ut?.({LitElement:i}),(ht.litElementVersions??=[]).push("4.2.2");const pt={attribute:!0,type:String,converter:x,reflect:!1,hasChanged:w},ft=(t=pt,e,s)=>{const{kind:o,metadata:r}=s;let a=globalThis.litPropertyMetadata.get(r);if(void 0===a&&globalThis.litPropertyMetadata.set(r,a=new Map),"setter"===o&&((t=Object.create(t)).wrapped=!0),a.set(s.name,t),"accessor"===o){const{name:o}=s;return{set(s){const r=e.get.call(this);e.set.call(this,s),this.requestUpdate(o,r,t,!0,s)},init(e){return void 0!==e&&this.C(o,void 0,t,e),e}}}if("setter"===o){const{name:o}=s;return function(s){const r=this[o];e.call(this,s),this.requestUpdate(o,r,t,!0,s)}}throw Error("Unsupported decorator location: "+o)};function _t(t){return(e,s)=>"object"==typeof s?ft(t,e,s):((t,e,s)=>{const o=e.hasOwnProperty(s);return e.constructor.createProperty(s,t),o?Object.getOwnPropertyDescriptor(e,s):void 0})(t,e,s)}function gt(t){return _t({...t,state:!0,attribute:!1})}const mt="maico_kwl",yt=new Set(["unavailable","unknown"]);function $t(t){const e=new Set;for(const s of Object.values(t.entities))s.platform===mt&&s.device_id&&e.add(s.device_id);return[...e]}class KwlDevice{constructor(t,e){this._hass=t,this.deviceId=e,this._entityIds=new Map;for(const s of Object.values(t.entities))s.platform===mt&&s.device_id===e&&s.translation_key&&this._entityIds.set(s.translation_key,s.entity_id)}get name(){const t=this._hass.devices[this.deviceId];return t?.name_by_user||t?.name||"Maico KWL"}entityId(t){return this._entityIds.get(t)}has(t){return void 0!==this.stateObj(t)}stateObj(t){const e=this._entityIds.get(t),s=e?this._hass.states[e]:void 0;return s&&!yt.has(s.state)?s:void 0}state(t){return this.stateObj(t)?.state}number(t){const e=Number(this.state(t));return void 0===this.state(t)||Number.isNaN(e)?void 0:e}isOn(t){const e=this.state(t);return void 0===e?void 0:"on"===e}attribute(t,e){return this.stateObj(t)?.attributes[e]}format(t){const e=this.stateObj(t);return e?this._hass.formatEntityState(e):void 0}present(t){return t.filter(t=>this.has(t))}}const vt="temp_air_intake",bt="temp_supply_air",xt="temp_extract_air",wt="temp_exhaust_air",kt="airflow_supply",Ct="airflow_exhaust",At="fan_speed_supply",St="fan_speed_exhaust",Mt="fan_supply_active",Et="fan_exhaust_active",Lt="summer_bypass_open",Ot="ptc_heater_active",Ht="heat_recovery_efficiency",Pt="heat_recovery_power",Ut="heat_recovery_energy",It="room_temp_source",Tt="temp_room",Rt="temp_room_external",zt="room_temp_bus_sent",jt="humidity_exhaust",Nt="absolute_humidity_extract",Vt="humidity_bus_sent",Dt="air_quality_bus_sent",Bt="operating_mode",Kt="ventilation_level",Wt="current_vent_level",Ft="boost_ventilation",qt="off_lock",Gt="season",Zt="filter_remaining_device",Jt="filter_remaining_outdoor",Xt="filter_remaining_room",Yt="filter_runtime_device",Qt="filter_runtime_outdoor",te="filter_runtime_room",ee="filter_next_change",ie="fault_code",se="notice_code",oe=["humidity_sensor_1","humidity_sensor_2","humidity_sensor_3","humidity_sensor_4","enocean_humidity_id0","enocean_humidity_id1","enocean_humidity_id2","enocean_humidity_id3","enocean_humidity_id4","enocean_humidity_id5","enocean_humidity_id6","enocean_humidity_id7"],ne=["co2_sensor_1","co2_sensor_2","co2_sensor_3","co2_sensor_4","enocean_co2_id0","enocean_co2_id1","enocean_co2_id2","enocean_co2_id3","enocean_co2_id4","enocean_co2_id5","enocean_co2_id6","enocean_co2_id7"],re=["voc_sensor_1","voc_sensor_2","voc_sensor_3","voc_sensor_4","enocean_voc_id0","enocean_voc_id1","enocean_voc_id2","enocean_voc_id3","enocean_voc_id4","enocean_voc_id5","enocean_voc_id6","enocean_voc_id7"];const ae={en:{card_name:"Maico KWL",card_description:"Airflow, temperatures and controls of a Maico ventilation unit.",no_device:"No Maico KWL unit found.",device_missing:"The selected unit no longer exists.",editor_device:"Unit",group_airflow:"Airflow",group_room:"Room",group_controls:"Controls",group_filters:"Filters",group_status:"Status",outdoor_air:"Outdoor air",supply_air:"Supply air",extract_air:"Extract air",exhaust_air:"Exhaust air",bypass_open:"Bypass open",bypass_closed:"Bypass closed",heat_recovery:"Heat recovery",fan_off:"off",ptc_heater:"PTC heater",tile_room:"Room",tile_humidity:"Humidity",tile_air_quality:"Air quality",tile_heat_recovery:"Heat recovery",bus_badge:"BUS",from_source:"from {name}",bus_stale:"no value for {minutes} min",bus_never:"no value sent yet",sub_extract_air:"extract air",sub_external_sensor:"external sensor",air_good:"good",air_moderate:"moderate",air_poor:"poor",absolute_humidity_extract:"Absolute humidity of the extract air",energy_today:"{value} today",ventilation_level:"Ventilation level",operating_mode:"Operating mode",boost:"Boost",level_off:"Off",level_humidity_protection:"Humidity",level_reduced:"Reduced",level_nominal:"Nominal",level_intensive:"Intensive",level_auto_hint:"Level is chosen by {mode}",filter_device:"Device filter",filter_outdoor:"Outdoor filter",filter_room:"Room filter",filter_days:"{days} days",filter_due:"due",filter_next_change:"Next change on {date}",notices_one:"1 notice",notices_many:"{count} notices",faults_one:"Fault",faults_many:"{count} faults"},de:{card_name:"Maico KWL",card_description:"Luftströme, Temperaturen und Bedienung eines Maico-Lüftungsgeräts.",no_device:"Kein Maico-KWL-Gerät gefunden.",device_missing:"Das gewählte Gerät gibt es nicht mehr.",editor_device:"Gerät",group_airflow:"Luftstrom",group_room:"Raum",group_controls:"Bedienung",group_filters:"Filter",group_status:"Status",outdoor_air:"Außenluft",supply_air:"Zuluft",extract_air:"Abluft",exhaust_air:"Fortluft",bypass_open:"Bypass offen",bypass_closed:"Bypass zu",heat_recovery:"Rückgewinnung",fan_off:"aus",ptc_heater:"PTC-Heizregister",tile_room:"Raum",tile_humidity:"Feuchte",tile_air_quality:"Luftgüte",tile_heat_recovery:"Rückgewinnung",bus_badge:"BUS",from_source:"von {name}",bus_stale:"seit {minutes} min kein Wert",bus_never:"noch kein Wert gesendet",sub_extract_air:"Abluft",sub_external_sensor:"externer Fühler",air_good:"gut",air_moderate:"mäßig",air_poor:"schlecht",absolute_humidity_extract:"Absolute Feuchte Abluft",energy_today:"heute {value}",ventilation_level:"Lüftungsstufe",operating_mode:"Betriebsart",boost:"Stoßlüftung",level_off:"Aus",level_humidity_protection:"Feuchte",level_reduced:"Reduziert",level_nominal:"Nenn",level_intensive:"Intensiv",level_auto_hint:"Stufe wird von {mode} gewählt",filter_device:"Gerätefilter",filter_outdoor:"Außenluftfilter",filter_room:"Raumfilter",filter_days:"{days} Tage",filter_due:"fällig",filter_next_change:"Nächster Wechsel am {date}",notices_one:"1 Hinweis",notices_many:"{count} Hinweise",faults_one:"Störung",faults_many:"{count} Störungen"}};function le(t,e,s={}){const o=(t?.locale?.language??t?.language??"en").split("-")[0];return(o in ae?ae[o]:ae.en)[e].replace(/\{(\w+)\}/g,(t,e)=>e in s?String(s[e]):t)}function ce(t){const e=navigator.language.split("-")[0];return(e in ae?ae[e]:ae.en)[t]}const de=["off","humidity_protection","reduced","nominal","intensive"],he={off:"M12.5,2C9.64,2 8.57,4.55 9.29,7.47L15,13.16C15.87,13.37 16.81,13.81 17.28,14.73C18.46,17.1 22.03,17 22.03,12.5C22.03,8.92 18.05,8.13 14.35,10.13C14.03,9.73 13.61,9.42 13.13,9.22C13.32,8.29 13.76,7.24 14.75,6.75C17.11,5.57 17,2 12.5,2M3.28,4L2,5.27L4.47,7.73C3.22,7.74 2,8.87 2,11.5C2,15.07 5.96,15.85 9.65,13.87C9.97,14.27 10.4,14.59 10.89,14.79C10.69,15.71 10.25,16.75 9.27,17.24C6.91,18.42 7,22 11.5,22C13.8,22 14.94,20.36 14.94,18.21L18.73,22L20,20.72L3.28,4Z",humidity_protection:"M12,3.25C12,3.25 6,10 6,14C6,17.32 8.69,20 12,20A6,6 0 0,0 18,14C18,10 12,3.25 12,3.25M14.47,9.97L15.53,11.03L9.53,17.03L8.47,15.97M9.75,10A1.25,1.25 0 0,1 11,11.25A1.25,1.25 0 0,1 9.75,12.5A1.25,1.25 0 0,1 8.5,11.25A1.25,1.25 0 0,1 9.75,10M14.25,14.5A1.25,1.25 0 0,1 15.5,15.75A1.25,1.25 0 0,1 14.25,17A1.25,1.25 0 0,1 13,15.75A1.25,1.25 0 0,1 14.25,14.5Z",reduced:"M13 19C13 17.59 13.5 16.3 14.3 15.28C14.17 14.97 14.03 14.65 13.86 14.34C14.26 14 14.57 13.59 14.77 13.11C15.26 13.21 15.78 13.39 16.25 13.67C17.07 13.25 18 13 19 13C20.05 13 21.03 13.27 21.89 13.74C21.95 13.37 22 12.96 22 12.5C22 8.92 18.03 8.13 14.33 10.13C14 9.73 13.59 9.42 13.11 9.22C13.3 8.29 13.74 7.24 14.73 6.75C17.09 5.57 17 2 12.5 2C8.93 2 8.14 5.96 10.13 9.65C9.72 9.97 9.4 10.39 9.21 10.87C8.28 10.68 7.23 10.25 6.73 9.26C5.56 6.89 2 7 2 11.5C2 15.07 5.95 15.85 9.64 13.87C9.96 14.27 10.39 14.59 10.88 14.79C10.68 15.71 10.24 16.75 9.26 17.24C6.9 18.42 7 22 11.5 22C12.31 22 13 21.78 13.5 21.41C13.19 20.67 13 19.86 13 19M12 13C11.43 13 11 12.55 11 12S11.43 11 12 11C12.54 11 13 11.45 13 12S12.54 13 12 13M17 15V17H18V23H20V15H17Z",nominal:"M13 19C13 17.59 13.5 16.3 14.3 15.28C14.17 14.97 14.03 14.65 13.86 14.34C14.26 14 14.57 13.59 14.77 13.11C15.26 13.21 15.78 13.39 16.25 13.67C17.07 13.25 18 13 19 13C20.05 13 21.03 13.27 21.89 13.74C21.95 13.37 22 12.96 22 12.5C22 8.92 18.03 8.13 14.33 10.13C14 9.73 13.59 9.42 13.11 9.22C13.3 8.29 13.74 7.24 14.73 6.75C17.09 5.57 17 2 12.5 2C8.93 2 8.14 5.96 10.13 9.65C9.72 9.97 9.4 10.39 9.21 10.87C8.28 10.68 7.23 10.25 6.73 9.26C5.56 6.89 2 7 2 11.5C2 15.07 5.95 15.85 9.64 13.87C9.96 14.27 10.39 14.59 10.88 14.79C10.68 15.71 10.24 16.75 9.26 17.24C6.9 18.42 7 22 11.5 22C12.31 22 13 21.78 13.5 21.41C13.19 20.67 13 19.86 13 19M12 13C11.43 13 11 12.55 11 12S11.43 11 12 11C12.54 11 13 11.45 13 12S12.54 13 12 13M16 15V17H19V18H18C16.9 18 16 18.9 16 20V23H21V21H18V20H19C20.11 20 21 19.11 21 18V17C21 15.9 20.11 15 19 15H16Z",intensive:"M13 19C13 17.59 13.5 16.3 14.3 15.28C14.17 14.97 14.03 14.65 13.86 14.34C14.26 14 14.57 13.59 14.77 13.11C15.26 13.21 15.78 13.39 16.25 13.67C17.07 13.25 18 13 19 13C20.05 13 21.03 13.27 21.89 13.74C21.95 13.37 22 12.96 22 12.5C22 8.92 18.03 8.13 14.33 10.13C14 9.73 13.59 9.42 13.11 9.22C13.3 8.29 13.74 7.24 14.73 6.75C17.09 5.57 17 2 12.5 2C8.93 2 8.14 5.96 10.13 9.65C9.72 9.97 9.4 10.39 9.21 10.87C8.28 10.68 7.23 10.25 6.73 9.26C5.56 6.89 2 7 2 11.5C2 15.07 5.95 15.85 9.64 13.87C9.96 14.27 10.39 14.59 10.88 14.79C10.68 15.71 10.24 16.75 9.26 17.24C6.9 18.42 7 22 11.5 22C12.31 22 13 21.78 13.5 21.41C13.19 20.67 13 19.86 13 19M12 13C11.43 13 11 12.55 11 12S11.43 11 12 11C12.54 11 13 11.45 13 12S12.54 13 12 13M21 21V20.5C21 19.67 20.33 19 19.5 19C20.33 19 21 18.33 21 17.5V17C21 15.89 20.1 15 19 15H16V17H19V18H17V20H19V21H16V23H19C20.11 23 21 22.11 21 21"},ue=new Set(["auto_time","auto_sensor"]),pe=[["filter_device",Zt,Yt],["filter_outdoor",Jt,Qt],["filter_room",Xt,te]],fe={level:t=>t.state(Wt)??t.state(Kt),mode:t=>t.state(Bt),boost:t=>t.state(Ft)};function _e(t,e,s,o){const r=t.device.entityId(s);r&&t.change(e,o,()=>t.hass.callService("select","select_option",{entity_id:r,option:o}))}function ge(t){const{hass:e,device:s}=t,o=(t,s)=>le(e,t,s);if(!s.stateObj(Kt))return ot;const r=t.shown("mode"),a=void 0!==r&&ue.has(r),l=t.shown("level"),c=t.pending("level"),d=s.isOn(qt)??!1,h=s.stateObj(Bt);return et`
    <div class="control">
      <div class="control-label" id="kwl-level-label">${o("ventilation_level")}</div>
      <div class=${a?"segments locked":"segments"} role="group" aria-labelledby="kwl-level-label">
        ${de.map(e=>{const s=e===l,r=a||"off"===e&&d;return et`<button
            type="button"
            class=${s?c?"segment active pending":"segment active":"segment"}
            aria-pressed=${s?"true":"false"}
            aria-label=${o(`level_${e}`)}
            title=${o(`level_${e}`)}
            ?disabled=${r}
            @click=${()=>_e(t,"level",Kt,e)}
          >
            ${t.narrow?et`<svg class="level-icon" viewBox="0 0 24 24" aria-hidden="true">
                  ${it`<path d=${he[e]}></path>`}
                </svg>`:o(`level_${e}`)}
          </button>`})}
      </div>
      ${function(t,e,s){const o=(e,s)=>le(t.hass,e,s),r=[t.narrow&&e&&de.includes(e)?o(`level_${e}`):void 0,s?o("level_auto_hint",{mode:s}):void 0].filter(Boolean);return r.length?et`<div class="hint">${r.join(" · ")}</div>`:ot}(t,l,a&&h?e.formatEntityState(h,r):void 0)}
    </div>
  `}function me(t){const{hass:e,device:s}=t,o=(t,s)=>le(e,t,s),r=pe.filter(([,t])=>void 0!==s.number(t));if(!r.length)return ot;const a=function(t,e){const s=e?.match(/^(\d{4})-(\d{2})-(\d{2})$/);if(!s)return;const[o,r,a]=s.slice(1).map(Number),l=t.locale?.language??t.language??"en";return new Intl.DateTimeFormat(l,{day:"2-digit",month:"2-digit",year:"numeric"}).format(new Date(o,r-1,a))}(e,s.state(ee))??s.format(ee);return et`
    <div class="filters">
      ${r.map(([e,r,a])=>{const l=Math.max(0,Math.round(s.number(r))),c=s.number(a),d=c?Math.min(1,l/(30.44*c)):1,h=0===l?"due":l<=14?"soon":"ok";return et`
          <button type="button" class="filter" @click=${()=>t.moreInfo(r)}>
            <span class="filter-head">
              <span class="control-label">${o(e)}</span>
              <span class=${`filter-days ${h}`}>
                ${"due"===h?o("filter_due"):o("filter_days",{days:l})}
              </span>
            </span>
            <span class="bar"><span class=${`bar-fill ${h}`} style=${`width: ${100*d}%`}></span></span>
          </button>
        `})}
      ${a?et`<div class="hint">${o("filter_next_change",{date:a})}</div>`:ot}
    </div>
  `}function ye(t){return et`${ge(t)}${function(t){const{hass:e,device:s}=t,o=t=>le(e,t),r=s.stateObj(Bt),a=s.has(Ft)?s.entityId(Ft):void 0,l=s.stateObj(Gt);if(!r&&!a&&!l)return ot;const c=r?.attributes.options??[],d=t.shown("mode"),h="on"===t.shown("boost"),u=["button",h?"active":"",t.pending("boost")?"pending":""].join(" "),p=e=>t.narrow?ot:et`<span>${e}</span>`;return et`
    <div class="mode-row">
      ${r?et`<label class="control mode">
            <span class="control-label">${o("operating_mode")}</span>
            <span class="select">
              <select
                class=${t.pending("mode")?"pending":""}
                .value=${d??""}
                @change=${e=>_e(t,"mode",Bt,e.target.value)}
              >
                ${c.map(t=>et`<option value=${t} ?selected=${t===d}>
                    ${e.formatEntityState(r,t)}
                  </option>`)}
              </select>
              <svg class="chevron" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M7 10l5 5 5-5"></path>
              </svg>
            </span>
          </label>`:ot}
      ${a?et`<button
            type="button"
            class=${u}
            aria-pressed=${h?"true":"false"}
            aria-label=${o("boost")}
            title=${o("boost")}
            @click=${()=>t.change("boost",h?"off":"on",()=>e.callService("switch",h?"turn_off":"turn_on",{entity_id:a}))}
          >
            <svg viewBox="0 0 18 18" aria-hidden="true" class="stroke-icon">
              <path d="M2 6 H11 A2.5 2.5 0 1 0 8.5 3.5"></path>
              <path d="M2 10 H14 A2.5 2.5 0 1 1 11.5 12.5"></path>
              <path d="M2 14 H7"></path>
            </svg>
            ${p(o("boost"))}
          </button>`:ot}
      ${!l||"summer"!==l.state&&"winter"!==l.state?ot:et`<button
            type="button"
            class="button"
            aria-label=${e.formatEntityState(l)}
            title=${e.formatEntityState(l)}
            @click=${()=>t.moreInfo(Gt)}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true" class="fill-icon">
              ${it`<path d=${"summer"===l.state?"M3.55 19.09L4.96 20.5L6.76 18.71L5.34 17.29M12 6C8.69 6 6 8.69 6 12S8.69 18 12 18 18 15.31 18 12C18 8.68 15.31 6 12 6M20 13H23V11H20M17.24 18.71L19.04 20.5L20.45 19.09L18.66 17.29M20.45 5L19.04 3.6L17.24 5.39L18.66 6.81M13 1H11V4H13M6.76 5.39L4.96 3.6L3.55 5L5.34 6.81L6.76 5.39M1 13H4V11H1M13 20H11V23H13":"M20.79,13.95L18.46,14.57L16.46,13.44V10.56L18.46,9.43L20.79,10.05L21.31,8.12L19.54,7.65L20,5.88L18.07,5.36L17.45,7.69L15.45,8.82L13,7.38V5.12L14.71,3.41L13.29,2L12,3.29L10.71,2L9.29,3.41L11,5.12V7.38L8.5,8.82L6.5,7.69L5.92,5.36L4,5.88L4.47,7.65L2.7,8.12L3.22,10.05L5.55,9.43L7.55,10.56V13.45L5.55,14.58L3.22,13.96L2.7,15.89L4.47,16.36L4,18.12L5.93,18.64L6.55,16.31L8.55,15.18L11,16.62V18.88L9.29,20.59L10.71,22L12,20.71L13.29,22L14.7,20.59L13,18.88V16.62L15.5,15.17L17.5,16.3L18.12,18.63L20,18.12L19.53,16.35L21.3,15.88L20.79,13.95M9.5,10.56L12,9.11L14.5,10.56V13.44L12,14.89L9.5,13.44V10.56Z"}></path>`}
            </svg>
            ${p(e.formatEntityState(l))}
          </button>`}
    </div>
  `}(t)}${me(t)}`}const $e=l`
  .pending {
    animation: kwl-pending 1.2s ease-in-out infinite alternate;
  }
  @keyframes kwl-pending {
    from {
      opacity: 1;
    }
    to {
      opacity: 0.55;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .pending {
      animation: none;
      opacity: 0.7;
    }
  }
  .control {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-top: 16px;
  }
  .control-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--secondary-text-color);
  }
  .hint {
    font-size: 12px;
    color: var(--secondary-text-color);
  }
  .segments {
    display: flex;
    gap: 4px;
    padding: 4px;
    border-radius: 12px;
    background: var(--secondary-background-color, #f5f5f5);
  }
  .segment {
    flex: 1 1 0;
    min-width: 0;
    height: 44px;
    padding: 0 4px;
    border: 0;
    border-radius: 8px;
    background: transparent;
    color: var(--primary-text-color);
    font: inherit;
    font-size: 13px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: pointer;
  }
  .level-icon {
    width: 22px;
    height: 22px;
    fill: currentColor;
    vertical-align: middle;
  }
  .segment.active {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
  }
  .segment:disabled {
    cursor: default;
  }
  .segments.locked .segment:not(.active),
  .segment:disabled:not(.active) {
    color: var(--secondary-text-color);
    opacity: 0.75;
  }
  .segments.locked .segment.active {
    opacity: 0.7;
  }
  .segment:focus-visible,
  .button:focus-visible,
  .filter:focus-visible,
  select:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  .mode-row {
    display: flex;
    align-items: flex-end;
    gap: 8px;
  }
  .mode {
    flex: 1 1 auto;
    min-width: 0;
  }
  /* Without appearance: none Safari draws its own control and ignores the
     border and background; the arrow is drawn by the card instead. */
  .select {
    position: relative;
    display: flex;
  }
  select {
    flex: 1 1 auto;
    min-width: 0;
    height: 44px;
    padding: 0 36px 0 12px;
    border: 0;
    border-radius: 10px;
    background: var(--secondary-background-color, #f5f5f5);
    color: var(--primary-text-color);
    font: inherit;
    font-size: 14px;
    -webkit-appearance: none;
    appearance: none;
    cursor: pointer;
  }
  .chevron {
    position: absolute;
    top: 50%;
    right: 10px;
    width: 20px;
    height: 20px;
    transform: translateY(-50%);
    fill: none;
    stroke: var(--primary-text-color);
    stroke-width: 2px;
    stroke-linecap: round;
    stroke-linejoin: round;
    pointer-events: none;
  }
  .button {
    display: flex;
    flex-shrink: 0;
    justify-content: center;
    min-width: 44px;
    align-items: center;
    gap: 8px;
    height: 44px;
    padding: 0 16px;
    border: 0;
    border-radius: 10px;
    background: var(--secondary-background-color, #f5f5f5);
    color: var(--primary-text-color);
    font: inherit;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
  }
  .button.active {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
  }
  .button svg {
    width: 18px;
    height: 18px;
  }
  .stroke-icon {
    fill: none;
    stroke: currentColor;
    stroke-width: 2px;
    stroke-linecap: round;
  }
  .fill-icon {
    fill: currentColor;
  }
  .filters {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 16px;
  }
  .filter {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 0;
    border: 0;
    background: none;
    color: var(--primary-text-color);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  .filter-head {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
  }
  .filter-days.soon,
  .filter-days.due {
    color: var(--kwl-warn-fg);
    font-weight: 500;
  }
  .bar {
    display: block;
    height: 6px;
    border-radius: 3px;
    background: var(--secondary-background-color, #f5f5f5);
    overflow: hidden;
  }
  .bar-fill {
    display: block;
    height: 100%;
    border-radius: 3px;
    background: var(--primary-color);
  }
  .bar-fill.soon,
  .bar-fill.due {
    background: var(--kwl-warn-fg);
  }
`,ve=new Set(["bypass_active"]);function be(t,e){const s=t.attribute(e,"active");return Array.isArray(s)?s.filter(t=>"string"==typeof t):[]}function xe(t){const{hass:e,device:s}=t,o=function(t,e){const s=[];for(const[o,r]of[["fault",ie],["notice",se]]){const a=e.stateObj(r);if(a)for(const l of be(e,r))"notice"===o&&ve.has(l)||s.push({kind:o,text:t.formatEntityAttributeValue(a,"active",l)})}return s}(e,s),r=o.filter(t=>"fault"===t.kind).length,a=o.length-r,l=r?1===r?le(e,"faults_one"):le(e,"faults_many",{count:r}):1===a?le(e,"notices_one"):le(e,"notices_many",{count:a});return et`
    <div class="header">
      <div class="title">${s.name}</div>
      ${o.length?et`<button
            type="button"
            class=${r?"chip fault":"chip notice"}
            aria-expanded=${t.expanded?"true":"false"}
            @click=${t.toggle}
          >
            <svg viewBox="0 0 16 16" aria-hidden="true">
              <circle cx="8" cy="8" r="6.5"></circle>
              <line x1="8" y1="4.5" x2="8" y2="9"></line>
              <line x1="8" y1="11.4" x2="8" y2="11.5"></line>
            </svg>
            ${l}
          </button>`:ot}
    </div>
    ${o.length&&t.expanded?et`<ul class="messages">
          ${o.map(e=>et`<li>
              <button
                type="button"
                class=${e.kind}
                @click=${()=>t.moreInfo("fault"===e.kind?ie:se)}
              >
                ${e.text}
              </button>
            </li>`)}
        </ul>`:ot}
  `}const we=l`
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 16px 16px 0;
  }
  .title {
    min-width: 0;
    overflow: hidden;
    font-size: 20px;
    font-weight: 400;
    line-height: 28px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .chip {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    gap: 6px;
    height: 32px;
    padding: 0 12px;
    border: 0;
    border-radius: 16px;
    font: inherit;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
  }
  .chip svg {
    width: 16px;
    height: 16px;
    fill: none;
    stroke: currentColor;
    stroke-width: 2px;
    stroke-linecap: round;
  }
  .chip.notice {
    background: var(--kwl-warn-bg);
    color: var(--kwl-warn-fg);
  }
  .chip.fault {
    background: var(--kwl-fault-bg);
    color: var(--kwl-fault-fg);
  }
  .chip:focus-visible,
  .messages button:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  .messages {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin: 12px 16px 0;
    padding: 0;
    list-style: none;
  }
  .messages button {
    width: 100%;
    padding: 8px 12px;
    border: 0;
    border-radius: 8px;
    font: inherit;
    font-size: 13px;
    text-align: left;
    cursor: pointer;
  }
  .messages .notice {
    background: var(--kwl-warn-bg);
    color: var(--kwl-warn-fg);
  }
  .messages .fault {
    background: var(--kwl-fault-bg);
    color: var(--kwl-fault-fg);
  }
`,ke=[[-10,"#0d47a1"],[0,"#1976d2"],[10,"#64b5f6"],[20,"#b8b8b8"],[25,"#ffb74d"],[30,"#f57c00"],[35,"#d32f2f"]],Ce=[[-10,"#1e88e5"],[0,"#42a5f5"],[10,"#90caf9"],[20,"#a8a8a8"],[25,"#ffb74d"],[30,"#ff9800"],[35,"#ef5350"]];function Ae(t,e){const s=e?Ce:ke;if(void 0===t)return function(t){return(t?Ce:ke)[3][1]}(e);if(t<=s[0][0])return s[0][1];for(let e=1;e<s.length;e++){const[o,r]=s[e],[a,l]=s[e-1];if(t<=o){return`color-mix(in oklab, ${r} ${Math.round((t-a)/(o-a)*100)}%, ${l})`}}return s[s.length-1][1]}function Se(t,e,s,o=5){return void 0===t||void 0===e?Array.from({length:o},(r,a)=>Ae(a<o/2?t??e:e??t,s)):Array.from({length:o},(r,a)=>Ae(t+(e-t)*a/(o-1),s))}const Me=62,Ee=142,Le=160,Oe=260,He="M96 62 C 128 62, 128 22, 162 22 L 258 22 C 292 22, 292 62, 324 62";const Pe=l`
  .schematic {
    display: block;
    width: 100%;
    max-width: 460px;
    margin: 0 auto;
    overflow: visible;
    font-family: inherit;
  }
  .schematic text {
    fill: var(--primary-text-color);
  }
  .schematic .name,
  .schematic .small {
    fill: var(--secondary-text-color);
  }
  .schematic .value,
  .schematic .fan-speed {
    font-weight: 500;
  }
  .exchanger {
    fill: var(--secondary-background-color, #f5f5f5);
    fill-opacity: 0.55;
    stroke: var(--divider-color);
  }
  .exchanger-line {
    stroke: var(--divider-color);
    opacity: 0.6;
  }
  .tube,
  .tube-sheen {
    fill: none;
    stroke-width: 10px;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .tube {
    opacity: 0.32;
  }
  .tube-sheen {
    opacity: 0.45;
  }
  .passage,
  .bypass-closed {
    fill: none;
    stroke: var(--secondary-text-color);
    stroke-width: 2px;
    stroke-dasharray: 3 5;
    opacity: 0.35;
  }
  .bypass-label {
    font-weight: 500;
    fill: var(--secondary-text-color);
  }
  .bypass-label.open {
    fill: var(--primary-text-color);
  }
  .fan-housing {
    fill: var(--card-background-color, #fff);
    stroke: var(--secondary-text-color);
    stroke-width: 1.5px;
  }
  .rotor {
    fill: var(--secondary-text-color);
    transform-box: fill-box;
    transform-origin: center;
  }
  .rotor.spinning {
    animation: kwl-spin linear infinite;
  }
  .ptc rect {
    fill: var(--card-background-color, #fff);
    stroke: var(--secondary-text-color);
    stroke-width: 1.5px;
  }
  .ptc path {
    fill: none;
    stroke: var(--secondary-text-color);
    stroke-width: 1.5px;
    stroke-linejoin: round;
  }
  .ptc.active rect,
  .ptc.active path {
    stroke: #f57c00;
  }
  .sheen {
    animation: kwl-sheen linear infinite;
  }
  .sheen.reverse {
    animation-direction: reverse;
  }
  .clickable {
    cursor: pointer;
    outline: none;
  }
  /* Invisible tap areas: a whole fan or temperature block takes a tap, not
     only its drawn parts, and a finger-wide stroke along the bypass line. */
  .hit-box {
    fill: transparent;
  }
  .hit-area {
    fill: none;
    stroke: transparent;
    stroke-width: 24px;
    pointer-events: stroke;
  }
  .clickable:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  @keyframes kwl-spin {
    to {
      transform: rotate(360deg);
    }
  }
  @keyframes kwl-sheen {
    from {
      transform: translateX(0);
    }
    to {
      transform: translateX(560px);
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .rotor.spinning,
    .sheen {
      animation: none;
    }
    .sheen-layer {
      display: none;
    }
  }
`;function Ue(t,e){const s=t.states[e]?.attributes.friendly_name;return"string"==typeof s?s:e}function Ie(t,e,s,o,r,a){const l=e.format(r),c=e.attribute(r,"source_entity");if(void 0===l||!c)return;const d=e.attribute(r,"last_written"),h=d?Math.floor((a-Date.parse(d))/6e4):void 0,u=void 0===h||h>=10;return{label:o,key:r,moreInfo:c,value:l,sub:void 0===h?s("bus_never"):u?s("bus_stale",{minutes:h}):s("from_source",{name:Ue(t,c)}),bus:{stale:u}}}function Te(t,e,s,o){const r=e.present(o).filter(t=>void 0!==e.number(t));if(!r.length)return;const a=r.reduce((t,s)=>e.number(s)>e.number(t)?s:t),l=e.entityId(a);return{label:s,key:a,moreInfo:l,value:e.format(a),sub:r.length>1?Ue(t,l):void 0}}function Re(t,e,s,o){const r=t.format(s);return void 0===r?void 0:{label:e,key:s,moreInfo:t.entityId(s),value:r,sub:o}}function ze(t,e,s,o){switch(e.state(It)){case"bus":return Ie(t,e,s,"tile_room",zt,o)??Re(e,"tile_room",Tt);case"external":return Re(e,"tile_room",Rt,s("sub_external_sensor"))??Re(e,"tile_room",Tt);default:return Re(e,"tile_room",Tt)}}function je(t,e,s,o){const r=Ie(t,e,s,"tile_humidity",Vt,o)??Te(t,e,"tile_humidity",oe)??Re(e,"tile_humidity",jt,s("sub_extract_air")),a=e.format(Nt);return r&&a&&(r.extra={value:a,title:s("absolute_humidity_extract")}),r}function Ne(t,e,s,o){const r=Te(t,e,"tile_air_quality",ne)??Te(t,e,"tile_air_quality",re)??Ie(t,e,s,"tile_air_quality",Dt,o);if(!r)return;const a=e.number(r.key);return void 0!==a&&(r.air=a<=800?"good":a<=1400?"moderate":"poor"),r}function Ve(t,e,s,o){const r=Re(e,"tile_heat_recovery",Pt);if(r&&void 0!==o){const e=t.locale?.language??t.language??"en",a=new Intl.NumberFormat(e,{maximumFractionDigits:o<10?2:1}).format(o);r.sub=s("energy_today",{value:`${a} kWh`})}return r}const De=l`
  .tiles {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-top: 16px;
  }
  .tile {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-height: 72px;
    padding: 10px 12px;
    border: 0;
    border-radius: 10px;
    background: var(--secondary-background-color, #f5f5f5);
    color: var(--primary-text-color);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  .tile:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  .tile-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--secondary-text-color);
  }
  .tile-value {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 18px;
    font-weight: 500;
  }
  .tile-sub {
    display: -webkit-box;
    overflow: hidden;
    max-width: 100%;
    font-size: 11px;
    line-height: 14px;
    color: var(--secondary-text-color);
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    overflow-wrap: anywhere;
  }
  .tile-extra {
    font-size: 13px;
    font-weight: 400;
    color: var(--secondary-text-color);
    white-space: nowrap;
  }
  .sub-icon {
    width: 14px;
    height: 14px;
    margin-right: 4px;
    fill: currentColor;
    vertical-align: -2px;
  }
  .badge {
    padding: 1px 6px;
    border-radius: 6px;
    background: var(--kwl-bus-bg);
    color: var(--kwl-bus-fg);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.3px;
  }
  .badge.stale {
    background: var(--kwl-warn-bg);
    color: var(--kwl-warn-fg);
  }
  .tile-sub.stale {
    color: var(--kwl-warn-fg);
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  .air-good {
    background: var(--kwl-good);
  }
  .air-moderate {
    background: var(--kwl-moderate);
  }
  .air-poor {
    background: var(--kwl-poor);
  }
`,Be="maico-kwl-card";class MaicoKwlCard extends i{constructor(){super(...arguments),this._uid=`kwl${Math.random().toString(36).slice(2,10)}`,this._pending=new Map,this._messagesExpanded=!1,this._width=0,this._energyFetchedAt=0}setConfig(t){this._config=t}getCardSize(){return 6}static async getConfigElement(){const{EDITOR_TYPE:t}=await(import("./editor-BCLyY86e.js"));return document.createElement(t)}static getStubConfig(t){const[e]=$t(t);return e?{device_id:e}:{}}connectedCallback(){super.connectedCallback(),this._resizeObserver??=new ResizeObserver(([t])=>{const e=Math.round(t.contentRect.width);e!==this._width&&requestAnimationFrame(()=>this._width=e)}),this._resizeObserver.observe(this)}disconnectedCallback(){super.disconnectedCallback(),this._resizeObserver?.disconnect();for(const t of[...this._pending.keys()])this._clearPending(t)}willUpdate(t){if(!t.has("hass")||!this._pending.size||!this.hass)return;const e=this._device();if(e)for(const[t,s]of this._pending)fe[t](e)===s.value&&this._clearPending(t)}firstUpdated(){const t=Math.round(this.getBoundingClientRect().width);t&&(this._width=t)}updated(t){super.updated(t),t.has("hass")&&Date.now()-this._energyFetchedAt>3e5&&this._fetchEnergyToday()}async _fetchEnergyToday(){const t=this.hass&&this._device(),e=t?.entityId(Ut);if(e){this._energyFetchedAt=Date.now();try{const t=await this.hass.callWS({type:"recorder/statistic_during_period",statistic_id:e,calendar:{period:"day"},types:["change"]});this._energyToday="number"==typeof t.change?Math.max(0,t.change):void 0}catch{this._energyToday=void 0}}}_clearPending(t){const e=this._pending.get(t);e&&(window.clearTimeout(e.timer),this._pending.delete(t),this._pending=new Map(this._pending))}_controls(t){return{hass:this.hass,device:t,narrow:this._width>0&&this._width<400,moreInfo:e=>this._moreInfo(t.entityId(e)),shown:e=>this._pending.get(e)?.value??fe[e](t),pending:t=>this._pending.has(t),change:(e,s,o)=>{if(this._clearPending(e),fe[e](t)===s)return void o();const r=window.setTimeout(()=>this._clearPending(e),35e3);this._pending=new Map(this._pending).set(e,{value:s,timer:r}),o().catch(()=>this._clearPending(e))}}}_device(){const t=this._config?.device_id??$t(this.hass)[0];if(t&&this.hass.devices[t])return new KwlDevice(this.hass,t)}render(){if(!this.hass||!this._config)return ot;const t=this._device();if(!t){const t=this._config.device_id?"device_missing":"no_device";return et`<ha-card><p class="empty">${le(this.hass,t)}</p></ha-card>`}return et`
      <ha-card class=${this.hass.themes?.darkMode?"dark":""}>
        ${xe({hass:this.hass,device:t,expanded:this._messagesExpanded,toggle:()=>this._messagesExpanded=!this._messagesExpanded,moreInfo:e=>this._moreInfo(t.entityId(e))})}
        <div class="content">
          ${function(t){const{hass:e,device:s,uid:o}=t,r=Math.max(1,t.scale),a=Math.max(12,11*r),l=Math.max(20,17*r),c=Math.max(12,11.5*r),d=Math.max(11,10.5*r),h=Math.max(18,15*r),u=r>1.15,p=Math.max(4,3.2*r),f=176+Math.max(18,1.25*a),_=e.themes?.darkMode??!1,g=t=>le(e,t),m=s.number(vt),$=s.number(bt),v=s.number(xt),b=s.number(wt),x=s.has(Lt),w=s.isOn(Lt)??!1,C=s.isOn(Mt)??(s.number(kt)??0)>0,A=s.isOn(Et)??(s.number(Ct)??0)>0,M=Se(m,$,_),E=Se(b,v,_),O=Ae(m,_),P=Ae($,_),U=Ae(b,_),T=Ae(v,_),j=w?"M20 62 L96 62 M324 62 L392 62":"M20 62 L392 62",N="M400 142 L28 142",V=t=>`${Math.min(12,Math.max(2,810/Math.max(t??180,1))).toFixed(2)}s`,D=(e,o,r)=>s.entityId(e)?it`<g class="clickable" role="button" tabindex="0" aria-label=${r}
          @click=${()=>t.moreInfo(e)}
          @keydown=${s=>{"Enter"!==s.key&&" "!==s.key||(s.preventDefault(),t.moreInfo(e))}}>${o}</g>`:o,B=(t,e,o,r,c,d,h)=>{if(void 0===o)return ot;const u=s.format(t),f="left"===c;return D(t,it`
        <rect class="hit-box" x=${f?16:284} y=${Math.min(d,h)-l}
          width=${120} height=${Math.abs(d-h)+l+6}></rect>
        <text class="name" x=${f?20:400} y=${d} text-anchor=${f?"start":"end"}
          style=${`font-size: ${a}px`}>${e}</text>
        <circle cx=${f?20+p:400-p} cy=${h-.35*l} r=${p}
          style=${`fill: ${r}`}></circle>
        <text class="value" x=${f?26+2*p:394-2*p} y=${h}
          text-anchor=${f?"start":"end"} style=${`font-size: ${l}px`}>${u}</text>
      `,`${e} ${u}`)},K=(t,e,o,r,l,d)=>{const h=1.2*a,u=Math.min(e-15,d-h-c),p=Math.max(e+15,d+4),f=s.number(r),_=f&&f>0?`${(4e3/f).toFixed(2)}s`:"2s",m=o?s.format(r):g("fan_off"),$=o?s.format(l):void 0;return D(r,it`
        <rect class="hit-box" x=${t-46} y=${u} width="92" height=${p-u}></rect>
        <circle class="fan-housing" cx=${t} cy=${e} r="13"></circle>
        <g class=${o?"rotor spinning":"rotor"} style=${`animation-duration: ${_}`}>
          <circle cx=${t} cy=${e} r="13" fill="none" stroke="none"></circle>
          ${[0,120,240].map(s=>it`<ellipse cx=${t} cy=${e-6} rx="3" ry="5.5" transform=${`rotate(${s} ${t} ${e})`}></ellipse>`)}
        </g>
        ${m?it`<text class="fan-speed" x=${t} y=${d-h} text-anchor="middle"
              style=${`font-size: ${c}px`}>${m}</text>`:ot}
        ${$?it`<text class="small" x=${t} y=${d} text-anchor="middle"
              style=${`font-size: ${a}px`}>${$}</text>`:ot}
      `,`${m??""} ${$??""}`)},W=s.format(Ht);return et`
    <svg class="schematic" viewBox="0 -14 420 214" role="img"
      aria-label=${[g("outdoor_air"),g("supply_air"),g("extract_air"),g("exhaust_air")].join(", ")}>
      <defs>
        <linearGradient id=${`${o}-top`} gradientUnits="userSpaceOnUse" x1=${Le} y1="0" x2=${Oe} y2="0">
          ${M.map((t,e)=>it`<stop offset=${e/(M.length-1)} style=${`stop-color: ${t}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${o}-bottom`} gradientUnits="userSpaceOnUse" x1=${Le} y1="0" x2=${Oe} y2="0">
          ${E.map((t,e)=>it`<stop offset=${e/(E.length-1)} style=${`stop-color: ${t}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${o}-sheen`}>
          <stop offset="0" stop-color="#000"></stop>
          <stop offset="0.5" stop-color="#fff"></stop>
          <stop offset="1" stop-color="#000"></stop>
        </linearGradient>
        <mask id=${`${o}-sheen-right`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen" x="-140" y="-14" width="140" height="214" fill=${`url(#${o}-sheen)`}
            style=${`animation-duration: ${V(s.number(kt))}`}></rect>
        </mask>
        <mask id=${`${o}-sheen-left`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen reverse" x="-140" y="-14" width="140" height="214" fill=${`url(#${o}-sheen)`}
            style=${`animation-duration: ${V(s.number(Ct))}`}></rect>
        </mask>
      </defs>

      <rect class="exchanger" x=${Le} y="34" width=${100} height="136" rx="12"></rect>
      <line class="exchanger-line" x1=${Le} y1="34" x2=${Oe} y2="170"></line>
      <line class="exchanger-line" x1=${Oe} y1="34" x2=${Le} y2="170"></line>

      ${x?D(Lt,it`
              <path class="hit-area" d=${He}></path>
              <path class=${w?"tube":"bypass-closed"} d=${He}
                style=${w?`stroke: ${O}`:""}></path>
              <text class=${w?"bypass-label open":"bypass-label"} x="210" y="6" text-anchor="middle"
                style=${`font-size: ${d}px`}>
                ${g(w?"bypass_open":"bypass_closed")}
              </text>`,g(w?"bypass_open":"bypass_closed")):ot}

      <path class="tube" d=${j} stroke=${`url(#${o}-top)`}></path>
      ${w?it`<path class="passage" d=${"M96 62 L324 62"}></path>`:ot}
      <path class="tube" d=${N} stroke=${`url(#${o}-bottom)`}></path>
      <polygon points="396,57 406,62 396,67" style=${`fill: ${P}`}></polygon>
      <polygon points="24,137 14,142 24,147" style=${`fill: ${U}`}></polygon>

      ${C?it`<g class="sheen-layer" mask=${`url(#${o}-sheen-right)`}>
            <path class="tube-sheen" d=${j} stroke=${`url(#${o}-top)`}></path>
            ${w?it`<path class="tube-sheen" d=${He} style=${`stroke: ${O}`}></path>`:ot}
          </g>`:ot}
      ${A?it`<g class="sheen-layer" mask=${`url(#${o}-sheen-left)`}>
            <path class="tube-sheen" d=${N} stroke=${`url(#${o}-bottom)`}></path>
          </g>`:ot}

      ${(()=>{if(!s.has(Ot))return ot;const t=s.isOn(Ot)??!1;return D(Ot,it`<g class=${t?"ptc active":"ptc"}>
        <rect x=${47} y=${53} width="22" height="18" rx="4"></rect>
        <path d=${"M51 62 l3 -4 l4 8 l4 -8 l3 4"}></path>
      </g>`,g("ptc_heater"))})()}

      ${W?D(Ht,it`
              <rect class="exchanger" x="166" y="80" width="88" height="44" rx="8" stroke="none"></rect>
              ${u?it`<text class="value" x="210" y=${102+.35*h} text-anchor="middle"
                    style=${`font-size: ${h}px`}>${W}</text>`:it`<text class="value" x="210" y="102" text-anchor="middle"
                      style=${`font-size: ${h}px`}>${W}</text>
                    <text class="small" x="210" y="117" text-anchor="middle"
                      style=${`font-size: ${a}px`}>${g("heat_recovery")}</text>`}`,`${g("heat_recovery")} ${W}`):ot}

      ${K(340,Me,C,At,kt,79+c+1.2*a)}
      ${K(80,Ee,A,St,Ct,120)}

      ${B(vt,g("outdoor_air"),m,O,"left",18,42)}
      ${B(bt,g("supply_air"),$,P,"right",18,42)}
      ${B(xt,g("extract_air"),v,T,"right",f,176)}
      ${B(wt,g("exhaust_air"),b,U,"left",f,176)}
    </svg>
  `}({hass:this.hass,device:t,uid:this._uid,scale:this._width?420/Math.min(460,this._width-32):1,moreInfo:e=>this._moreInfo(t.entityId(e))})}
          ${function(t,e,s){if(!e.length)return ot;const o=e=>le(t,e);return et`
    <div class="tiles">
      ${e.map(t=>et`
          <button class="tile" type="button" @click=${()=>s(t.moreInfo)}>
            <span class="tile-label">
              ${o(t.label)}
              ${t.bus?et`<span class=${t.bus.stale?"badge stale":"badge"}>${o("bus_badge")}</span>`:ot}
            </span>
            <span class="tile-value">
              ${t.air?et`<span class=${`dot air-${t.air}`} title=${o(`air_${t.air}`)}></span>`:ot}
              ${t.value}
              ${t.extra?et`<span class="tile-extra" title=${t.extra.title}>${t.extra.value}</span>`:ot}
            </span>
            ${t.sub?et`<span class=${t.bus?.stale?"tile-sub stale":"tile-sub"}>
                  ${t.subIcon?et`<svg class="sub-icon" viewBox="0 0 24 24" aria-hidden="true">
                        ${it`<path d=${t.subIcon}></path>`}
                      </svg>`:ot}${t.sub}
                </span>`:ot}
          </button>
        `)}
    </div>
  `}(this.hass,function(t,e,s,o=Date.now()){const r=(e,s)=>le(t,e,s);return[ze(t,e,r,o),je(t,e,r,o),Ne(t,e,r,o),Ve(t,e,r,s)].filter(t=>void 0!==t)}(this.hass,t,this._energyToday),t=>this._moreInfo(t))}
          ${ye(this._controls(t))}
        </div>
      </ha-card>
    `}_moreInfo(t){t&&this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:t},bubbles:!0,composed:!0}))}}MaicoKwlCard.styles=[we,Pe,De,$e,l`
    ha-card {
      color: var(--primary-text-color);
      --kwl-bus-bg: #dcebf6;
      --kwl-bus-fg: #01497c;
      --kwl-warn-bg: #fff1dc;
      --kwl-warn-fg: #7a4a00;
      --kwl-good: #2e7d32;
      --kwl-moderate: #f9a825;
      --kwl-poor: #c62828;
      --kwl-fault-bg: #fde7e7;
      --kwl-fault-fg: #9b1c1c;
    }
    ha-card.dark {
      --kwl-bus-bg: #123447;
      --kwl-bus-fg: #8fd3f7;
      --kwl-warn-bg: #3b2c12;
      --kwl-warn-fg: #ffcc80;
      --kwl-good: #81c784;
      --kwl-moderate: #ffd54f;
      --kwl-poor: #ef5350;
      --kwl-fault-bg: #4a1c1c;
      --kwl-fault-fg: #ffb4b4;
    }
    .content {
      padding: 16px;
    }
    .empty {
      padding: 16px;
      margin: 0;
      color: var(--secondary-text-color);
    }
  `],t([_t({attribute:!1})],MaicoKwlCard.prototype,"hass",void 0),t([gt()],MaicoKwlCard.prototype,"_config",void 0),t([gt()],MaicoKwlCard.prototype,"_pending",void 0),t([gt()],MaicoKwlCard.prototype,"_messagesExpanded",void 0),t([gt()],MaicoKwlCard.prototype,"_width",void 0),t([gt()],MaicoKwlCard.prototype,"_energyToday",void 0),customElements.get(Be)||(customElements.define(Be,MaicoKwlCard),window.customCards=window.customCards??[],window.customCards.push({type:Be,name:ce("card_name"),description:ce("card_description"),preview:!0}));var Ke=Object.freeze({__proto__:null,MaicoKwlCard:MaicoKwlCard});export{ot as A,mt as D,t as _,et as b,Ke as c,i,le as l,_t as n,gt as r};
