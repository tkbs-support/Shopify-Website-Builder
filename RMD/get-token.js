const http = require('http');
const https = require('https');
const { execSync } = require('child_process');
require('dotenv').config();

const STORE = process.env.SHOPIFY_STORE_DOMAIN;
// Falls back to the original Clothing Cove app ID if SHOPIFY_CLIENT_ID is not set
const CLIENT_ID = process.env.SHOPIFY_CLIENT_ID || '03a5e971f908d5c9964220a886417ee6';
const REDIRECT_URI = 'http://localhost:3456/callback';
const SCOPES = process.env.SHOPIFY_SCOPES || 'read_themes,write_themes,read_products,write_products,read_content,write_content,read_online_store_pages,write_online_store_pages';

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:3456`);

  if (url.pathname === '/callback') {
    const code = url.searchParams.get('code');
    if (!code) {
      res.writeHead(400);
      res.end('No code received');
      return;
    }

    const postData = JSON.stringify({
      client_id: CLIENT_ID,
      client_secret: process.env.SHOPIFY_CLIENT_SECRET,
      code: code
    });

    const tokenReq = https.request({
      hostname: STORE,
      path: '/admin/oauth/access_token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    }, (tokenRes) => {
      let data = '';
      tokenRes.on('data', chunk => data += chunk);
      tokenRes.on('end', () => {
        const parsed = JSON.parse(data);
        if (parsed.access_token) {
          console.log('\n=== SUCCESS ===');
          console.log('Access Token:', parsed.access_token);
          console.log('\nPaste this into your .env as SHOPIFY_ACCESS_TOKEN');
          res.writeHead(200, { 'Content-Type': 'text/html' });
          res.end('<h1>Success!</h1><p>Access token printed in your terminal. You can close this tab.</p>');
        } else {
          console.log('Error:', data);
          res.writeHead(400, { 'Content-Type': 'text/html' });
          res.end('<h1>Error</h1><pre>' + data + '</pre>');
        }
        server.close();
      });
    });
    tokenReq.write(postData);
    tokenReq.end();
  }
});

server.listen(3456, () => {
  const authUrl = `https://${STORE}/admin/oauth/authorize?client_id=${CLIENT_ID}&scope=${SCOPES}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;
  console.log('Opening browser for authorization...\n');
  console.log('If browser does not open, visit:\n', authUrl, '\n');
  try {
    execSync(`start "" "${authUrl}"`);
  } catch {}
});
