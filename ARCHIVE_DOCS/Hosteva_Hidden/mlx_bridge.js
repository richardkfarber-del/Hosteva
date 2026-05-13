const http = require('http');
http.createServer((req, res) => {
  let body = [];
  req.on('data', c => body.push(c));
  req.on('end', () => {
    let parsed = {};
    try { parsed = JSON.parse(Buffer.concat(body).toString()); } catch(e) {}
    
    console.log("\n[Bridge] Intercepted payload. Flattening content for MLX...");
    
    let clean = {
      model: "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit", // <--- SHIFTED TO 7B
      messages: parsed.messages || parsed.input || [],
      stream: false
    };
    
    if (typeof clean.messages === 'string') {
      clean.messages = [{ role: 'user', content: clean.messages }];
    }
    
    if (Array.isArray(clean.messages)) {
      clean.messages = clean.messages.map(m => {
        if (m.role === 'model') m.role = 'assistant';
        
        if (Array.isArray(m.content)) {
            m.content = m.content.map(part => {
                if (typeof part === 'string') return part;
                if (part && part.text) return part.text;
                return JSON.stringify(part);
            }).join('\n');
        } else if (typeof m.content === 'object' && m.content !== null) {
            m.content = JSON.stringify(m.content);
        }
        
        return m;
      });
    }
    
    if (parsed.max_output_tokens) clean.max_tokens = parsed.max_output_tokens;
    if (parsed.tools) clean.tools = parsed.tools;
    
    const payloadOut = Buffer.from(JSON.stringify(clean));
    
    const options = {
      hostname: '192.168.4.91',
      port: 8080,
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': payloadOut.length
      }
    };
    
    const pReq = http.request(options, pRes => {
      console.log(`[Bridge] Mac Mini Status: ${pRes.statusCode}`);
      res.writeHead(pRes.statusCode, pRes.headers);
      pRes.pipe(res);
    });
    
    pReq.on('error', e => {
      res.writeHead(502); res.end();
    });
    
    pReq.write(payloadOut);
    pReq.end();
  });
}).listen(8081, () => console.log('🌉 V2 Native Bridge (7B Model) Active'));
