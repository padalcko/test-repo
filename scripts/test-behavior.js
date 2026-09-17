/* Run with JavaScriptCore jsc from the repository root. No network or dependencies. */
function assert(value, message) { if (!value) throw new Error(message); }
function element() {
  return { children: [], attrs: {}, listeners: {}, classList: { add() {}, remove() {}, toggle() {} },
    append(...children) { this.children.push(...children); },
    setAttribute(key, value) { this.attrs[key] = value; },
    addEventListener(event, callback) { this.listeners[event] = callback; },
    close() { this.closed = true; }, showModal() { this.open = true; }
  };
}
// Privacy must never load analytics before consent, including blocked storage.
for (const storageFails of [false, true]) {
  const button = element(), body = element(), head = element();
  const document = { documentElement: { lang: "en" }, head, body, createElement: element, getElementById: () => button };
  const window = {};
  const localStorage = { getItem() { if (storageFails) throw Error("blocked"); return null; }, setItem() { if (storageFails) throw Error("blocked"); } };
  new Function("document", "window", "localStorage", readFile("js/privacy.js"))(document, window, localStorage);
  assert(head.children.length === 0, "Analytics loaded before consent");
  const dialog = body.children[0], actions = dialog.children[2];
  button.listeners.click(); assert(dialog.open, "Privacy settings did not open");
  actions.children[0].listeners.click(); assert(head.children.length === 1, "Consent did not enable analytics");
  actions.children[1].listeners.click(); assert(window["ga-disable-G-1Z98BZS3WW"] === true, "Revocation did not disable analytics");
  actions.children[0].listeners.click(); assert(head.children.length === 1, "Duplicate analytics script");
}
// A slow previous image request must not overwrite the latest gallery selection.
const buttons = [element(), element(), element()];
buttons.forEach((b,i) => { b.dataset = { image: "photo" + i }; b.querySelector = () => ({ alt: "Photo " + i }); });
const link = {}, main = { src: "photo0", closest: () => link };
const gallery = { querySelector: () => main, querySelectorAll: () => buttons };
const requests = [];
function ImageMock() { requests.push(this); }
new Function("document", "Image", readFile("js/uzywane.js"))({ querySelectorAll: () => [gallery] }, ImageMock);
buttons[1].listeners.click(); buttons[2].listeners.click();
requests[1].onload(); requests[0].onload();
assert(main.src === "photo2" && link.href === "photo2", "Stale image replaced latest selection");
assert(buttons[2].attrs["aria-pressed"] === "true", "Active thumbnail not updated");
buttons[1].listeners.click(); assert(main.src === "photo2", "Unloaded image replaced working image");
// The global homepage handler must not attach to the separate contact-page form.
const form = element();
const doc = { body: element(), getElementById: id => id === "contact-form" ? form : null, querySelectorAll: () => [], addEventListener: (event, cb) => { if (event === "DOMContentLoaded") cb(); } };
const win = { location: { hash: "" }, addEventListener() {}, matchMedia: () => ({ addEventListener() {} }) };
new Function("document", "window", readFile("js/main.js"))(doc, win);
assert(!form.listeners.submit, "Global handler attached to the contact-page form");
print("PASS: consent and revocation, blocked storage, gallery race protection, failed-load fallback, independent form handlers.");
