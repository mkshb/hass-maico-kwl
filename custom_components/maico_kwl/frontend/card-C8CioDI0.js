function e(e,t,s,o){var r,a=arguments.length,l=a<3?t:null===o?o=Object.getOwnPropertyDescriptor(t,s):o;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)l=Reflect.decorate(e,t,s,o);else for(var c=e.length-1;c>=0;c--)(r=e[c])&&(l=(a<3?r(l):a>3?r(t,s,l):r(t,s))||l);return a>3&&l&&Object.defineProperty(t,s,l),l}"function"==typeof SuppressedError&&SuppressedError;const t=globalThis,s=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,o=Symbol(),r=new WeakMap;let a=class n{constructor(e,t,s){if(this._$cssResult$=!0,s!==o)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(s&&void 0===e){const s=void 0!==t&&1===t.length;s&&(e=r.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&r.set(t,e))}return e}toString(){return this.cssText}};const l=(e,...t)=>{const s=1===e.length?e[0]:t.reduce((t,s,o)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+e[o+1],e[0]);return new a(s,e,o)},c=s?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const s of e.cssRules)t+=s.cssText;return(e=>new a("string"==typeof e?e:e+"",void 0,o))(t)})(e):e,{is:d,defineProperty:h,getOwnPropertyDescriptor:u,getOwnPropertyNames:p,getOwnPropertySymbols:f,getPrototypeOf:_}=Object,g=globalThis,m=g.trustedTypes,$=m?m.emptyScript:"",v=g.reactiveElementPolyfillSupport,b=(e,t)=>e,x={toAttribute(e,t){switch(t){case Boolean:e=e?$:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let s=e;switch(t){case Boolean:s=null!==e;break;case Number:s=null===e?null:Number(e);break;case Object:case Array:try{s=JSON.parse(e)}catch(e){s=null}}return s}},w=(e,t)=>!d(e,t),C={attribute:!0,type:String,converter:x,reflect:!1,useDefault:!1,hasChanged:w};Symbol.metadata??=Symbol("metadata"),g.litPropertyMetadata??=new WeakMap;let A=class y extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=C){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const s=Symbol(),o=this.getPropertyDescriptor(e,s,t);void 0!==o&&h(this.prototype,e,o)}}static getPropertyDescriptor(e,t,s){const{get:o,set:r}=u(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:o,set(t){const a=o?.call(this);r?.call(this,t),this.requestUpdate(e,a,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??C}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;const e=_(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){const e=this.properties,t=[...p(e),...f(e)];for(const s of t)this.createProperty(s,e[s])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,s]of t)this.elementProperties.set(e,s)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const s=this._$Eu(e,t);void 0!==s&&this._$Eh.set(s,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const s=new Set(e.flat(1/0).reverse());for(const e of s)t.unshift(c(e))}else void 0!==e&&t.push(c(e));return t}static _$Eu(e,t){const s=t.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,o)=>{if(s)e.adoptedStyleSheets=o.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const s of o){const o=document.createElement("style"),r=t.litNonce;void 0!==r&&o.setAttribute("nonce",r),o.textContent=s.cssText,e.appendChild(o)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){const s=this.constructor.elementProperties.get(e),o=this.constructor._$Eu(e,s);if(void 0!==o&&!0===s.reflect){const r=(void 0!==s.converter?.toAttribute?s.converter:x).toAttribute(t,s.type);this._$Em=e,null==r?this.removeAttribute(o):this.setAttribute(o,r),this._$Em=null}}_$AK(e,t){const s=this.constructor,o=s._$Eh.get(e);if(void 0!==o&&this._$Em!==o){const e=s.getPropertyOptions(o),r="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:x;this._$Em=o;const a=r.fromAttribute(t,e.type);this[o]=a??this._$Ej?.get(o)??a,this._$Em=null}}requestUpdate(e,t,s,o=!1,r){if(void 0!==e){const a=this.constructor;if(!1===o&&(r=this[e]),s??=a.getPropertyOptions(e),!((s.hasChanged??w)(r,t)||s.useDefault&&s.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(a._$Eu(e,s))))return;this.C(e,t,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:o,wrapped:r},a){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,a??t??this[e]),!0!==r||void 0!==a)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),!0===o&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,s]of e){const{wrapped:e}=s,o=this[t];!0!==e||this._$AL.has(t)||void 0===o||this.C(t,void 0,s,o)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[b("elementProperties")]=new Map,A[b("finalized")]=new Map,v?.({ReactiveElement:A}),(g.reactiveElementVersions??=[]).push("2.1.2");const M=globalThis,E=e=>e,O=M.trustedTypes,P=O?O.createPolicy("lit-html",{createHTML:e=>e}):void 0,U="$lit$",T=`lit$${Math.random().toFixed(9).slice(2)}$`,j="?"+T,N=`<${j}>`,V=document,D=()=>V.createComment(""),B=e=>null===e||"object"!=typeof e&&"function"!=typeof e,K=Array.isArray,W="[ \t\n\f\r]",F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,q=/-->/g,G=/>/g,J=RegExp(`>|${W}(?:([^\\s"'>=/]+)(${W}*=${W}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),X=/'/g,Y=/"/g,Q=/^(?:script|style|textarea|title)$/i,ee=e=>(t,...s)=>({_$litType$:e,strings:t,values:s}),te=ee(1),ie=ee(2),se=Symbol.for("lit-noChange"),oe=Symbol.for("lit-nothing"),ne=new WeakMap,re=V.createTreeWalker(V,129);function ae(e,t){if(!K(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==P?P.createHTML(t):t}const le=(e,t)=>{const s=e.length-1,o=[];let r,a=2===t?"<svg>":3===t?"<math>":"",l=F;for(let t=0;t<s;t++){const s=e[t];let c,d,h=-1,u=0;for(;u<s.length&&(l.lastIndex=u,d=l.exec(s),null!==d);)u=l.lastIndex,l===F?"!--"===d[1]?l=q:void 0!==d[1]?l=G:void 0!==d[2]?(Q.test(d[2])&&(r=RegExp("</"+d[2],"g")),l=J):void 0!==d[3]&&(l=J):l===J?">"===d[0]?(l=r??F,h=-1):void 0===d[1]?h=-2:(h=l.lastIndex-d[2].length,c=d[1],l=void 0===d[3]?J:'"'===d[3]?Y:X):l===Y||l===X?l=J:l===q||l===G?l=F:(l=J,r=void 0);const p=l===J&&e[t+1].startsWith("/>")?" ":"";a+=l===F?s+N:h>=0?(o.push(c),s.slice(0,h)+U+s.slice(h)+T+p):s+T+(-2===h?t:p)}return[ae(e,a+(e[s]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),o]};class S{constructor({strings:e,_$litType$:t},s){let o;this.parts=[];let r=0,a=0;const l=e.length-1,c=this.parts,[d,h]=le(e,t);if(this.el=S.createElement(d,s),re.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(o=re.nextNode())&&c.length<l;){if(1===o.nodeType){if(o.hasAttributes())for(const e of o.getAttributeNames())if(e.endsWith(U)){const t=h[a++],s=o.getAttribute(e).split(T),l=/([.?@])?(.*)/.exec(t);c.push({type:1,index:r,name:l[2],strings:s,ctor:"."===l[1]?I:"?"===l[1]?L:"@"===l[1]?z:H}),o.removeAttribute(e)}else e.startsWith(T)&&(c.push({type:6,index:r}),o.removeAttribute(e));if(Q.test(o.tagName)){const e=o.textContent.split(T),t=e.length-1;if(t>0){o.textContent=O?O.emptyScript:"";for(let s=0;s<t;s++)o.append(e[s],D()),re.nextNode(),c.push({type:2,index:++r});o.append(e[t],D())}}}else if(8===o.nodeType)if(o.data===j)c.push({type:2,index:r});else{let e=-1;for(;-1!==(e=o.data.indexOf(T,e+1));)c.push({type:7,index:r}),e+=T.length-1}r++}}static createElement(e,t){const s=V.createElement("template");return s.innerHTML=e,s}}function ce(e,t,s=e,o){if(t===se)return t;let r=void 0!==o?s._$Co?.[o]:s._$Cl;const a=B(t)?void 0:t._$litDirective$;return r?.constructor!==a&&(r?._$AO?.(!1),void 0===a?r=void 0:(r=new a(e),r._$AT(e,s,o)),void 0!==o?(s._$Co??=[])[o]=r:s._$Cl=r),void 0!==r&&(t=ce(e,r._$AS(e,t.values),r,o)),t}class R{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:s}=this._$AD,o=(e?.creationScope??V).importNode(t,!0);re.currentNode=o;let r=re.nextNode(),a=0,l=0,c=s[0];for(;void 0!==c;){if(a===c.index){let t;2===c.type?t=new k(r,r.nextSibling,this,e):1===c.type?t=new c.ctor(r,c.name,c.strings,this,e):6===c.type&&(t=new Z(r,this,e)),this._$AV.push(t),c=s[++l]}a!==c?.index&&(r=re.nextNode(),a++)}return re.currentNode=V,o}p(e){let t=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}}class k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,o){this.type=2,this._$AH=oe,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=o,this._$Cv=o?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=ce(this,e,t),B(e)?e===oe||null==e||""===e?(this._$AH!==oe&&this._$AR(),this._$AH=oe):e!==this._$AH&&e!==se&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>K(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==oe&&B(this._$AH)?this._$AA.nextSibling.data=e:this.T(V.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:s}=e,o="number"==typeof s?this._$AC(e):(void 0===s.el&&(s.el=S.createElement(ae(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===o)this._$AH.p(t);else{const e=new R(o,this),s=e.u(this.options);e.p(t),this.T(s),this._$AH=e}}_$AC(e){let t=ne.get(e.strings);return void 0===t&&ne.set(e.strings,t=new S(e)),t}k(e){K(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let s,o=0;for(const r of e)o===t.length?t.push(s=new k(this.O(D()),this.O(D()),this,this.options)):s=t[o],s._$AI(r),o++;o<t.length&&(this._$AR(s&&s._$AB.nextSibling,o),t.length=o)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=E(e).nextSibling;E(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class H{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,o,r){this.type=1,this._$AH=oe,this._$AN=void 0,this.element=e,this.name=t,this._$AM=o,this.options=r,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=oe}_$AI(e,t=this,s,o){const r=this.strings;let a=!1;if(void 0===r)e=ce(this,e,t,0),a=!B(e)||e!==this._$AH&&e!==se,a&&(this._$AH=e);else{const o=e;let l,c;for(e=r[0],l=0;l<r.length-1;l++)c=ce(this,o[s+l],t,l),c===se&&(c=this._$AH[l]),a||=!B(c)||c!==this._$AH[l],c===oe?e=oe:e!==oe&&(e+=(c??"")+r[l+1]),this._$AH[l]=c}a&&!o&&this.j(e)}j(e){e===oe?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class I extends H{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===oe?void 0:e}}class L extends H{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==oe)}}class z extends H{constructor(e,t,s,o,r){super(e,t,s,o,r),this.type=5}_$AI(e,t=this){if((e=ce(this,e,t,0)??oe)===se)return;const s=this._$AH,o=e===oe&&s!==oe||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,r=e!==oe&&(s===oe||o);o&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Z{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){ce(this,e)}}const de=M.litHtmlPolyfillSupport;de?.(S,k),(M.litHtmlVersions??=[]).push("3.3.3");const he=globalThis;class i extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,s)=>{const o=s?.renderBefore??t;let r=o._$litPart$;if(void 0===r){const e=s?.renderBefore??null;o._$litPart$=r=new k(t.insertBefore(D(),e),e,void 0,s??{})}return r._$AI(e),r})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return se}}i._$litElement$=!0,i.finalized=!0,he.litElementHydrateSupport?.({LitElement:i});const ue=he.litElementPolyfillSupport;ue?.({LitElement:i}),(he.litElementVersions??=[]).push("4.2.2");const pe={attribute:!0,type:String,converter:x,reflect:!1,hasChanged:w},fe=(e=pe,t,s)=>{const{kind:o,metadata:r}=s;let a=globalThis.litPropertyMetadata.get(r);if(void 0===a&&globalThis.litPropertyMetadata.set(r,a=new Map),"setter"===o&&((e=Object.create(e)).wrapped=!0),a.set(s.name,e),"accessor"===o){const{name:o}=s;return{set(s){const r=t.get.call(this);t.set.call(this,s),this.requestUpdate(o,r,e,!0,s)},init(t){return void 0!==t&&this.C(o,void 0,e,t),t}}}if("setter"===o){const{name:o}=s;return function(s){const r=this[o];t.call(this,s),this.requestUpdate(o,r,e,!0,s)}}throw Error("Unsupported decorator location: "+o)};function _e(e){return(t,s)=>"object"==typeof s?fe(e,t,s):((e,t,s)=>{const o=t.hasOwnProperty(s);return t.constructor.createProperty(s,e),o?Object.getOwnPropertyDescriptor(t,s):void 0})(e,t,s)}function ge(e){return _e({...e,state:!0,attribute:!1})}const me="maico_kwl",ye=new Set(["unavailable","unknown"]);function $e(e){const t=new Set;for(const s of Object.values(e.entities))s.platform===me&&s.device_id&&t.add(s.device_id);return[...t]}class KwlDevice{constructor(e,t){this._hass=e,this.deviceId=t,this._entityIds=new Map;for(const s of Object.values(e.entities))s.platform===me&&s.device_id===t&&s.translation_key&&this._entityIds.set(s.translation_key,s.entity_id)}get name(){const e=this._hass.devices[this.deviceId];return e?.name_by_user||e?.name||"Maico KWL"}entityId(e){return this._entityIds.get(e)}has(e){return void 0!==this.stateObj(e)}stateObj(e){const t=this._entityIds.get(e),s=t?this._hass.states[t]:void 0;return s&&!ye.has(s.state)?s:void 0}state(e){return this.stateObj(e)?.state}number(e){const t=Number(this.state(e));return void 0===this.state(e)||Number.isNaN(t)?void 0:t}isOn(e){const t=this.state(e);return void 0===t?void 0:"on"===t}attribute(e,t){return this.stateObj(e)?.attributes[t]}format(e){const t=this.stateObj(e);return t?this._hass.formatEntityState(t):void 0}present(e){return e.filter(e=>this.has(e))}}const ve="temp_air_intake",be="temp_supply_air",xe="temp_extract_air",we="temp_exhaust_air",ke="airflow_supply",Ce="airflow_exhaust",Ae="fan_speed_supply",Se="fan_speed_exhaust",Me="fan_supply_active",Ee="fan_exhaust_active",Le="summer_bypass_open",Oe="ptc_heater_active",He="heat_recovery_efficiency",Pe="heat_recovery_power",Ue="heat_recovery_energy",Ie="room_temp_source",Te="temp_room",ze="temp_room_external",Re="room_temp_bus_sent",je="humidity_exhaust",Ne="absolute_humidity_extract",Ve="humidity_bus_sent",De="air_quality_bus_sent",Be="operating_mode",Ke="ventilation_level",We="current_vent_level",Fe="boost_ventilation",qe="off_lock",Ge="season",Ze="filter_remaining_device",Je="filter_remaining_outdoor",Xe="filter_remaining_room",Ye="filter_runtime_device",Qe="filter_runtime_outdoor",et="filter_runtime_room",tt="filter_next_change",it="fault_code",st="notice_code",ot=["humidity_sensor_1","humidity_sensor_2","humidity_sensor_3","humidity_sensor_4","enocean_humidity_id0","enocean_humidity_id1","enocean_humidity_id2","enocean_humidity_id3","enocean_humidity_id4","enocean_humidity_id5","enocean_humidity_id6","enocean_humidity_id7"],nt=["co2_sensor_1","co2_sensor_2","co2_sensor_3","co2_sensor_4","enocean_co2_id0","enocean_co2_id1","enocean_co2_id2","enocean_co2_id3","enocean_co2_id4","enocean_co2_id5","enocean_co2_id6","enocean_co2_id7"],rt=["voc_sensor_1","voc_sensor_2","voc_sensor_3","voc_sensor_4","enocean_voc_id0","enocean_voc_id1","enocean_voc_id2","enocean_voc_id3","enocean_voc_id4","enocean_voc_id5","enocean_voc_id6","enocean_voc_id7"];const at={en:{card_name:"Maico KWL",card_description:"Airflow, temperatures and controls of a Maico ventilation unit.",no_device:"No Maico KWL unit found.",device_missing:"The selected unit no longer exists.",editor_device:"Unit",group_airflow:"Airflow",group_room:"Room",group_controls:"Controls",group_filters:"Filters",group_status:"Status",outdoor_air:"Outdoor air",supply_air:"Supply air",extract_air:"Extract air",exhaust_air:"Exhaust air",bypass_open:"Bypass open",bypass_closed:"Bypass closed",heat_recovery:"Heat recovery",fan_off:"off",ptc_heater:"PTC heater",tile_room:"Room",tile_humidity:"Humidity",tile_air_quality:"Air quality",tile_heat_recovery:"Heat recovery",bus_badge:"BUS",from_source:"from {name}",bus_stale:"no value for {minutes} min",bus_never:"no value sent yet",sub_extract_air:"extract air",sub_external_sensor:"external sensor",air_good:"good",air_moderate:"moderate",air_poor:"poor",absolute_humidity_extract:"Absolute humidity of the extract air",energy_today:"{value} today",ventilation_level:"Ventilation level",operating_mode:"Operating mode",boost:"Boost",level_off:"Off",level_humidity_protection:"Humidity",level_reduced:"Reduced",level_nominal:"Nominal",level_intensive:"Intensive",level_auto_hint:"Level is chosen by {mode}",filter_device:"Device filter",filter_outdoor:"Outdoor filter",filter_room:"Room filter",filter_days:"{days} days",filter_due:"due",filter_next_change:"Next change on {date}",notices_one:"1 notice",notices_many:"{count} notices",faults_one:"Fault",faults_many:"{count} faults"},de:{card_name:"Maico KWL",card_description:"Luftströme, Temperaturen und Bedienung eines Maico-Lüftungsgeräts.",no_device:"Kein Maico-KWL-Gerät gefunden.",device_missing:"Das gewählte Gerät gibt es nicht mehr.",editor_device:"Gerät",group_airflow:"Luftstrom",group_room:"Raum",group_controls:"Bedienung",group_filters:"Filter",group_status:"Status",outdoor_air:"Außenluft",supply_air:"Zuluft",extract_air:"Abluft",exhaust_air:"Fortluft",bypass_open:"Bypass offen",bypass_closed:"Bypass zu",heat_recovery:"Rückgewinnung",fan_off:"aus",ptc_heater:"PTC-Heizregister",tile_room:"Raum",tile_humidity:"Feuchte",tile_air_quality:"Luftgüte",tile_heat_recovery:"Rückgewinnung",bus_badge:"BUS",from_source:"von {name}",bus_stale:"seit {minutes} min kein Wert",bus_never:"noch kein Wert gesendet",sub_extract_air:"Abluft",sub_external_sensor:"externer Fühler",air_good:"gut",air_moderate:"mäßig",air_poor:"schlecht",absolute_humidity_extract:"Absolute Feuchte Abluft",energy_today:"heute {value}",ventilation_level:"Lüftungsstufe",operating_mode:"Betriebsart",boost:"Stoßlüftung",level_off:"Aus",level_humidity_protection:"Feuchte",level_reduced:"Reduziert",level_nominal:"Nenn",level_intensive:"Intensiv",level_auto_hint:"Stufe wird von {mode} gewählt",filter_device:"Gerätefilter",filter_outdoor:"Außenluftfilter",filter_room:"Raumfilter",filter_days:"{days} Tage",filter_due:"fällig",filter_next_change:"Nächster Wechsel am {date}",notices_one:"1 Hinweis",notices_many:"{count} Hinweise",faults_one:"Störung",faults_many:"{count} Störungen"}};function lt(e,t,s={}){const o=(e?.locale?.language??e?.language??"en").split("-")[0];return(o in at?at[o]:at.en)[t].replace(/\{(\w+)\}/g,(e,t)=>t in s?String(s[t]):e)}function ct(e){const t=navigator.language.split("-")[0];return(t in at?at[t]:at.en)[e]}const dt=["off","humidity_protection","reduced","nominal","intensive"],ht={off:"M12.5,2C9.64,2 8.57,4.55 9.29,7.47L15,13.16C15.87,13.37 16.81,13.81 17.28,14.73C18.46,17.1 22.03,17 22.03,12.5C22.03,8.92 18.05,8.13 14.35,10.13C14.03,9.73 13.61,9.42 13.13,9.22C13.32,8.29 13.76,7.24 14.75,6.75C17.11,5.57 17,2 12.5,2M3.28,4L2,5.27L4.47,7.73C3.22,7.74 2,8.87 2,11.5C2,15.07 5.96,15.85 9.65,13.87C9.97,14.27 10.4,14.59 10.89,14.79C10.69,15.71 10.25,16.75 9.27,17.24C6.91,18.42 7,22 11.5,22C13.8,22 14.94,20.36 14.94,18.21L18.73,22L20,20.72L3.28,4Z",humidity_protection:"M12,3.25C12,3.25 6,10 6,14C6,17.32 8.69,20 12,20A6,6 0 0,0 18,14C18,10 12,3.25 12,3.25M14.47,9.97L15.53,11.03L9.53,17.03L8.47,15.97M9.75,10A1.25,1.25 0 0,1 11,11.25A1.25,1.25 0 0,1 9.75,12.5A1.25,1.25 0 0,1 8.5,11.25A1.25,1.25 0 0,1 9.75,10M14.25,14.5A1.25,1.25 0 0,1 15.5,15.75A1.25,1.25 0 0,1 14.25,17A1.25,1.25 0 0,1 13,15.75A1.25,1.25 0 0,1 14.25,14.5Z",reduced:"M13 19C13 17.59 13.5 16.3 14.3 15.28C14.17 14.97 14.03 14.65 13.86 14.34C14.26 14 14.57 13.59 14.77 13.11C15.26 13.21 15.78 13.39 16.25 13.67C17.07 13.25 18 13 19 13C20.05 13 21.03 13.27 21.89 13.74C21.95 13.37 22 12.96 22 12.5C22 8.92 18.03 8.13 14.33 10.13C14 9.73 13.59 9.42 13.11 9.22C13.3 8.29 13.74 7.24 14.73 6.75C17.09 5.57 17 2 12.5 2C8.93 2 8.14 5.96 10.13 9.65C9.72 9.97 9.4 10.39 9.21 10.87C8.28 10.68 7.23 10.25 6.73 9.26C5.56 6.89 2 7 2 11.5C2 15.07 5.95 15.85 9.64 13.87C9.96 14.27 10.39 14.59 10.88 14.79C10.68 15.71 10.24 16.75 9.26 17.24C6.9 18.42 7 22 11.5 22C12.31 22 13 21.78 13.5 21.41C13.19 20.67 13 19.86 13 19M12 13C11.43 13 11 12.55 11 12S11.43 11 12 11C12.54 11 13 11.45 13 12S12.54 13 12 13M17 15V17H18V23H20V15H17Z",nominal:"M13 19C13 17.59 13.5 16.3 14.3 15.28C14.17 14.97 14.03 14.65 13.86 14.34C14.26 14 14.57 13.59 14.77 13.11C15.26 13.21 15.78 13.39 16.25 13.67C17.07 13.25 18 13 19 13C20.05 13 21.03 13.27 21.89 13.74C21.95 13.37 22 12.96 22 12.5C22 8.92 18.03 8.13 14.33 10.13C14 9.73 13.59 9.42 13.11 9.22C13.3 8.29 13.74 7.24 14.73 6.75C17.09 5.57 17 2 12.5 2C8.93 2 8.14 5.96 10.13 9.65C9.72 9.97 9.4 10.39 9.21 10.87C8.28 10.68 7.23 10.25 6.73 9.26C5.56 6.89 2 7 2 11.5C2 15.07 5.95 15.85 9.64 13.87C9.96 14.27 10.39 14.59 10.88 14.79C10.68 15.71 10.24 16.75 9.26 17.24C6.9 18.42 7 22 11.5 22C12.31 22 13 21.78 13.5 21.41C13.19 20.67 13 19.86 13 19M12 13C11.43 13 11 12.55 11 12S11.43 11 12 11C12.54 11 13 11.45 13 12S12.54 13 12 13M16 15V17H19V18H18C16.9 18 16 18.9 16 20V23H21V21H18V20H19C20.11 20 21 19.11 21 18V17C21 15.9 20.11 15 19 15H16Z",intensive:"M13 19C13 17.59 13.5 16.3 14.3 15.28C14.17 14.97 14.03 14.65 13.86 14.34C14.26 14 14.57 13.59 14.77 13.11C15.26 13.21 15.78 13.39 16.25 13.67C17.07 13.25 18 13 19 13C20.05 13 21.03 13.27 21.89 13.74C21.95 13.37 22 12.96 22 12.5C22 8.92 18.03 8.13 14.33 10.13C14 9.73 13.59 9.42 13.11 9.22C13.3 8.29 13.74 7.24 14.73 6.75C17.09 5.57 17 2 12.5 2C8.93 2 8.14 5.96 10.13 9.65C9.72 9.97 9.4 10.39 9.21 10.87C8.28 10.68 7.23 10.25 6.73 9.26C5.56 6.89 2 7 2 11.5C2 15.07 5.95 15.85 9.64 13.87C9.96 14.27 10.39 14.59 10.88 14.79C10.68 15.71 10.24 16.75 9.26 17.24C6.9 18.42 7 22 11.5 22C12.31 22 13 21.78 13.5 21.41C13.19 20.67 13 19.86 13 19M12 13C11.43 13 11 12.55 11 12S11.43 11 12 11C12.54 11 13 11.45 13 12S12.54 13 12 13M21 21V20.5C21 19.67 20.33 19 19.5 19C20.33 19 21 18.33 21 17.5V17C21 15.89 20.1 15 19 15H16V17H19V18H17V20H19V21H16V23H19C20.11 23 21 22.11 21 21"},ut=new Set(["auto_time","auto_sensor"]),pt=[["filter_device",Ze,Ye],["filter_outdoor",Je,Qe],["filter_room",Xe,et]],ft={level:e=>e.state(We)??e.state(Ke),mode:e=>e.state(Be),boost:e=>e.state(Fe)};function _t(e,t,s,o){const r=e.device.entityId(s);r&&e.change(t,o,()=>e.hass.callService("select","select_option",{entity_id:r,option:o}))}function gt(e){const{hass:t,device:s}=e,o=(e,s)=>lt(t,e,s);if(!s.stateObj(Ke))return oe;const r=e.shown("mode"),a=void 0!==r&&ut.has(r),l=e.shown("level"),c=e.pending("level"),d=s.isOn(qe)??!1,h=s.stateObj(Be);return te`
    <div class="control">
      <div class="control-label" id="kwl-level-label">${o("ventilation_level")}</div>
      <div class=${a?"segments locked":"segments"} role="group" aria-labelledby="kwl-level-label">
        ${dt.map(t=>{const s=t===l,r=a||"off"===t&&d;return te`<button
            type="button"
            class=${s?c?"segment active pending":"segment active":"segment"}
            aria-pressed=${s?"true":"false"}
            aria-label=${o(`level_${t}`)}
            title=${o(`level_${t}`)}
            ?disabled=${r}
            @click=${()=>_t(e,"level",Ke,t)}
          >
            ${e.narrow?te`<svg class="level-icon" viewBox="0 0 24 24" aria-hidden="true">
                  ${ie`<path d=${ht[t]}></path>`}
                </svg>`:o(`level_${t}`)}
          </button>`})}
      </div>
      ${function(e,t,s){const o=(t,s)=>lt(e.hass,t,s),r=[e.narrow&&t&&dt.includes(t)?o(`level_${t}`):void 0,s?o("level_auto_hint",{mode:s}):void 0].filter(Boolean);return r.length?te`<div class="hint">${r.join(" · ")}</div>`:oe}(e,l,a&&h?t.formatEntityState(h,r):void 0)}
    </div>
  `}function mt(e){const{hass:t,device:s}=e,o=(e,s)=>lt(t,e,s),r=pt.filter(([,e])=>void 0!==s.number(e));if(!r.length)return oe;const a=function(e,t){const s=t?.match(/^(\d{4})-(\d{2})-(\d{2})$/);if(!s)return;const[o,r,a]=s.slice(1).map(Number),l=e.locale?.language??e.language??"en";return new Intl.DateTimeFormat(l,{day:"2-digit",month:"2-digit",year:"numeric"}).format(new Date(o,r-1,a))}(t,s.state(tt))??s.format(tt);return te`
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
  `}function yt(e){return te`${gt(e)}${function(e){const{hass:t,device:s}=e,o=e=>lt(t,e),r=s.stateObj(Be),a=s.has(Fe)?s.entityId(Fe):void 0,l=s.stateObj(Ge);if(!r&&!a&&!l)return oe;const c=r?.attributes.options??[],d=e.shown("mode"),h="on"===e.shown("boost"),u=["button",h?"active":"",e.pending("boost")?"pending":""].join(" "),p=t=>e.narrow?oe:te`<span>${t}</span>`;return te`
    <div class="mode-row">
      ${r?te`<label class="control mode">
            <span class="control-label">${o("operating_mode")}</span>
            <span class="select">
              <select
                class=${e.pending("mode")?"pending":""}
                .value=${d??""}
                @change=${t=>_t(e,"mode",Be,t.target.value)}
              >
                ${c.map(e=>te`<option value=${e} ?selected=${e===d}>
                    ${t.formatEntityState(r,e)}
                  </option>`)}
              </select>
              <svg class="chevron" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M7 10l5 5 5-5"></path>
              </svg>
            </span>
          </label>`:oe}
      ${a?te`<button
            type="button"
            class=${u}
            aria-pressed=${h?"true":"false"}
            aria-label=${o("boost")}
            title=${o("boost")}
            @click=${()=>e.change("boost",h?"off":"on",()=>t.callService("switch",h?"turn_off":"turn_on",{entity_id:a}))}
          >
            <svg viewBox="0 0 18 18" aria-hidden="true" class="stroke-icon">
              <path d="M2 6 H11 A2.5 2.5 0 1 0 8.5 3.5"></path>
              <path d="M2 10 H14 A2.5 2.5 0 1 1 11.5 12.5"></path>
              <path d="M2 14 H7"></path>
            </svg>
            ${p(o("boost"))}
          </button>`:oe}
      ${!l||"summer"!==l.state&&"winter"!==l.state?oe:te`<button
            type="button"
            class="button"
            aria-label=${t.formatEntityState(l)}
            title=${t.formatEntityState(l)}
            @click=${()=>e.moreInfo(Ge)}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true" class="fill-icon">
              ${ie`<path d=${"summer"===l.state?"M3.55 19.09L4.96 20.5L6.76 18.71L5.34 17.29M12 6C8.69 6 6 8.69 6 12S8.69 18 12 18 18 15.31 18 12C18 8.68 15.31 6 12 6M20 13H23V11H20M17.24 18.71L19.04 20.5L20.45 19.09L18.66 17.29M20.45 5L19.04 3.6L17.24 5.39L18.66 6.81M13 1H11V4H13M6.76 5.39L4.96 3.6L3.55 5L5.34 6.81L6.76 5.39M1 13H4V11H1M13 20H11V23H13":"M20.79,13.95L18.46,14.57L16.46,13.44V10.56L18.46,9.43L20.79,10.05L21.31,8.12L19.54,7.65L20,5.88L18.07,5.36L17.45,7.69L15.45,8.82L13,7.38V5.12L14.71,3.41L13.29,2L12,3.29L10.71,2L9.29,3.41L11,5.12V7.38L8.5,8.82L6.5,7.69L5.92,5.36L4,5.88L4.47,7.65L2.7,8.12L3.22,10.05L5.55,9.43L7.55,10.56V13.45L5.55,14.58L3.22,13.96L2.7,15.89L4.47,16.36L4,18.12L5.93,18.64L6.55,16.31L8.55,15.18L11,16.62V18.88L9.29,20.59L10.71,22L12,20.71L13.29,22L14.7,20.59L13,18.88V16.62L15.5,15.17L17.5,16.3L18.12,18.63L20,18.12L19.53,16.35L21.3,15.88L20.79,13.95M9.5,10.56L12,9.11L14.5,10.56V13.44L12,14.89L9.5,13.44V10.56Z"}></path>`}
            </svg>
            ${p(t.formatEntityState(l))}
          </button>`}
    </div>
  `}(e)}${mt(e)}`}const $t=l`
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
`,vt=new Set(["bypass_active"]);function bt(e,t){const s=e.attribute(t,"active");return Array.isArray(s)?s.filter(e=>"string"==typeof e):[]}function xt(e){const{hass:t,device:s}=e,o=function(e,t){const s=[];for(const[o,r]of[["fault",it],["notice",st]]){const a=t.stateObj(r);if(a)for(const l of bt(t,r))"notice"===o&&vt.has(l)||s.push({kind:o,text:e.formatEntityAttributeValue(a,"active",l)})}return s}(t,s),r=o.filter(e=>"fault"===e.kind).length,a=o.length-r,l=r?1===r?lt(t,"faults_one"):lt(t,"faults_many",{count:r}):1===a?lt(t,"notices_one"):lt(t,"notices_many",{count:a});return te`
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
                @click=${()=>e.moreInfo("fault"===t.kind?it:st)}
              >
                ${t.text}
              </button>
            </li>`)}
        </ul>`:oe}
  `}const wt=l`
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
`,kt=[[-10,"#0d47a1"],[0,"#1976d2"],[10,"#64b5f6"],[20,"#b8b8b8"],[25,"#ffb74d"],[30,"#f57c00"],[35,"#d32f2f"]],Ct=[[-10,"#1e88e5"],[0,"#42a5f5"],[10,"#90caf9"],[20,"#a8a8a8"],[25,"#ffb74d"],[30,"#ff9800"],[35,"#ef5350"]];function At(e,t){const s=t?Ct:kt;if(void 0===e)return function(e){return(e?Ct:kt)[3][1]}(t);if(e<=s[0][0])return s[0][1];for(let t=1;t<s.length;t++){const[o,r]=s[t],[a,l]=s[t-1];if(e<=o){return`color-mix(in oklab, ${r} ${Math.round((e-a)/(o-a)*100)}%, ${l})`}}return s[s.length-1][1]}function St(e,t,s,o=5){return void 0===e||void 0===t?Array.from({length:o},(r,a)=>At(a<o/2?e??t:t??e,s)):Array.from({length:o},(r,a)=>At(e+(t-e)*a/(o-1),s))}const Mt=62,Et=142,Lt=160,Ot=260,Ht="M96 62 C 128 62, 128 22, 162 22 L 258 22 C 292 22, 292 62, 324 62";const Pt=l`
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
`;function Ut(e,t){const s=e.states[t]?.attributes.friendly_name;return"string"==typeof s?s:t}function It(e,t,s,o,r,a){const l=t.format(r),c=t.attribute(r,"source_entity");if(void 0===l||!c)return;const d=t.attribute(r,"last_written"),h=d?Math.floor((a-Date.parse(d))/6e4):void 0,u=void 0===h||h>=10;return{label:o,key:r,moreInfo:c,value:l,sub:void 0===h?s("bus_never"):u?s("bus_stale",{minutes:h}):s("from_source",{name:Ut(e,c)}),bus:{stale:u}}}function Tt(e,t,s,o){const r=t.present(o).filter(e=>void 0!==t.number(e));if(!r.length)return;const a=r.reduce((e,s)=>t.number(s)>t.number(e)?s:e),l=t.entityId(a);return{label:s,key:a,moreInfo:l,value:t.format(a),sub:r.length>1?Ut(e,l):void 0}}function zt(e,t,s,o){const r=e.format(s);return void 0===r?void 0:{label:t,key:s,moreInfo:e.entityId(s),value:r,sub:o}}function Rt(e,t,s,o){switch(t.state(Ie)){case"bus":return It(e,t,s,"tile_room",Re,o)??zt(t,"tile_room",Te);case"external":return zt(t,"tile_room",ze,s("sub_external_sensor"))??zt(t,"tile_room",Te);default:return zt(t,"tile_room",Te)}}function jt(e,t,s,o){const r=It(e,t,s,"tile_humidity",Ve,o)??Tt(e,t,"tile_humidity",ot)??zt(t,"tile_humidity",je,s("sub_extract_air")),a=t.format(Ne);return r&&a&&(r.extra={value:a,title:s("absolute_humidity_extract")}),r}function Nt(e,t,s,o){const r=Tt(e,t,"tile_air_quality",nt)??Tt(e,t,"tile_air_quality",rt)??It(e,t,s,"tile_air_quality",De,o);if(!r)return;const a=t.number(r.key);return void 0!==a&&(r.air=a<=800?"good":a<=1400?"moderate":"poor"),r}function Vt(e,t,s,o){const r=zt(t,"tile_heat_recovery",Pe);if(r&&void 0!==o){const t=e.locale?.language??e.language??"en",a=new Intl.NumberFormat(t,{maximumFractionDigits:o<10?2:1}).format(o);r.sub=s("energy_today",{value:`${a} kWh`})}return r}const Dt=l`
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
`,Bt="maico-kwl-card";class MaicoKwlCard extends i{constructor(){super(...arguments),this._uid=`kwl${Math.random().toString(36).slice(2,10)}`,this._pending=new Map,this._messagesExpanded=!1,this._width=0,this._energyFetchedAt=0}setConfig(e){this._config=e}getCardSize(){return 6}static async getConfigElement(){const{EDITOR_TYPE:e}=await(import("./editor-BMOPF8-E.js"));return document.createElement(e)}static getStubConfig(e){const[t]=$e(e);return t?{device_id:t}:{}}connectedCallback(){super.connectedCallback(),this._resizeObserver??=new ResizeObserver(([e])=>{this._width=Math.round(e.contentRect.width)}),this._resizeObserver.observe(this)}disconnectedCallback(){super.disconnectedCallback(),this._resizeObserver?.disconnect();for(const e of[...this._pending.keys()])this._clearPending(e)}willUpdate(e){if(!e.has("hass")||!this._pending.size||!this.hass)return;const t=this._device();if(t)for(const[e,s]of this._pending)ft[e](t)===s.value&&this._clearPending(e)}updated(e){super.updated(e),e.has("hass")&&Date.now()-this._energyFetchedAt>3e5&&this._fetchEnergyToday()}async _fetchEnergyToday(){const e=this.hass&&this._device(),t=e?.entityId(Ue);if(t){this._energyFetchedAt=Date.now();try{const e=await this.hass.callWS({type:"recorder/statistic_during_period",statistic_id:t,calendar:{period:"day"},types:["change"]});this._energyToday="number"==typeof e.change?Math.max(0,e.change):void 0}catch{this._energyToday=void 0}}}_clearPending(e){const t=this._pending.get(e);t&&(window.clearTimeout(t.timer),this._pending.delete(e),this._pending=new Map(this._pending))}_controls(e){return{hass:this.hass,device:e,narrow:this._width>0&&this._width<400,moreInfo:t=>this._moreInfo(e.entityId(t)),shown:t=>this._pending.get(t)?.value??ft[t](e),pending:e=>this._pending.has(e),change:(t,s,o)=>{if(this._clearPending(t),ft[t](e)===s)return void o();const r=window.setTimeout(()=>this._clearPending(t),35e3);this._pending=new Map(this._pending).set(t,{value:s,timer:r}),o().catch(()=>this._clearPending(t))}}}_device(){const e=this._config?.device_id??$e(this.hass)[0];if(e&&this.hass.devices[e])return new KwlDevice(this.hass,e)}render(){if(!this.hass||!this._config)return oe;const e=this._device();if(!e){const e=this._config.device_id?"device_missing":"no_device";return te`<ha-card><p class="empty">${lt(this.hass,e)}</p></ha-card>`}return te`
      <ha-card class=${this.hass.themes?.darkMode?"dark":""}>
        ${xt({hass:this.hass,device:e,expanded:this._messagesExpanded,toggle:()=>this._messagesExpanded=!this._messagesExpanded,moreInfo:t=>this._moreInfo(e.entityId(t))})}
        <div class="content">
          ${function(e){const{hass:t,device:s,uid:o}=e,r=Math.max(1,e.scale),a=Math.max(12,11*r),l=Math.max(20,17*r),c=Math.max(12,11.5*r),d=Math.max(11,10.5*r),h=Math.max(18,15*r),u=r>1.15,p=Math.max(4,3.2*r),f=176+Math.max(18,1.25*a),_=t.themes?.darkMode??!1,g=e=>lt(t,e),m=s.number(ve),$=s.number(be),v=s.number(xe),b=s.number(we),x=s.has(Le),w=s.isOn(Le)??!1,C=s.isOn(Me)??(s.number(ke)??0)>0,A=s.isOn(Ee)??(s.number(Ce)??0)>0,M=St(m,$,_),E=St(b,v,_),O=At(m,_),P=At($,_),U=At(b,_),T=At(v,_),j=w?"M20 62 L96 62 M324 62 L392 62":"M20 62 L392 62",N="M400 142 L28 142",V=e=>`${Math.min(12,Math.max(2,810/Math.max(e??180,1))).toFixed(2)}s`,D=(t,o,r)=>s.entityId(t)?ie`<g class="clickable" role="button" tabindex="0" aria-label=${r}
          @click=${()=>e.moreInfo(t)}
          @keydown=${s=>{"Enter"!==s.key&&" "!==s.key||(s.preventDefault(),e.moreInfo(t))}}>${o}</g>`:o,B=(e,t,o,r,c,d,h)=>{if(void 0===o)return oe;const u=s.format(e),f="left"===c;return D(e,ie`
        <text class="name" x=${f?20:400} y=${d} text-anchor=${f?"start":"end"}
          style=${`font-size: ${a}px`}>${t}</text>
        <circle cx=${f?20+p:400-p} cy=${h-.35*l} r=${p}
          style=${`fill: ${r}`}></circle>
        <text class="value" x=${f?26+2*p:394-2*p} y=${h}
          text-anchor=${f?"start":"end"} style=${`font-size: ${l}px`}>${u}</text>
      `,`${t} ${u}`)},K=(e,t,o,r,l,d)=>{const h=1.2*a,u=s.number(r),p=u&&u>0?`${(4e3/u).toFixed(2)}s`:"2s",f=o?s.format(r):g("fan_off"),_=o?s.format(l):void 0;return D(r,ie`
        <circle class="fan-housing" cx=${e} cy=${t} r="13"></circle>
        <g class=${o?"rotor spinning":"rotor"} style=${`animation-duration: ${p}`}>
          <circle cx=${e} cy=${t} r="13" fill="none" stroke="none"></circle>
          ${[0,120,240].map(s=>ie`<ellipse cx=${e} cy=${t-6} rx="3" ry="5.5" transform=${`rotate(${s} ${e} ${t})`}></ellipse>`)}
        </g>
        ${f?ie`<text class="fan-speed" x=${e} y=${d-h} text-anchor="middle"
              style=${`font-size: ${c}px`}>${f}</text>`:oe}
        ${_?ie`<text class="small" x=${e} y=${d} text-anchor="middle"
              style=${`font-size: ${a}px`}>${_}</text>`:oe}
      `,`${f??""} ${_??""}`)},W=s.format(He);return te`
    <svg class="schematic" viewBox="0 -14 420 214" role="img"
      aria-label=${[g("outdoor_air"),g("supply_air"),g("extract_air"),g("exhaust_air")].join(", ")}>
      <defs>
        <linearGradient id=${`${o}-top`} gradientUnits="userSpaceOnUse" x1=${Lt} y1="0" x2=${Ot} y2="0">
          ${M.map((e,t)=>ie`<stop offset=${t/(M.length-1)} style=${`stop-color: ${e}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${o}-bottom`} gradientUnits="userSpaceOnUse" x1=${Lt} y1="0" x2=${Ot} y2="0">
          ${E.map((e,t)=>ie`<stop offset=${t/(E.length-1)} style=${`stop-color: ${e}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${o}-sheen`}>
          <stop offset="0" stop-color="#000"></stop>
          <stop offset="0.5" stop-color="#fff"></stop>
          <stop offset="1" stop-color="#000"></stop>
        </linearGradient>
        <mask id=${`${o}-sheen-right`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen" x="-140" y="-14" width="140" height="214" fill=${`url(#${o}-sheen)`}
            style=${`animation-duration: ${V(s.number(ke))}`}></rect>
        </mask>
        <mask id=${`${o}-sheen-left`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen reverse" x="-140" y="-14" width="140" height="214" fill=${`url(#${o}-sheen)`}
            style=${`animation-duration: ${V(s.number(Ce))}`}></rect>
        </mask>
      </defs>

      <rect class="exchanger" x=${Lt} y="34" width=${100} height="136" rx="12"></rect>
      <line class="exchanger-line" x1=${Lt} y1="34" x2=${Ot} y2="170"></line>
      <line class="exchanger-line" x1=${Ot} y1="34" x2=${Lt} y2="170"></line>

      ${x?D(Le,ie`
              <path class=${w?"tube":"bypass-closed"} d=${Ht}
                style=${w?`stroke: ${O}`:""}></path>
              <text class=${w?"bypass-label open":"bypass-label"} x="210" y="6" text-anchor="middle"
                style=${`font-size: ${d}px`}>
                ${g(w?"bypass_open":"bypass_closed")}
              </text>`,g(w?"bypass_open":"bypass_closed")):oe}

      <path class="tube" d=${j} stroke=${`url(#${o}-top)`}></path>
      ${w?ie`<path class="passage" d=${"M96 62 L324 62"}></path>`:oe}
      <path class="tube" d=${N} stroke=${`url(#${o}-bottom)`}></path>
      <polygon points="396,57 406,62 396,67" style=${`fill: ${P}`}></polygon>
      <polygon points="24,137 14,142 24,147" style=${`fill: ${U}`}></polygon>

      ${C?ie`<g class="sheen-layer" mask=${`url(#${o}-sheen-right)`}>
            <path class="tube-sheen" d=${j} stroke=${`url(#${o}-top)`}></path>
            ${w?ie`<path class="tube-sheen" d=${Ht} style=${`stroke: ${O}`}></path>`:oe}
          </g>`:oe}
      ${A?ie`<g class="sheen-layer" mask=${`url(#${o}-sheen-left)`}>
            <path class="tube-sheen" d=${N} stroke=${`url(#${o}-bottom)`}></path>
          </g>`:oe}

      ${(()=>{if(!s.has(Oe))return oe;const e=s.isOn(Oe)??!1;return D(Oe,ie`<g class=${e?"ptc active":"ptc"}>
        <rect x=${47} y=${53} width="22" height="18" rx="4"></rect>
        <path d=${"M51 62 l3 -4 l4 8 l4 -8 l3 4"}></path>
      </g>`,g("ptc_heater"))})()}

      ${W?D(He,ie`
              <rect class="exchanger" x="166" y="80" width="88" height="44" rx="8" stroke="none"></rect>
              ${u?ie`<text class="value" x="210" y=${102+.35*h} text-anchor="middle"
                    style=${`font-size: ${h}px`}>${W}</text>`:ie`<text class="value" x="210" y="102" text-anchor="middle"
                      style=${`font-size: ${h}px`}>${W}</text>
                    <text class="small" x="210" y="117" text-anchor="middle"
                      style=${`font-size: ${a}px`}>${g("heat_recovery")}</text>`}`,`${g("heat_recovery")} ${W}`):oe}

      ${K(340,Mt,C,Ae,ke,79+c+1.2*a)}
      ${K(80,Et,A,Se,Ce,120)}

      ${B(ve,g("outdoor_air"),m,O,"left",18,42)}
      ${B(be,g("supply_air"),$,P,"right",18,42)}
      ${B(xe,g("extract_air"),v,T,"right",f,176)}
      ${B(we,g("exhaust_air"),b,U,"left",f,176)}
    </svg>
  `}({hass:this.hass,device:e,uid:this._uid,scale:this._width?420/Math.min(460,this._width-32):1,moreInfo:t=>this._moreInfo(e.entityId(t))})}
          ${function(e,t,s){if(!t.length)return oe;const o=t=>lt(e,t);return te`
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
              ${e.extra?te`<span class="tile-extra" title=${e.extra.title}>${e.extra.value}</span>`:oe}
            </span>
            ${e.sub?te`<span class=${e.bus?.stale?"tile-sub stale":"tile-sub"}>
                  ${e.subIcon?te`<svg class="sub-icon" viewBox="0 0 24 24" aria-hidden="true">
                        ${ie`<path d=${e.subIcon}></path>`}
                      </svg>`:oe}${e.sub}
                </span>`:oe}
          </button>
        `)}
    </div>
  `}(this.hass,function(e,t,s,o=Date.now()){const r=(t,s)=>lt(e,t,s);return[Rt(e,t,r,o),jt(e,t,r,o),Nt(e,t,r,o),Vt(e,t,r,s)].filter(e=>void 0!==e)}(this.hass,e,this._energyToday),e=>this._moreInfo(e))}
          ${yt(this._controls(e))}
        </div>
      </ha-card>
    `}_moreInfo(e){e&&this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:e},bubbles:!0,composed:!0}))}}MaicoKwlCard.styles=[wt,Pt,Dt,$t,l`
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
  `],e([_e({attribute:!1})],MaicoKwlCard.prototype,"hass",void 0),e([ge()],MaicoKwlCard.prototype,"_config",void 0),e([ge()],MaicoKwlCard.prototype,"_pending",void 0),e([ge()],MaicoKwlCard.prototype,"_messagesExpanded",void 0),e([ge()],MaicoKwlCard.prototype,"_width",void 0),e([ge()],MaicoKwlCard.prototype,"_energyToday",void 0),customElements.get(Bt)||(customElements.define(Bt,MaicoKwlCard),window.customCards=window.customCards??[],window.customCards.push({type:Bt,name:ct("card_name"),description:ct("card_description"),preview:!0}));var Kt=Object.freeze({__proto__:null,MaicoKwlCard:MaicoKwlCard});export{oe as A,me as D,e as _,te as b,Kt as c,i,lt as l,_e as n,ge as r};
