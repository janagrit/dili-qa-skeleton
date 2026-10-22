// Mock of the live login flow, used only by the login-no-fixed-wait judge.
// Usage: node mock-login-server.js <good|bad-now|bad-late> <port>
// A filled submit always POSTs /auth/login (401). An empty submit sends nothing
// in `good` mode, POSTs at once in `bad-now`, and POSTs after 250ms in `bad-late`.
const http = require('http');

const [mode, port] = process.argv.slice(2);
const emptySubmit = {
  good: '',
  'bad-now': 'login();',
  'bad-late': 'setTimeout(login, 250);',
}[mode];
if (emptySubmit === undefined) throw new Error(`unknown mode: ${mode}`);

const home = `<!doctype html><title>Home</title>
<nav><a href="/login">Log In</a></nav>`;

const login = `<!doctype html><title>Sign in</title>
<h1>Sign in</h1>
<label>Email <input id="email" type="text"></label>
<label>Password <input id="password" type="password"></label>
<button type="button" id="go">Sign in</button>
<a href="#">Forgot password?</a> <a href="#">Sign in with SSO</a>
<p id="error" hidden>Invalid username or password</p>
<script>
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  async function login() {
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value }),
    });
    if (res.status === 401) document.getElementById('error').hidden = false;
  }
  document.getElementById('go').addEventListener('click', () => {
    if (email.value || password.value) login();
    else { ${emptySubmit} }
  });
</script>`;

http
  .createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/auth/login') {
      res.writeHead(401, { 'content-type': 'application/json' });
      return res.end('{"error":"invalid"}');
    }
    res.writeHead(200, { 'content-type': 'text/html' });
    res.end(req.url.startsWith('/login') ? login : home);
  })
  .listen(Number(port), '127.0.0.1');
