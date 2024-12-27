const http = require('http');

// Create the server
const server = http.createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/up') {
        // Respond to /up route with JSON
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 200, message: "Server is up and running!" }));
    } else {
        // Set the response HTTP header
        res.writeHead(200, {'Content-Type': 'text/plain'});
        // Write the response content
        res.end('hello world');
    }
});

// Listen on port 8081
server.listen(8081, () => {
    console.log('Server is listening on port 8081');
});
