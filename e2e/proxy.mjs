// The one origin the browser talks to, as nginx is in production: /api goes
// to the API, everything else to the Nuxt server. Without it the browser's
// same-origin /api calls would land on Nuxt and 404.
import http from 'node:http'

const PORT = Number(process.env.E2E_PORT || 3100)
const API = { host: '127.0.0.1', port: Number(process.env.E2E_API_PORT || 8100) }
const WEB = { host: '127.0.0.1', port: Number(process.env.E2E_WEB_PORT || 3101) }

http
  .createServer((req, res) => {
    const target = req.url.startsWith('/api/') || req.url === '/api' ? API : WEB
    const upstream = http.request(
      { ...target, method: req.method, path: req.url, headers: { ...req.headers, 'x-real-ip': '127.0.0.1' } },
      (answer) => {
        res.writeHead(answer.statusCode, answer.headers)
        answer.pipe(res)
      }
    )
    upstream.on('error', () => {
      res.writeHead(502)
      res.end('upstream unavailable')
    })
    req.pipe(upstream)
  })
  .listen(PORT, '127.0.0.1')
