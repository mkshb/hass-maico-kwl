function e(e,t,s,o){var r,a=arguments.length,l=a<3?t:null===o?o=Object.getOwnPropertyDescriptor(t,s):o;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)l=Reflect.decorate(e,t,s,o);else for(var c=e.length-1;c>=0;c--)(r=e[c])&&(l=(a<3?r(l):a>3?r(t,s,l):r(t,s))||l);return a>3&&l&&Object.defineProperty(t,s,l),l}"function"==typeof SuppressedError&&SuppressedError;const t=globalThis,s=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,o=Symbol(),r=new WeakMap;let a=class n{constructor(e,t,s){if(this._$cssResult$=!0,s!==o)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(s&&void 0===e){const s=void 0!==t&&1===t.length;s&&(e=r.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&r.set(t,e))}return e}toString(){return this.cssText}};const l=(e,...t)=>{const s=1===e.length?e[0]:t.reduce((t,s,o)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+e[o+1],e[0]);return new a(s,e,o)},c=s?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const s of e.cssRules)t+=s.cssText;return(e=>new a("string"==typeof e?e:e+"",void 0,o))(t)})(e):e,{is:d,defineProperty:h,getOwnPropertyDescriptor:u,getOwnPropertyNames:p,getOwnPropertySymbols:f,getPrototypeOf:_}=Object,g=globalThis,m=g.trustedTypes,$=m?m.emptyScript:"",v=g.reactiveElementPolyfillSupport,b=(e,t)=>e,x={toAttribute(e,t){switch(t){case Boolean:e=e?$:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let s=e;switch(t){case Boolean:s=null!==e;break;case Number:s=null===e?null:Number(e);break;case Object:case Array:try{s=JSON.parse(e)}catch(e){s=null}}return s}},w=(e,t)=>!d(e,t),A={attribute:!0,type:String,converter:x,reflect:!1,useDefault:!1,hasChanged:w};Symbol.metadata??=Symbol("metadata"),g.litPropertyMetadata??=new WeakMap;let E=class y extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=A){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const s=Symbol(),o=this.getPropertyDescriptor(e,s,t);void 0!==o&&h(this.prototype,e,o)}}static getPropertyDescriptor(e,t,s){const{get:o,set:r}=u(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:o,set(t){const a=o?.call(this);r?.call(this,t),this.requestUpdate(e,a,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??A}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;const e=_(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){const e=this.properties,t=[...p(e),...f(e)];for(const s of t)this.createProperty(s,e[s])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,s]of t)this.elementProperties.set(e,s)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const s=this._$Eu(e,t);void 0!==s&&this._$Eh.set(s,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const s=new Set(e.flat(1/0).reverse());for(const e of s)t.unshift(c(e))}else void 0!==e&&t.push(c(e));return t}static _$Eu(e,t){const s=t.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,o)=>{if(s)e.adoptedStyleSheets=o.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const s of o){const o=document.createElement("style"),r=t.litNonce;void 0!==r&&o.setAttribute("nonce",r),o.textContent=s.cssText,e.appendChild(o)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){const s=this.constructor.elementProperties.get(e),o=this.constructor._$Eu(e,s);if(void 0!==o&&!0===s.reflect){const r=(void 0!==s.converter?.toAttribute?s.converter:x).toAttribute(t,s.type);this._$Em=e,null==r?this.removeAttribute(o):this.setAttribute(o,r),this._$Em=null}}_$AK(e,t){const s=this.constructor,o=s._$Eh.get(e);if(void 0!==o&&this._$Em!==o){const e=s.getPropertyOptions(o),r="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:x;this._$Em=o;const a=r.fromAttribute(t,e.type);this[o]=a??this._$Ej?.get(o)??a,this._$Em=null}}requestUpdate(e,t,s,o=!1,r){if(void 0!==e){const a=this.constructor;if(!1===o&&(r=this[e]),s??=a.getPropertyOptions(e),!((s.hasChanged??w)(r,t)||s.useDefault&&s.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(a._$Eu(e,s))))return;this.C(e,t,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:o,wrapped:r},a){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,a??t??this[e]),!0!==r||void 0!==a)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),!0===o&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,s]of e){const{wrapped:e}=s,o=this[t];!0!==e||this._$AL.has(t)||void 0===o||this.C(t,void 0,s,o)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};E.elementStyles=[],E.shadowRootOptions={mode:"open"},E[b("elementProperties")]=new Map,E[b("finalized")]=new Map,v?.({ReactiveElement:E}),(g.reactiveElementVersions??=[]).push("2.1.2");const C=globalThis,M=e=>e,O=C.trustedTypes,P=O?O.createPolicy("lit-html",{createHTML:e=>e}):void 0,U="$lit$",T=`lit$${Math.random().toFixed(9).slice(2)}$`,N="?"+T,j=`<${N}>`,D=document,B=()=>D.createComment(""),K=e=>null===e||"object"!=typeof e&&"function"!=typeof e,W=Array.isArray,q="[ \t\n\f\r]",F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,G=/-->/g,V=/>/g,J=RegExp(`>|${q}(?:([^\\s"'>=/]+)(${q}*=${q}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),X=/'/g,Y=/"/g,Q=/^(?:script|style|textarea|title)$/i,ee=e=>(t,...s)=>({_$litType$:e,strings:t,values:s}),te=ee(1),ie=ee(2),se=Symbol.for("lit-noChange"),oe=Symbol.for("lit-nothing"),re=new WeakMap,ne=D.createTreeWalker(D,129);function ae(e,t){if(!W(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==P?P.createHTML(t):t}const le=(e,t)=>{const s=e.length-1,o=[];let r,a=2===t?"<svg>":3===t?"<math>":"",l=F;for(let t=0;t<s;t++){const s=e[t];let c,d,h=-1,u=0;for(;u<s.length&&(l.lastIndex=u,d=l.exec(s),null!==d);)u=l.lastIndex,l===F?"!--"===d[1]?l=G:void 0!==d[1]?l=V:void 0!==d[2]?(Q.test(d[2])&&(r=RegExp("</"+d[2],"g")),l=J):void 0!==d[3]&&(l=J):l===J?">"===d[0]?(l=r??F,h=-1):void 0===d[1]?h=-2:(h=l.lastIndex-d[2].length,c=d[1],l=void 0===d[3]?J:'"'===d[3]?Y:X):l===Y||l===X?l=J:l===G||l===V?l=F:(l=J,r=void 0);const p=l===J&&e[t+1].startsWith("/>")?" ":"";a+=l===F?s+j:h>=0?(o.push(c),s.slice(0,h)+U+s.slice(h)+T+p):s+T+(-2===h?t:p)}return[ae(e,a+(e[s]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),o]};class S{constructor({strings:e,_$litType$:t},s){let o;this.parts=[];let r=0,a=0;const l=e.length-1,c=this.parts,[d,h]=le(e,t);if(this.el=S.createElement(d,s),ne.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(o=ne.nextNode())&&c.length<l;){if(1===o.nodeType){if(o.hasAttributes())for(const e of o.getAttributeNames())if(e.endsWith(U)){const t=h[a++],s=o.getAttribute(e).split(T),l=/([.?@])?(.*)/.exec(t);c.push({type:1,index:r,name:l[2],strings:s,ctor:"."===l[1]?I:"?"===l[1]?L:"@"===l[1]?z:H}),o.removeAttribute(e)}else e.startsWith(T)&&(c.push({type:6,index:r}),o.removeAttribute(e));if(Q.test(o.tagName)){const e=o.textContent.split(T),t=e.length-1;if(t>0){o.textContent=O?O.emptyScript:"";for(let s=0;s<t;s++)o.append(e[s],B()),ne.nextNode(),c.push({type:2,index:++r});o.append(e[t],B())}}}else if(8===o.nodeType)if(o.data===N)c.push({type:2,index:r});else{let e=-1;for(;-1!==(e=o.data.indexOf(T,e+1));)c.push({type:7,index:r}),e+=T.length-1}r++}}static createElement(e,t){const s=D.createElement("template");return s.innerHTML=e,s}}function ce(e,t,s=e,o){if(t===se)return t;let r=void 0!==o?s._$Co?.[o]:s._$Cl;const a=K(t)?void 0:t._$litDirective$;return r?.constructor!==a&&(r?._$AO?.(!1),void 0===a?r=void 0:(r=new a(e),r._$AT(e,s,o)),void 0!==o?(s._$Co??=[])[o]=r:s._$Cl=r),void 0!==r&&(t=ce(e,r._$AS(e,t.values),r,o)),t}class R{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:s}=this._$AD,o=(e?.creationScope??D).importNode(t,!0);ne.currentNode=o;let r=ne.nextNode(),a=0,l=0,c=s[0];for(;void 0!==c;){if(a===c.index){let t;2===c.type?t=new k(r,r.nextSibling,this,e):1===c.type?t=new c.ctor(r,c.name,c.strings,this,e):6===c.type&&(t=new Z(r,this,e)),this._$AV.push(t),c=s[++l]}a!==c?.index&&(r=ne.nextNode(),a++)}return ne.currentNode=D,o}p(e){let t=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}}class k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,o){this.type=2,this._$AH=oe,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=o,this._$Cv=o?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=ce(this,e,t),K(e)?e===oe||null==e||""===e?(this._$AH!==oe&&this._$AR(),this._$AH=oe):e!==this._$AH&&e!==se&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>W(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==oe&&K(this._$AH)?this._$AA.nextSibling.data=e:this.T(D.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:s}=e,o="number"==typeof s?this._$AC(e):(void 0===s.el&&(s.el=S.createElement(ae(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===o)this._$AH.p(t);else{const e=new R(o,this),s=e.u(this.options);e.p(t),this.T(s),this._$AH=e}}_$AC(e){let t=re.get(e.strings);return void 0===t&&re.set(e.strings,t=new S(e)),t}k(e){W(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let s,o=0;for(const r of e)o===t.length?t.push(s=new k(this.O(B()),this.O(B()),this,this.options)):s=t[o],s._$AI(r),o++;o<t.length&&(this._$AR(s&&s._$AB.nextSibling,o),t.length=o)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=M(e).nextSibling;M(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class H{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,o,r){this.type=1,this._$AH=oe,this._$AN=void 0,this.element=e,this.name=t,this._$AM=o,this.options=r,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=oe}_$AI(e,t=this,s,o){const r=this.strings;let a=!1;if(void 0===r)e=ce(this,e,t,0),a=!K(e)||e!==this._$AH&&e!==se,a&&(this._$AH=e);else{const o=e;let l,c;for(e=r[0],l=0;l<r.length-1;l++)c=ce(this,o[s+l],t,l),c===se&&(c=this._$AH[l]),a||=!K(c)||c!==this._$AH[l],c===oe?e=oe:e!==oe&&(e+=(c??"")+r[l+1]),this._$AH[l]=c}a&&!o&&this.j(e)}j(e){e===oe?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class I extends H{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===oe?void 0:e}}class L extends H{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==oe)}}class z extends H{constructor(e,t,s,o,r){super(e,t,s,o,r),this.type=5}_$AI(e,t=this){if((e=ce(this,e,t,0)??oe)===se)return;const s=this._$AH,o=e===oe&&s!==oe||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,r=e!==oe&&(s===oe||o);o&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Z{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){ce(this,e)}}const de=C.litHtmlPolyfillSupport;de?.(S,k),(C.litHtmlVersions??=[]).push("3.3.3");const he=globalThis;class i extends E{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,s)=>{const o=s?.renderBefore??t;let r=o._$litPart$;if(void 0===r){const e=s?.renderBefore??null;o._$litPart$=r=new k(t.insertBefore(B(),e),e,void 0,s??{})}return r._$AI(e),r})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return se}}i._$litElement$=!0,i.finalized=!0,he.litElementHydrateSupport?.({LitElement:i});const ue=he.litElementPolyfillSupport;ue?.({LitElement:i}),(he.litElementVersions??=[]).push("4.2.2");const pe={attribute:!0,type:String,converter:x,reflect:!1,hasChanged:w},fe=(e=pe,t,s)=>{const{kind:o,metadata:r}=s;let a=globalThis.litPropertyMetadata.get(r);if(void 0===a&&globalThis.litPropertyMetadata.set(r,a=new Map),"setter"===o&&((e=Object.create(e)).wrapped=!0),a.set(s.name,e),"accessor"===o){const{name:o}=s;return{set(s){const r=t.get.call(this);t.set.call(this,s),this.requestUpdate(o,r,e,!0,s)},init(t){return void 0!==t&&this.C(o,void 0,e,t),t}}}if("setter"===o){const{name:o}=s;return function(s){const r=this[o];t.call(this,s),this.requestUpdate(o,r,e,!0,s)}}throw Error("Unsupported decorator location: "+o)};function _e(e){return(t,s)=>"object"==typeof s?fe(e,t,s):((e,t,s)=>{const o=t.hasOwnProperty(s);return t.constructor.createProperty(s,e),o?Object.getOwnPropertyDescriptor(t,s):void 0})(e,t,s)}function ge(e){return _e({...e,state:!0,attribute:!1})}const me="maico_kwl",$e=new Set(["unavailable","unknown"]);function ve(e){const t=new Set;for(const s of Object.values(e.entities))s.platform===me&&s.device_id&&t.add(s.device_id);return[...t]}class KwlDevice{constructor(e,t){this._hass=e,this.deviceId=t,this._entityIds=new Map;for(const s of Object.values(e.entities))s.platform===me&&s.device_id===t&&s.translation_key&&this._entityIds.set(s.translation_key,s.entity_id)}get name(){const e=this._hass.devices[this.deviceId];return e?.name_by_user||e?.name||"Maico KWL"}entityId(e){return this._entityIds.get(e)}has(e){return void 0!==this.stateObj(e)}stateObj(e){const t=this._entityIds.get(e),s=t?this._hass.states[t]:void 0;return s&&!$e.has(s.state)?s:void 0}state(e){return this.stateObj(e)?.state}number(e){const t=Number(this.state(e));return void 0===this.state(e)||Number.isNaN(t)?void 0:t}isOn(e){const t=this.state(e);return void 0===t?void 0:"on"===t}attribute(e,t){return this.stateObj(e)?.attributes[t]}format(e){const t=this.stateObj(e);return t?this._hass.formatEntityState(t):void 0}present(e){return e.filter(e=>this.has(e))}}const ye="temp_air_intake",be="temp_supply_air",xe="temp_extract_air",we="temp_exhaust_air",ke="airflow_supply",Ae="airflow_exhaust",Se="fan_speed_supply",Ee="fan_speed_exhaust",Ce="fan_supply_active",Me="fan_exhaust_active",Oe="summer_bypass_open",Pe="ptc_heater_active",Ue="heat_recovery_efficiency",He="heat_recovery_power",Ie="room_temp_source",Re="temp_room",Te="temp_room_external",Ne="room_temp_bus_sent",je="humidity_exhaust",ze="humidity_bus_sent",Le="air_quality_bus_sent",De="operating_mode",Be="ventilation_level",Ke="current_vent_level",We="boost_ventilation",qe="off_lock",Fe="filter_remaining_device",Ge="filter_remaining_outdoor",Ve="filter_remaining_room",Ze="filter_runtime_device",Je="filter_runtime_outdoor",Xe="filter_runtime_room",Ye="filter_next_change",Qe="fault_code",et="notice_code",tt=["humidity_sensor_1","humidity_sensor_2","humidity_sensor_3","humidity_sensor_4","enocean_humidity_id0","enocean_humidity_id1","enocean_humidity_id2","enocean_humidity_id3","enocean_humidity_id4","enocean_humidity_id5","enocean_humidity_id6","enocean_humidity_id7"],it=["co2_sensor_1","co2_sensor_2","co2_sensor_3","co2_sensor_4","enocean_co2_id0","enocean_co2_id1","enocean_co2_id2","enocean_co2_id3","enocean_co2_id4","enocean_co2_id5","enocean_co2_id6","enocean_co2_id7"],st=["voc_sensor_1","voc_sensor_2","voc_sensor_3","voc_sensor_4","enocean_voc_id0","enocean_voc_id1","enocean_voc_id2","enocean_voc_id3","enocean_voc_id4","enocean_voc_id5","enocean_voc_id6","enocean_voc_id7"],ot={en:{card_name:"Maico KWL",card_description:"Airflow, temperatures and controls of a Maico ventilation unit.",no_device:"No Maico KWL unit found.",device_missing:"The selected unit no longer exists.",editor_device:"Unit",group_airflow:"Airflow",group_room:"Room",group_controls:"Controls",group_filters:"Filters",group_status:"Status",outdoor_air:"Outdoor air",supply_air:"Supply air",extract_air:"Extract air",exhaust_air:"Exhaust air",bypass_open:"Bypass open",bypass_closed:"Bypass closed",heat_recovery:"Heat recovery",fan_off:"off",ptc_heater:"PTC heater",tile_room:"Room",tile_humidity:"Humidity",tile_air_quality:"Air quality",tile_heat_recovery:"Heat recovery",bus_badge:"BUS",from_source:"from {name}",bus_stale:"no new value for {minutes} min",bus_never:"no value sent yet",sub_extract_air:"extract air",sub_external_sensor:"external sensor",air_good:"good",air_moderate:"moderate",air_poor:"poor",ventilation_level:"Ventilation level",operating_mode:"Operating mode",boost:"Boost",level_off:"Off",level_humidity_protection:"Humidity",level_reduced:"Reduced",level_nominal:"Nominal",level_intensive:"Intensive",level_auto_hint:"Level is chosen by {mode}",filter_device:"Device filter",filter_outdoor:"Outdoor filter",filter_room:"Room filter",filter_days:"{days} days",filter_due:"due",filter_next_change:"Next change on {date}",notices_one:"1 notice",notices_many:"{count} notices",faults_one:"Fault",faults_many:"{count} faults"},de:{card_name:"Maico KWL",card_description:"Luftströme, Temperaturen und Bedienung eines Maico-Lüftungsgeräts.",no_device:"Kein Maico-KWL-Gerät gefunden.",device_missing:"Das gewählte Gerät gibt es nicht mehr.",editor_device:"Gerät",group_airflow:"Luftstrom",group_room:"Raum",group_controls:"Bedienung",group_filters:"Filter",group_status:"Status",outdoor_air:"Außenluft",supply_air:"Zuluft",extract_air:"Abluft",exhaust_air:"Fortluft",bypass_open:"Bypass offen",bypass_closed:"Bypass zu",heat_recovery:"Rückgewinnung",fan_off:"aus",ptc_heater:"PTC-Heizregister",tile_room:"Raum",tile_humidity:"Feuchte",tile_air_quality:"Luftgüte",tile_heat_recovery:"Rückgewinnung",bus_badge:"BUS",from_source:"von {name}",bus_stale:"seit {minutes} min kein neuer Wert",bus_never:"noch kein Wert gesendet",sub_extract_air:"Abluft",sub_external_sensor:"externer Fühler",air_good:"gut",air_moderate:"mäßig",air_poor:"schlecht",ventilation_level:"Lüftungsstufe",operating_mode:"Betriebsart",boost:"Stoßlüftung",level_off:"Aus",level_humidity_protection:"Feuchte",level_reduced:"Reduziert",level_nominal:"Nenn",level_intensive:"Intensiv",level_auto_hint:"Stufe wird von {mode} gewählt",filter_device:"Gerätefilter",filter_outdoor:"Außenluftfilter",filter_room:"Raumfilter",filter_days:"{days} Tage",filter_due:"fällig",filter_next_change:"Nächster Wechsel am {date}",notices_one:"1 Hinweis",notices_many:"{count} Hinweise",faults_one:"Störung",faults_many:"{count} Störungen"}};function rt(e,t,s={}){const o=(e?.locale?.language??e?.language??"en").split("-")[0];return(o in ot?ot[o]:ot.en)[t].replace(/\{(\w+)\}/g,(e,t)=>t in s?String(s[t]):e)}function nt(e){const t=navigator.language.split("-")[0];return(t in ot?ot[t]:ot.en)[e]}const at=["off","humidity_protection","reduced","nominal","intensive"],lt=new Set(["auto_time","auto_sensor"]),ct=[["filter_device",Fe,Ze],["filter_outdoor",Ge,Je],["filter_room",Ve,Xe]],dt={level:e=>e.state(Ke)??e.state(Be),mode:e=>e.state(De),boost:e=>e.state(We)};function ht(e,t,s,o){const r=e.device.entityId(s);r&&e.change(t,o,()=>e.hass.callService("select","select_option",{entity_id:r,option:o}))}function ut(e){return te`${function(e){const{hass:t,device:s}=e,o=(e,s)=>rt(t,e,s);if(!s.stateObj(Be))return oe;const r=e.shown("mode"),a=void 0!==r&&lt.has(r),l=e.shown("level"),c=e.pending("level"),d=s.isOn(qe)??!1,h=s.stateObj(De);return te`
    <div class="control">
      <div class="control-label" id="kwl-level-label">${o("ventilation_level")}</div>
      <div class=${a?"segments locked":"segments"} role="group" aria-labelledby="kwl-level-label">
        ${at.map(t=>{const s=t===l;return te`<button
            type="button"
            class=${s?c?"segment active pending":"segment active":"segment"}
            aria-pressed=${s?"true":"false"}
            ?disabled=${a||"off"===t&&d}
            @click=${()=>ht(e,"level",Be,t)}
          >
            ${o(`level_${t}`)}
          </button>`})}
      </div>
      ${a&&h?te`<div class="hint">
            ${o("level_auto_hint",{mode:t.formatEntityState(h,r)})}
          </div>`:oe}
    </div>
  `}(e)}${function(e){const{hass:t,device:s}=e,o=e=>rt(t,e),r=s.stateObj(De),a=s.has(We)?s.entityId(We):void 0;if(!r&&!a)return oe;const l=r?.attributes.options??[],c=e.shown("mode"),d="on"===e.shown("boost"),h=["boost",d?"active":"",e.pending("boost")?"pending":""].join(" ");return te`
    <div class="mode-row">
      ${r?te`<label class="control mode">
            <span class="control-label">${o("operating_mode")}</span>
            <select
              class=${e.pending("mode")?"pending":""}
              .value=${c??""}
              @change=${t=>ht(e,"mode",De,t.target.value)}
            >
              ${l.map(e=>te`<option value=${e} ?selected=${e===c}>
                  ${t.formatEntityState(r,e)}
                </option>`)}
            </select>
          </label>`:oe}
      ${a?te`<button
            type="button"
            class=${h}
            aria-pressed=${d?"true":"false"}
            @click=${()=>e.change("boost",d?"off":"on",()=>t.callService("switch",d?"turn_off":"turn_on",{entity_id:a}))}
          >
            <svg viewBox="0 0 18 18" aria-hidden="true">
              <path d="M2 6 H11 A2.5 2.5 0 1 0 8.5 3.5"></path>
              <path d="M2 10 H14 A2.5 2.5 0 1 1 11.5 12.5"></path>
              <path d="M2 14 H7"></path>
            </svg>
            ${o("boost")}
          </button>`:oe}
    </div>
  `}(e)}${function(e){const{hass:t,device:s}=e,o=(e,s)=>rt(t,e,s),r=ct.filter(([,e])=>void 0!==s.number(e));if(!r.length)return oe;const a=s.format(Ye);return te`
    <div class="filters">
      ${r.map(([t,r,a])=>{const l=Math.max(0,Math.round(s.number(r))),c=s.number(a),d=c?Math.min(1,l/(30.44*c)):1,h=0===l?"due":l<=14?"soon":"ok";return te`
          <button type="button" class="filter" @click=${()=>e.moreInfo(r)}>
            <span class="filter-head">
              <span class="control-label">${o(t)}</span>
              <span class=${`filter-days ${h}`}>
                ${"due"===h?o("filter_due"):o("filter_days",{days:l})}
              </span>
            </span>
            <span class="bar"><span class=${`bar-fill ${h}`} style=${`width: ${100*d}%`}></span></span>
          </button>
        `})}
      ${a?te`<div class="hint">${o("filter_next_change",{date:a})}</div>`:oe}
    </div>
  `}(e)}`}const pt=l`
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
  .boost:focus-visible,
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
  select {
    height: 44px;
    padding: 0 12px;
    border: 0;
    border-radius: 10px;
    background: var(--secondary-background-color, #f5f5f5);
    color: var(--primary-text-color);
    font: inherit;
    font-size: 14px;
  }
  .boost {
    display: flex;
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
  .boost.active {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
  }
  .boost svg {
    width: 18px;
    height: 18px;
    fill: none;
    stroke: currentColor;
    stroke-width: 2px;
    stroke-linecap: round;
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
`,ft=new Set(["bypass_active"]);function _t(e,t){const s=e.attribute(t,"active");return Array.isArray(s)?s.filter(e=>"string"==typeof e):[]}function gt(e){const{hass:t,device:s}=e,o=function(e,t){const s=[];for(const[o,r]of[["fault",Qe],["notice",et]]){const a=t.stateObj(r);if(a)for(const l of _t(t,r))"notice"===o&&ft.has(l)||s.push({kind:o,text:e.formatEntityAttributeValue(a,"active",l)})}return s}(t,s),r=o.filter(e=>"fault"===e.kind).length,a=o.length-r,l=r?1===r?rt(t,"faults_one"):rt(t,"faults_many",{count:r}):1===a?rt(t,"notices_one"):rt(t,"notices_many",{count:a});return te`
    <div class="header">
      <div class="title">${s.name}</div>
      ${o.length?te`<button
            type="button"
            class=${r?"chip fault":"chip notice"}
            aria-expanded=${e.expanded?"true":"false"}
            @click=${e.toggle}
          >
            <svg viewBox="0 0 16 16" aria-hidden="true">
              <circle cx="8" cy="8" r="6.5"></circle>
              <line x1="8" y1="4.5" x2="8" y2="9"></line>
              <line x1="8" y1="11.4" x2="8" y2="11.5"></line>
            </svg>
            ${l}
          </button>`:oe}
    </div>
    ${o.length&&e.expanded?te`<ul class="messages">
          ${o.map(t=>te`<li>
              <button
                type="button"
                class=${t.kind}
                @click=${()=>e.moreInfo("fault"===t.kind?Qe:et)}
              >
                ${t.text}
              </button>
            </li>`)}
        </ul>`:oe}
  `}const mt=l`
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
`,$t=[[-10,"#0d47a1"],[0,"#1976d2"],[10,"#64b5f6"],[20,"#b8b8b8"],[25,"#ffb74d"],[30,"#f57c00"],[35,"#d32f2f"]],vt=[[-10,"#1e88e5"],[0,"#42a5f5"],[10,"#90caf9"],[20,"#a8a8a8"],[25,"#ffb74d"],[30,"#ff9800"],[35,"#ef5350"]];function yt(e,t){const s=t?vt:$t;if(void 0===e)return function(e){return(e?vt:$t)[3][1]}(t);if(e<=s[0][0])return s[0][1];for(let t=1;t<s.length;t++){const[o,r]=s[t],[a,l]=s[t-1];if(e<=o){return`color-mix(in oklab, ${r} ${Math.round((e-a)/(o-a)*100)}%, ${l})`}}return s[s.length-1][1]}function bt(e,t,s,o=5){return void 0===e||void 0===t?Array.from({length:o},(r,a)=>yt(a<o/2?e??t:t??e,s)):Array.from({length:o},(r,a)=>yt(e+(t-e)*a/(o-1),s))}const xt=62,wt=160,kt=260,At="M96 62 C 128 62, 128 22, 162 22 L 258 22 C 292 22, 292 62, 324 62";const St=l`
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
`;function Et(e,t){const s=e.states[t]?.attributes.friendly_name;return"string"==typeof s?s:t}function Ct(e,t,s,o,r,a){const l=t.format(r),c=t.attribute(r,"source_entity");if(void 0===l||!c)return;const d=t.attribute(r,"last_written"),h=d?Math.floor((a-Date.parse(d))/6e4):void 0,u=void 0===h||h>=10;return{label:o,key:r,moreInfo:c,value:l,sub:void 0===h?s("bus_never"):u?s("bus_stale",{minutes:h}):s("from_source",{name:Et(e,c)}),bus:{stale:u}}}function Mt(e,t,s,o){const r=t.present(o).filter(e=>void 0!==t.number(e));if(!r.length)return;const a=r.reduce((e,s)=>t.number(s)>t.number(e)?s:e),l=t.entityId(a);return{label:s,key:a,moreInfo:l,value:t.format(a),sub:r.length>1?Et(e,l):void 0}}function Ot(e,t,s,o){const r=e.format(s);return void 0===r?void 0:{label:t,key:s,moreInfo:e.entityId(s),value:r,sub:o}}function Pt(e,t,s,o){switch(t.state(Ie)){case"bus":return Ct(e,t,s,"tile_room",Ne,o)??Ot(t,"tile_room",Re);case"external":return Ot(t,"tile_room",Te,s("sub_external_sensor"))??Ot(t,"tile_room",Re);default:return Ot(t,"tile_room",Re)}}function Ut(e,t,s,o){return Ct(e,t,s,"tile_humidity",ze,o)??Mt(e,t,"tile_humidity",tt)??Ot(t,"tile_humidity",je,s("sub_extract_air"))}function Ht(e,t,s,o){const r=Mt(e,t,"tile_air_quality",it)??Mt(e,t,"tile_air_quality",st)??Ct(e,t,s,"tile_air_quality",Le,o);if(!r)return;const a=t.number(r.key);return void 0!==a&&(r.air=a<=800?"good":a<=1400?"moderate":"poor"),r}function It(e){return Ot(e,"tile_heat_recovery",He)}const Rt=l`
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
    overflow: hidden;
    max-width: 100%;
    font-size: 11px;
    color: var(--secondary-text-color);
    white-space: nowrap;
    text-overflow: ellipsis;
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
`,Tt="maico-kwl-card";class MaicoKwlCard extends i{constructor(){super(...arguments),this._uid=`kwl${Math.random().toString(36).slice(2,10)}`,this._pending=new Map,this._messagesExpanded=!1}setConfig(e){this._config=e}getCardSize(){return 6}static async getConfigElement(){const{EDITOR_TYPE:e}=await(import("./editor-uf46Gy5c.js"));return document.createElement(e)}static getStubConfig(e){const[t]=ve(e);return t?{device_id:t}:{}}disconnectedCallback(){super.disconnectedCallback();for(const e of[...this._pending.keys()])this._clearPending(e)}willUpdate(e){if(!e.has("hass")||!this._pending.size||!this.hass)return;const t=this._device();if(t)for(const[e,s]of this._pending)dt[e](t)===s.value&&this._clearPending(e)}_clearPending(e){const t=this._pending.get(e);t&&(window.clearTimeout(t.timer),this._pending.delete(e),this._pending=new Map(this._pending))}_controls(e){return{hass:this.hass,device:e,moreInfo:t=>this._moreInfo(e.entityId(t)),shown:t=>this._pending.get(t)?.value??dt[t](e),pending:e=>this._pending.has(e),change:(t,s,o)=>{if(this._clearPending(t),dt[t](e)===s)return void o();const r=window.setTimeout(()=>this._clearPending(t),35e3);this._pending=new Map(this._pending).set(t,{value:s,timer:r}),o().catch(()=>this._clearPending(t))}}}_device(){const e=this._config?.device_id??ve(this.hass)[0];if(e&&this.hass.devices[e])return new KwlDevice(this.hass,e)}render(){if(!this.hass||!this._config)return oe;const e=this._device();if(!e){const e=this._config.device_id?"device_missing":"no_device";return te`<ha-card><p class="empty">${rt(this.hass,e)}</p></ha-card>`}return te`
      <ha-card class=${this.hass.themes?.darkMode?"dark":""}>
        ${gt({hass:this.hass,device:e,expanded:this._messagesExpanded,toggle:()=>this._messagesExpanded=!this._messagesExpanded,moreInfo:t=>this._moreInfo(e.entityId(t))})}
        <div class="content">
          ${function(e){const{hass:t,device:s,uid:o}=e,r=t.themes?.darkMode??!1,a=e=>rt(t,e),l=s.number(ye),c=s.number(be),d=s.number(xe),h=s.number(we),u=s.has(Oe),p=s.isOn(Oe)??!1,f=s.isOn(Ce)??(s.number(ke)??0)>0,_=s.isOn(Me)??(s.number(Ae)??0)>0,g=bt(l,c,r),m=bt(h,d,r),$=yt(l,r),v=yt(c,r),b=yt(h,r),x=yt(d,r),w=p?"M20 62 L96 62 M324 62 L392 62":"M20 62 L392 62",A="M400 142 L28 142",E=e=>`${Math.min(12,Math.max(2,810/Math.max(e??180,1))).toFixed(2)}s`,C=(t,o,r)=>s.entityId(t)?ie`<g class="clickable" role="button" tabindex="0" aria-label=${r}
          @click=${()=>e.moreInfo(t)}
          @keydown=${s=>{"Enter"!==s.key&&" "!==s.key||(s.preventDefault(),e.moreInfo(t))}}>${o}</g>`:o,M=(e,t,o,r,a,l,c)=>{if(void 0===o)return oe;const d=s.format(e),h="left"===a;return C(e,ie`
        <text class="name" x=${h?20:400} y=${l} text-anchor=${h?"start":"end"}>${t}</text>
        <circle cx=${h?24:396} cy=${c-7} r="4" style=${`fill: ${r}`}></circle>
        <text class="value" x=${h?34:386} y=${c} text-anchor=${h?"start":"end"}>${d}</text>
      `,`${t} ${d}`)},O=(e,t,o,r,l,c)=>{const d=s.number(r),h=d&&d>0?`${(4e3/d).toFixed(2)}s`:"2s",u=o?s.format(r):a("fan_off"),p=o?s.format(l):void 0;return C(r,ie`
        <circle class="fan-housing" cx=${e} cy=${t} r="13"></circle>
        <g class=${o?"rotor spinning":"rotor"} style=${`animation-duration: ${h}`}>
          <circle cx=${e} cy=${t} r="13" fill="none" stroke="none"></circle>
          ${[0,120,240].map(s=>ie`<ellipse cx=${e} cy=${t-6} rx="3" ry="5.5" transform=${`rotate(${s} ${e} ${t})`}></ellipse>`)}
        </g>
        ${u?ie`<text class="fan-speed" x=${e} y=${c} text-anchor="middle">${u}</text>`:oe}
        ${p?ie`<text class="small" x=${e} y=${c+14} text-anchor="middle">${p}</text>`:oe}
      `,`${u??""} ${p??""}`)},P=s.format(Ue);return te`
    <svg class="schematic" viewBox="0 -14 420 214" role="img"
      aria-label=${[a("outdoor_air"),a("supply_air"),a("extract_air"),a("exhaust_air")].join(", ")}>
      <defs>
        <linearGradient id=${`${o}-top`} gradientUnits="userSpaceOnUse" x1=${wt} y1="0" x2=${kt} y2="0">
          ${g.map((e,t)=>ie`<stop offset=${t/(g.length-1)} style=${`stop-color: ${e}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${o}-bottom`} gradientUnits="userSpaceOnUse" x1=${wt} y1="0" x2=${kt} y2="0">
          ${m.map((e,t)=>ie`<stop offset=${t/(m.length-1)} style=${`stop-color: ${e}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${o}-sheen`}>
          <stop offset="0" stop-color="#000"></stop>
          <stop offset="0.5" stop-color="#fff"></stop>
          <stop offset="1" stop-color="#000"></stop>
        </linearGradient>
        <mask id=${`${o}-sheen-right`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen" x="-140" y="-14" width="140" height="214" fill=${`url(#${o}-sheen)`}
            style=${`animation-duration: ${E(s.number(ke))}`}></rect>
        </mask>
        <mask id=${`${o}-sheen-left`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen reverse" x="-140" y="-14" width="140" height="214" fill=${`url(#${o}-sheen)`}
            style=${`animation-duration: ${E(s.number(Ae))}`}></rect>
        </mask>
      </defs>

      <rect class="exchanger" x=${wt} y="34" width=${100} height="136" rx="12"></rect>
      <line class="exchanger-line" x1=${wt} y1="34" x2=${kt} y2="170"></line>
      <line class="exchanger-line" x1=${kt} y1="34" x2=${wt} y2="170"></line>

      ${u?C(Oe,ie`
              <path class=${p?"tube":"bypass-closed"} d=${At}
                style=${p?`stroke: ${$}`:""}></path>
              <text class=${p?"bypass-label open":"bypass-label"} x="210" y="6" text-anchor="middle">
                ${a(p?"bypass_open":"bypass_closed")}
              </text>`,a(p?"bypass_open":"bypass_closed")):oe}

      <path class="tube" d=${w} stroke=${`url(#${o}-top)`}></path>
      ${p?ie`<path class="passage" d=${"M96 62 L324 62"}></path>`:oe}
      <path class="tube" d=${A} stroke=${`url(#${o}-bottom)`}></path>
      <polygon points="396,57 406,62 396,67" style=${`fill: ${v}`}></polygon>
      <polygon points="24,137 14,142 24,147" style=${`fill: ${b}`}></polygon>

      ${f?ie`<g class="sheen-layer" mask=${`url(#${o}-sheen-right)`}>
            <path class="tube-sheen" d=${w} stroke=${`url(#${o}-top)`}></path>
            ${p?ie`<path class="tube-sheen" d=${At} style=${`stroke: ${$}`}></path>`:oe}
          </g>`:oe}
      ${_?ie`<g class="sheen-layer" mask=${`url(#${o}-sheen-left)`}>
            <path class="tube-sheen" d=${A} stroke=${`url(#${o}-bottom)`}></path>
          </g>`:oe}

      ${(()=>{if(!s.has(Pe))return oe;const e=s.isOn(Pe)??!1;return C(Pe,ie`<g class=${e?"ptc active":"ptc"}>
        <rect x=${47} y=${53} width="22" height="18" rx="4"></rect>
        <path d=${"M51 62 l3 -4 l4 8 l4 -8 l3 4"}></path>
      </g>`,a("ptc_heater"))})()}

      ${P?C(Ue,ie`
              <rect class="exchanger" x="166" y="80" width="88" height="44" rx="8" stroke="none"></rect>
              <text class="value" x="210" y="102" text-anchor="middle">${P}</text>
              <text class="small" x="210" y="117" text-anchor="middle">${a("heat_recovery")}</text>`,`${a("heat_recovery")} ${P}`):oe}

      ${O(340,xt,f,Se,ke,96)}
      ${O(80,142,_,Ee,Ae,104)}

      ${M(ye,a("outdoor_air"),l,$,"left",18,42)}
      ${M(be,a("supply_air"),c,v,"right",18,42)}
      ${M(xe,a("extract_air"),d,x,"right",194,176)}
      ${M(we,a("exhaust_air"),h,b,"left",194,176)}
    </svg>
  `}({hass:this.hass,device:e,uid:this._uid,moreInfo:t=>this._moreInfo(e.entityId(t))})}
          ${function(e,t,s){if(!t.length)return oe;const o=t=>rt(e,t);return te`
    <div class="tiles">
      ${t.map(e=>te`
          <button class="tile" type="button" @click=${()=>s(e.moreInfo)}>
            <span class="tile-label">
              ${o(e.label)}
              ${e.bus?te`<span class=${e.bus.stale?"badge stale":"badge"}>${o("bus_badge")}</span>`:oe}
            </span>
            <span class="tile-value">
              ${e.air?te`<span class=${`dot air-${e.air}`} title=${o(`air_${e.air}`)}></span>`:oe}
              ${e.value}
            </span>
            ${e.sub?te`<span class=${e.bus?.stale?"tile-sub stale":"tile-sub"}>${e.sub}</span>`:oe}
          </button>
        `)}
    </div>
  `}(this.hass,function(e,t,s=Date.now()){const o=(t,s)=>rt(e,t,s);return[Pt(e,t,o,s),Ut(e,t,o,s),Ht(e,t,o,s),It(t)].filter(e=>void 0!==e)}(this.hass,e),e=>this._moreInfo(e))}
          ${ut(this._controls(e))}
        </div>
      </ha-card>
    `}_moreInfo(e){e&&this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:e},bubbles:!0,composed:!0}))}}MaicoKwlCard.styles=[mt,St,Rt,pt,l`
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
  `],e([_e({attribute:!1})],MaicoKwlCard.prototype,"hass",void 0),e([ge()],MaicoKwlCard.prototype,"_config",void 0),e([ge()],MaicoKwlCard.prototype,"_pending",void 0),e([ge()],MaicoKwlCard.prototype,"_messagesExpanded",void 0),customElements.get(Tt)||(customElements.define(Tt,MaicoKwlCard),window.customCards=window.customCards??[],window.customCards.push({type:Tt,name:nt("card_name"),description:nt("card_description"),preview:!0}));var Nt=Object.freeze({__proto__:null,MaicoKwlCard:MaicoKwlCard});export{oe as A,me as D,e as _,te as b,Nt as c,i,rt as l,_e as n,ge as r};
