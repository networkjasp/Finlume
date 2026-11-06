/* Finlume website editor: sign-in page. Loads the editor (Decap CMS) only after a successful login. */
(function () {
  var KEY = "decap-cms-user", d = document;
  function saved() {
    try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; }
  }
  function expiry(u) {
    try { return JSON.parse(atob(u.token.split(".")[0].replace(/-/g, "+").replace(/_/g, "/"))).exp || 0; } catch (e) { return 0; }
  }
  function valid(u) { return u && u.backendName === "github" && u.token && expiry(u) > Date.now() + 30000; }
  function clear() { try { localStorage.removeItem(KEY); } catch (e) {} }

  function startEditor() {
    var box = d.getElementById("login");
    if (box) box.remove();
    var s = d.createElement("script");
    s.src = "/studio/decap-cms-3.17.1.js";
    d.body.appendChild(s);
    // Signed out (Log out in the editor) or session expired: back to the sign-in page.
    setInterval(function () { if (!valid(saved())) { clear(); location.replace("/studio/"); } }, 2000);
  }

  if (valid(saved())) { startEditor(); return; }
  clear();
  var form = d.getElementById("login-form"), msg = d.getElementById("login-msg"), btn = form.querySelector("button");
  d.getElementById("login").hidden = false;
  d.getElementById("u").focus();
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var u = d.getElementById("u").value.trim(), p = d.getElementById("p").value;
    if (!u || !p) { msg.textContent = "Please enter your username and password."; return; }
    btn.disabled = true; btn.textContent = "Signing in…"; msg.textContent = "";
    fetch("/api/cms/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username: u, password: p }) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { j.status = r.status; return j; }); })
      .then(function (j) {
        if (j.ok && j.token) {
          localStorage.setItem(KEY, JSON.stringify({ backendName: "github", token: j.token, name: j.name, login: j.name }));
          startEditor();
          return;
        }
        msg.textContent = j.status === 429 ? "Too many attempts. Please wait a minute and try again."
          : j.error === "not_configured" ? "The editor isn't set up yet (Netlify settings missing)."
          : j.status === 401 ? "Incorrect username or password." : "Sign-in failed. Please try again.";
        d.getElementById("p").value = "";
        btn.disabled = false; btn.textContent = "Sign in";
      })
      .catch(function () { msg.textContent = "Couldn't connect. Check your internet and try again."; btn.disabled = false; btn.textContent = "Sign in"; });
  });
})();
