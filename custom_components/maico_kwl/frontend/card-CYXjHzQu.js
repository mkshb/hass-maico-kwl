function t(t,e,s,r){var o,a=arguments.length,c=a<3?e:null===r?r=Object.getOwnPropertyDescriptor(e,s):r;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)c=Reflect.decorate(t,e,s,r);else for(var l=t.length-1;l>=0;l--)(o=t[l])&&(c=(a<3?o(c):a>3?o(e,s,c):o(e,s))||c);return a>3&&c&&Object.defineProperty(e,s,c),c}"function"==typeof SuppressedError&&SuppressedError;const e=globalThis,s=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,r=Symbol(),o=new WeakMap;let a=class n{constructor(t,e,s){if(this._$cssResult$=!0,s!==r)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(s&&void 0===t){const s=void 0!==e&&1===e.length;s&&(t=o.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&o.set(e,t))}return t}toString(){return this.cssText}};const c=(t,...e)=>{const s=1===t.length?t[0]:e.reduce((e,s,r)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[r+1],t[0]);return new a(s,t,r)},l=s?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return(t=>new a("string"==typeof t?t:t+"",void 0,r))(e)})(t):t,{is:h,defineProperty:d,getOwnPropertyDescriptor:p,getOwnPropertyNames:u,getOwnPropertySymbols:_,getPrototypeOf:f}=Object,$=globalThis,m=$.trustedTypes,g=m?m.emptyScript:"",v=$.reactiveElementPolyfillSupport,b=(t,e)=>t,x={toAttribute(t,e){switch(e){case Boolean:t=t?g:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},A=(t,e)=>!h(t,e),w={attribute:!0,type:String,converter:x,reflect:!1,useDefault:!1,hasChanged:A};Symbol.metadata??=Symbol("metadata"),$.litPropertyMetadata??=new WeakMap;let E=class y extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=w){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const s=Symbol(),r=this.getPropertyDescriptor(t,s,e);void 0!==r&&d(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){const{get:r,set:o}=p(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:r,set(e){const a=r?.call(this);o?.call(this,e),this.requestUpdate(t,a,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??w}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;const t=f(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){const t=this.properties,e=[...u(t),..._(t)];for(const s of e)this.createProperty(s,t[s])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,s]of e)this.elementProperties.set(t,s)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const s=this._$Eu(t,e);void 0!==s&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(l(t))}else void 0!==t&&e.push(l(t));return e}static _$Eu(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,r)=>{if(s)t.adoptedStyleSheets=r.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const s of r){const r=document.createElement("style"),o=e.litNonce;void 0!==o&&r.setAttribute("nonce",o),r.textContent=s.cssText,t.appendChild(r)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){const s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(void 0!==r&&!0===s.reflect){const o=(void 0!==s.converter?.toAttribute?s.converter:x).toAttribute(e,s.type);this._$Em=t,null==o?this.removeAttribute(r):this.setAttribute(r,o),this._$Em=null}}_$AK(t,e){const s=this.constructor,r=s._$Eh.get(t);if(void 0!==r&&this._$Em!==r){const t=s.getPropertyOptions(r),o="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:x;this._$Em=r;const a=o.fromAttribute(e,t.type);this[r]=a??this._$Ej?.get(r)??a,this._$Em=null}}requestUpdate(t,e,s,r=!1,o){if(void 0!==t){const a=this.constructor;if(!1===r&&(o=this[t]),s??=a.getPropertyOptions(t),!((s.hasChanged??A)(o,e)||s.useDefault&&s.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(a._$Eu(t,s))))return;this.C(t,e,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:o},a){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,a??e??this[t]),!0!==o||void 0!==a)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),!0===r&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,s]of t){const{wrapped:t}=s,r=this[e];!0!==t||this._$AL.has(e)||void 0===r||this.C(e,void 0,s,r)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};E.elementStyles=[],E.shadowRootOptions={mode:"open"},E[b("elementProperties")]=new Map,E[b("finalized")]=new Map,v?.({ReactiveElement:E}),($.reactiveElementVersions??=[]).push("2.1.2");const C=globalThis,M=t=>t,O=C.trustedTypes,P=O?O.createPolicy("lit-html",{createHTML:t=>t}):void 0,U="$lit$",T=`lit$${Math.random().toFixed(9).slice(2)}$`,N="?"+T,j=`<${N}>`,D=document,B=()=>D.createComment(""),K=t=>null===t||"object"!=typeof t&&"function"!=typeof t,W=Array.isArray,q="[ \t\n\f\r]",G=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,V=/-->/g,F=/>/g,J=RegExp(`>|${q}(?:([^\\s"'>=/]+)(${q}*=${q}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),X=/'/g,Y=/"/g,Q=/^(?:script|style|textarea|title)$/i,tt=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),et=tt(1),st=tt(2),it=Symbol.for("lit-noChange"),rt=Symbol.for("lit-nothing"),ot=new WeakMap,nt=D.createTreeWalker(D,129);function at(t,e){if(!W(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==P?P.createHTML(e):e}const ct=(t,e)=>{const s=t.length-1,r=[];let o,a=2===e?"<svg>":3===e?"<math>":"",c=G;for(let e=0;e<s;e++){const s=t[e];let l,h,d=-1,p=0;for(;p<s.length&&(c.lastIndex=p,h=c.exec(s),null!==h);)p=c.lastIndex,c===G?"!--"===h[1]?c=V:void 0!==h[1]?c=F:void 0!==h[2]?(Q.test(h[2])&&(o=RegExp("</"+h[2],"g")),c=J):void 0!==h[3]&&(c=J):c===J?">"===h[0]?(c=o??G,d=-1):void 0===h[1]?d=-2:(d=c.lastIndex-h[2].length,l=h[1],c=void 0===h[3]?J:'"'===h[3]?Y:X):c===Y||c===X?c=J:c===V||c===F?c=G:(c=J,o=void 0);const u=c===J&&t[e+1].startsWith("/>")?" ":"";a+=c===G?s+j:d>=0?(r.push(l),s.slice(0,d)+U+s.slice(d)+T+u):s+T+(-2===d?e:u)}return[at(t,a+(t[s]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),r]};class S{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let o=0,a=0;const c=t.length-1,l=this.parts,[h,d]=ct(t,e);if(this.el=S.createElement(h,s),nt.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(r=nt.nextNode())&&l.length<c;){if(1===r.nodeType){if(r.hasAttributes())for(const t of r.getAttributeNames())if(t.endsWith(U)){const e=d[a++],s=r.getAttribute(t).split(T),c=/([.?@])?(.*)/.exec(e);l.push({type:1,index:o,name:c[2],strings:s,ctor:"."===c[1]?I:"?"===c[1]?L:"@"===c[1]?z:H}),r.removeAttribute(t)}else t.startsWith(T)&&(l.push({type:6,index:o}),r.removeAttribute(t));if(Q.test(r.tagName)){const t=r.textContent.split(T),e=t.length-1;if(e>0){r.textContent=O?O.emptyScript:"";for(let s=0;s<e;s++)r.append(t[s],B()),nt.nextNode(),l.push({type:2,index:++o});r.append(t[e],B())}}}else if(8===r.nodeType)if(r.data===N)l.push({type:2,index:o});else{let t=-1;for(;-1!==(t=r.data.indexOf(T,t+1));)l.push({type:7,index:o}),t+=T.length-1}o++}}static createElement(t,e){const s=D.createElement("template");return s.innerHTML=t,s}}function lt(t,e,s=t,r){if(e===it)return e;let o=void 0!==r?s._$Co?.[r]:s._$Cl;const a=K(e)?void 0:e._$litDirective$;return o?.constructor!==a&&(o?._$AO?.(!1),void 0===a?o=void 0:(o=new a(t),o._$AT(t,s,r)),void 0!==r?(s._$Co??=[])[r]=o:s._$Cl=o),void 0!==o&&(e=lt(t,o._$AS(t,e.values),o,r)),e}class R{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??D).importNode(e,!0);nt.currentNode=r;let o=nt.nextNode(),a=0,c=0,l=s[0];for(;void 0!==l;){if(a===l.index){let e;2===l.type?e=new k(o,o.nextSibling,this,t):1===l.type?e=new l.ctor(o,l.name,l.strings,this,t):6===l.type&&(e=new Z(o,this,t)),this._$AV.push(e),l=s[++c]}a!==l?.index&&(o=nt.nextNode(),a++)}return nt.currentNode=D,r}p(t){let e=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=rt,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=lt(this,t,e),K(t)?t===rt||null==t||""===t?(this._$AH!==rt&&this._$AR(),this._$AH=rt):t!==this._$AH&&t!==it&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>W(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==rt&&K(this._$AH)?this._$AA.nextSibling.data=t:this.T(D.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:s}=t,r="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=S.createElement(at(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{const t=new R(r,this),s=t.u(this.options);t.p(e),this.T(s),this._$AH=t}}_$AC(t){let e=ot.get(t.strings);return void 0===e&&ot.set(t.strings,e=new S(t)),e}k(t){W(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,r=0;for(const o of t)r===e.length?e.push(s=new k(this.O(B()),this.O(B()),this,this.options)):s=e[r],s._$AI(o),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=M(t).nextSibling;M(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class H{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,o){this.type=1,this._$AH=rt,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=rt}_$AI(t,e=this,s,r){const o=this.strings;let a=!1;if(void 0===o)t=lt(this,t,e,0),a=!K(t)||t!==this._$AH&&t!==it,a&&(this._$AH=t);else{const r=t;let c,l;for(t=o[0],c=0;c<o.length-1;c++)l=lt(this,r[s+c],e,c),l===it&&(l=this._$AH[c]),a||=!K(l)||l!==this._$AH[c],l===rt?t=rt:t!==rt&&(t+=(l??"")+o[c+1]),this._$AH[c]=l}a&&!r&&this.j(t)}j(t){t===rt?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class I extends H{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===rt?void 0:t}}class L extends H{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==rt)}}class z extends H{constructor(t,e,s,r,o){super(t,e,s,r,o),this.type=5}_$AI(t,e=this){if((t=lt(this,t,e,0)??rt)===it)return;const s=this._$AH,r=t===rt&&s!==rt||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,o=t!==rt&&(s===rt||r);r&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class Z{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){lt(this,t)}}const ht=C.litHtmlPolyfillSupport;ht?.(S,k),(C.litHtmlVersions??=[]).push("3.3.3");const dt=globalThis;class i extends E{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,s)=>{const r=s?.renderBefore??e;let o=r._$litPart$;if(void 0===o){const t=s?.renderBefore??null;r._$litPart$=o=new k(e.insertBefore(B(),t),t,void 0,s??{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return it}}i._$litElement$=!0,i.finalized=!0,dt.litElementHydrateSupport?.({LitElement:i});const pt=dt.litElementPolyfillSupport;pt?.({LitElement:i}),(dt.litElementVersions??=[]).push("4.2.2");const ut={attribute:!0,type:String,converter:x,reflect:!1,hasChanged:A},_t=(t=ut,e,s)=>{const{kind:r,metadata:o}=s;let a=globalThis.litPropertyMetadata.get(o);if(void 0===a&&globalThis.litPropertyMetadata.set(o,a=new Map),"setter"===r&&((t=Object.create(t)).wrapped=!0),a.set(s.name,t),"accessor"===r){const{name:r}=s;return{set(s){const o=e.get.call(this);e.set.call(this,s),this.requestUpdate(r,o,t,!0,s)},init(e){return void 0!==e&&this.C(r,void 0,t,e),e}}}if("setter"===r){const{name:r}=s;return function(s){const o=this[r];e.call(this,s),this.requestUpdate(r,o,t,!0,s)}}throw Error("Unsupported decorator location: "+r)};function ft(t){return(e,s)=>"object"==typeof s?_t(t,e,s):((t,e,s)=>{const r=e.hasOwnProperty(s);return e.constructor.createProperty(s,t),r?Object.getOwnPropertyDescriptor(e,s):void 0})(t,e,s)}function $t(t){return ft({...t,state:!0,attribute:!1})}const mt="maico_kwl",yt=new Set(["unavailable","unknown"]);function gt(t){const e=new Set;for(const s of Object.values(t.entities))s.platform===mt&&s.device_id&&e.add(s.device_id);return[...e]}class KwlDevice{constructor(t,e){this._hass=t,this.deviceId=e,this._entityIds=new Map;for(const s of Object.values(t.entities))s.platform===mt&&s.device_id===e&&s.translation_key&&this._entityIds.set(s.translation_key,s.entity_id)}get name(){const t=this._hass.devices[this.deviceId];return t?.name_by_user||t?.name||"Maico KWL"}entityId(t){return this._entityIds.get(t)}has(t){return void 0!==this.stateObj(t)}stateObj(t){const e=this._entityIds.get(t),s=e?this._hass.states[e]:void 0;return s&&!yt.has(s.state)?s:void 0}state(t){return this.stateObj(t)?.state}number(t){const e=Number(this.state(t));return void 0===this.state(t)||Number.isNaN(e)?void 0:e}isOn(t){const e=this.state(t);return void 0===e?void 0:"on"===e}attribute(t,e){return this.stateObj(t)?.attributes[e]}format(t){const e=this.stateObj(t);return e?this._hass.formatEntityState(e):void 0}present(t){return t.filter(t=>this.has(t))}}const vt="temp_air_intake",bt="temp_supply_air",xt="temp_extract_air",At="temp_exhaust_air",wt="airflow_supply",Et="airflow_exhaust",St="fan_speed_supply",kt="fan_speed_exhaust",Ct="fan_supply_active",Mt="fan_exhaust_active",Ot="summer_bypass_open",Pt="ptc_heater_active",Ut="heat_recovery_efficiency",Ht={en:{card_name:"Maico KWL",card_description:"Airflow, temperatures and controls of a Maico ventilation unit.",no_device:"No Maico KWL unit found.",device_missing:"The selected unit no longer exists.",editor_device:"Unit",group_airflow:"Airflow",group_room:"Room",group_controls:"Controls",group_filters:"Filters",group_status:"Status",outdoor_air:"Outdoor air",supply_air:"Supply air",extract_air:"Extract air",exhaust_air:"Exhaust air",bypass_open:"Bypass open",bypass_closed:"Bypass closed",heat_recovery:"Heat recovery",fan_off:"off",ptc_heater:"PTC heater"},de:{card_name:"Maico KWL",card_description:"Luftströme, Temperaturen und Bedienung eines Maico-Lüftungsgeräts.",no_device:"Kein Maico-KWL-Gerät gefunden.",device_missing:"Das gewählte Gerät gibt es nicht mehr.",editor_device:"Gerät",group_airflow:"Luftstrom",group_room:"Raum",group_controls:"Bedienung",group_filters:"Filter",group_status:"Status",outdoor_air:"Außenluft",supply_air:"Zuluft",extract_air:"Abluft",exhaust_air:"Fortluft",bypass_open:"Bypass offen",bypass_closed:"Bypass zu",heat_recovery:"Rückgewinnung",fan_off:"aus",ptc_heater:"PTC-Heizregister"}};function Tt(t,e){const s=(t?.locale?.language??t?.language??"en").split("-")[0];return(s in Ht?Ht[s]:Ht.en)[e]}function Rt(t){const e=navigator.language.split("-")[0];return(e in Ht?Ht[e]:Ht.en)[t]}const Nt=[[-10,"#0d47a1"],[0,"#1976d2"],[10,"#64b5f6"],[20,"#b8b8b8"],[25,"#ffb74d"],[30,"#f57c00"],[35,"#d32f2f"]],jt=[[-10,"#1e88e5"],[0,"#42a5f5"],[10,"#90caf9"],[20,"#a8a8a8"],[25,"#ffb74d"],[30,"#ff9800"],[35,"#ef5350"]];function Lt(t,e){const s=e?jt:Nt;if(void 0===t)return function(t){return(t?jt:Nt)[3][1]}(e);if(t<=s[0][0])return s[0][1];for(let e=1;e<s.length;e++){const[r,o]=s[e],[a,c]=s[e-1];if(t<=r){return`color-mix(in oklab, ${o} ${Math.round((t-a)/(r-a)*100)}%, ${c})`}}return s[s.length-1][1]}function It(t,e,s,r=5){return void 0===t||void 0===e?Array.from({length:r},(o,a)=>Lt(a<r/2?t??e:e??t,s)):Array.from({length:r},(o,a)=>Lt(t+(e-t)*a/(r-1),s))}const zt=62,Dt=160,Bt=260,Kt="M96 62 C 128 62, 128 22, 162 22 L 258 22 C 292 22, 292 62, 324 62";const Wt=c`
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
    font-size: 12px;
  }
  .schematic .value {
    font-size: 20px;
    font-weight: 500;
  }
  .schematic .fan-speed {
    font-size: 12px;
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
    font-size: 11px;
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
    .rotor.spinning {
      animation: none;
    }
    .sheen-layer {
      display: none;
    }
  }
`,qt="maico-kwl-card",Gt=[["group_room",["room_temp_source","temp_room","temp_room_external","room_temp_bus_sent","humidity_exhaust","humidity_bus_sent","air_quality_bus_sent","humidity_sensor_1","humidity_sensor_2","humidity_sensor_3","humidity_sensor_4","enocean_humidity_id0","enocean_humidity_id1","enocean_humidity_id2","enocean_humidity_id3","enocean_humidity_id4","enocean_humidity_id5","enocean_humidity_id6","enocean_humidity_id7","co2_sensor_1","co2_sensor_2","co2_sensor_3","co2_sensor_4","enocean_co2_id0","enocean_co2_id1","enocean_co2_id2","enocean_co2_id3","enocean_co2_id4","enocean_co2_id5","enocean_co2_id6","enocean_co2_id7","voc_sensor_1","voc_sensor_2","voc_sensor_3","voc_sensor_4","enocean_voc_id0","enocean_voc_id1","enocean_voc_id2","enocean_voc_id3","enocean_voc_id4","enocean_voc_id5","enocean_voc_id6","enocean_voc_id7"]],["group_controls",["operating_mode","ventilation_level","current_vent_level","boost_ventilation","season"]],["group_filters",["filter_remaining_device","filter_remaining_outdoor","filter_remaining_room","filter_next_change"]],["group_status",["problem","fault_code","notice_code"]]];class MaicoKwlCard extends i{constructor(){super(...arguments),this._uid=`kwl${Math.random().toString(36).slice(2,10)}`}setConfig(t){this._config=t}getCardSize(){return 6}static async getConfigElement(){const{EDITOR_TYPE:t}=await(import("./editor-Bqpo8RMX.js"));return document.createElement(t)}static getStubConfig(t){const[e]=gt(t);return e?{device_id:e}:{}}_device(){const t=this._config?.device_id??gt(this.hass)[0];if(t&&this.hass.devices[t])return new KwlDevice(this.hass,t)}render(){if(!this.hass||!this._config)return rt;const t=this._device();if(!t){const t=this._config.device_id?"device_missing":"no_device";return et`<ha-card><p class="empty">${Tt(this.hass,t)}</p></ha-card>`}return et`
      <ha-card .header=${t.name}>
        <div class="content">
          ${function(t){const{hass:e,device:s,uid:r}=t,o=e.themes?.darkMode??!1,a=t=>Tt(e,t),c=s.number(vt),l=s.number(bt),h=s.number(xt),d=s.number(At),p=s.has(Ot),u=s.isOn(Ot)??!1,_=s.isOn(Ct)??(s.number(wt)??0)>0,f=s.isOn(Mt)??(s.number(Et)??0)>0,$=It(c,l,o),m=It(d,h,o),g=Lt(c,o),v=Lt(l,o),b=Lt(d,o),x=Lt(h,o),A=u?"M20 62 L96 62 M324 62 L392 62":"M20 62 L392 62",w="M400 142 L28 142",E=t=>`${Math.min(12,Math.max(2,810/Math.max(t??180,1))).toFixed(2)}s`,C=(e,r,o)=>s.entityId(e)?st`<g class="clickable" role="button" tabindex="0" aria-label=${o}
          @click=${()=>t.moreInfo(e)}
          @keydown=${s=>{"Enter"!==s.key&&" "!==s.key||(s.preventDefault(),t.moreInfo(e))}}>${r}</g>`:r,M=(t,e,r,o,a,c,l)=>{if(void 0===r)return rt;const h=s.format(t),d="left"===a;return C(t,st`
        <text class="name" x=${d?20:400} y=${c} text-anchor=${d?"start":"end"}>${e}</text>
        <circle cx=${d?24:396} cy=${l-7} r="4" style=${`fill: ${o}`}></circle>
        <text class="value" x=${d?34:386} y=${l} text-anchor=${d?"start":"end"}>${h}</text>
      `,`${e} ${h}`)},O=(t,e,r,o,c,l)=>{const h=s.number(o),d=h&&h>0?`${(4e3/h).toFixed(2)}s`:"2s",p=r?s.format(o):a("fan_off"),u=r?s.format(c):void 0;return C(o,st`
        <circle class="fan-housing" cx=${t} cy=${e} r="13"></circle>
        <g class=${r?"rotor spinning":"rotor"} style=${`animation-duration: ${d}`}>
          <circle cx=${t} cy=${e} r="13" fill="none" stroke="none"></circle>
          ${[0,120,240].map(s=>st`<ellipse cx=${t} cy=${e-6} rx="3" ry="5.5" transform=${`rotate(${s} ${t} ${e})`}></ellipse>`)}
        </g>
        ${p?st`<text class="fan-speed" x=${t} y=${l} text-anchor="middle">${p}</text>`:rt}
        ${u?st`<text class="small" x=${t} y=${l+14} text-anchor="middle">${u}</text>`:rt}
      `,`${p??""} ${u??""}`)},P=s.format(Ut);return et`
    <svg class="schematic" viewBox="0 -14 420 214" role="img"
      aria-label=${[a("outdoor_air"),a("supply_air"),a("extract_air"),a("exhaust_air")].join(", ")}>
      <defs>
        <linearGradient id=${`${r}-top`} gradientUnits="userSpaceOnUse" x1=${Dt} y1="0" x2=${Bt} y2="0">
          ${$.map((t,e)=>st`<stop offset=${e/($.length-1)} style=${`stop-color: ${t}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${r}-bottom`} gradientUnits="userSpaceOnUse" x1=${Dt} y1="0" x2=${Bt} y2="0">
          ${m.map((t,e)=>st`<stop offset=${e/(m.length-1)} style=${`stop-color: ${t}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${r}-sheen`}>
          <stop offset="0" stop-color="#000"></stop>
          <stop offset="0.5" stop-color="#fff"></stop>
          <stop offset="1" stop-color="#000"></stop>
        </linearGradient>
        <mask id=${`${r}-sheen-right`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen" x="-140" y="-14" width="140" height="214" fill=${`url(#${r}-sheen)`}
            style=${`animation-duration: ${E(s.number(wt))}`}></rect>
        </mask>
        <mask id=${`${r}-sheen-left`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen reverse" x="-140" y="-14" width="140" height="214" fill=${`url(#${r}-sheen)`}
            style=${`animation-duration: ${E(s.number(Et))}`}></rect>
        </mask>
      </defs>

      <rect class="exchanger" x=${Dt} y="34" width=${100} height="136" rx="12"></rect>
      <line class="exchanger-line" x1=${Dt} y1="34" x2=${Bt} y2="170"></line>
      <line class="exchanger-line" x1=${Bt} y1="34" x2=${Dt} y2="170"></line>

      ${p?C(Ot,st`
              <path class=${u?"tube":"bypass-closed"} d=${Kt}
                style=${u?`stroke: ${g}`:""}></path>
              <text class=${u?"bypass-label open":"bypass-label"} x="210" y="6" text-anchor="middle">
                ${a(u?"bypass_open":"bypass_closed")}
              </text>`,a(u?"bypass_open":"bypass_closed")):rt}

      <path class="tube" d=${A} stroke=${`url(#${r}-top)`}></path>
      ${u?st`<path class="passage" d=${"M96 62 L324 62"}></path>`:rt}
      <path class="tube" d=${w} stroke=${`url(#${r}-bottom)`}></path>
      <polygon points="396,57 406,62 396,67" style=${`fill: ${v}`}></polygon>
      <polygon points="24,137 14,142 24,147" style=${`fill: ${b}`}></polygon>

      ${_?st`<g class="sheen-layer" mask=${`url(#${r}-sheen-right)`}>
            <path class="tube-sheen" d=${A} stroke=${`url(#${r}-top)`}></path>
            ${u?st`<path class="tube-sheen" d=${Kt} style=${`stroke: ${g}`}></path>`:rt}
          </g>`:rt}
      ${f?st`<g class="sheen-layer" mask=${`url(#${r}-sheen-left)`}>
            <path class="tube-sheen" d=${w} stroke=${`url(#${r}-bottom)`}></path>
          </g>`:rt}

      ${(()=>{if(!s.has(Pt))return rt;const t=s.isOn(Pt)??!1;return C(Pt,st`<g class=${t?"ptc active":"ptc"}>
        <rect x=${47} y=${53} width="22" height="18" rx="4"></rect>
        <path d=${"M51 62 l3 -4 l4 8 l4 -8 l3 4"}></path>
      </g>`,a("ptc_heater"))})()}

      ${P?C(Ut,st`
              <rect class="exchanger" x="166" y="80" width="88" height="44" rx="8" stroke="none"></rect>
              <text class="value" x="210" y="102" text-anchor="middle">${P}</text>
              <text class="small" x="210" y="117" text-anchor="middle">${a("heat_recovery")}</text>`,`${a("heat_recovery")} ${P}`):rt}

      ${O(340,zt,_,St,wt,96)}
      ${O(80,142,f,kt,Et,104)}

      ${M(vt,a("outdoor_air"),c,g,"left",18,42)}
      ${M(bt,a("supply_air"),l,v,"right",18,42)}
      ${M(xt,a("extract_air"),h,x,"right",194,176)}
      ${M(At,a("exhaust_air"),d,b,"left",194,176)}
    </svg>
  `}({hass:this.hass,device:t,uid:this._uid,moreInfo:e=>this._moreInfo(t.entityId(e))})}
          ${Gt.map(([e,s])=>{const r=t.present(s);return r.length?et`
              <h3>${Tt(this.hass,e)}</h3>
              <table>
                ${r.map(e=>et`<tr>
                    <td>${t.stateObj(e).attributes.friendly_name??e}</td>
                    <td class="state">${t.format(e)}</td>
                  </tr>`)}
              </table>
            `:rt})}
        </div>
      </ha-card>
    `}_moreInfo(t){t&&this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:t},bubbles:!0,composed:!0}))}}MaicoKwlCard.styles=[Wt,c`
    .content {
      padding: 0 16px 16px;
    }
    h3 {
      margin: 16px 0 4px;
      font-size: 14px;
      font-weight: 500;
      color: var(--secondary-text-color);
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    td {
      padding: 4px 0;
      border-bottom: 1px solid var(--divider-color);
    }
    td.state {
      text-align: right;
      color: var(--secondary-text-color);
    }
    .empty {
      padding: 16px;
      margin: 0;
      color: var(--secondary-text-color);
    }
  `],t([ft({attribute:!1})],MaicoKwlCard.prototype,"hass",void 0),t([$t()],MaicoKwlCard.prototype,"_config",void 0),customElements.get(qt)||(customElements.define(qt,MaicoKwlCard),window.customCards=window.customCards??[],window.customCards.push({type:qt,name:Rt("card_name"),description:Rt("card_description"),preview:!0}));var Vt=Object.freeze({__proto__:null,MaicoKwlCard:MaicoKwlCard});export{rt as A,mt as D,t as _,et as b,Vt as c,i,Tt as l,ft as n,$t as r};
