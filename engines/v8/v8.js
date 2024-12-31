const http = require('http');

// The port the server will run on
const port = 8081;

const reply = (res, success, body) => {
    // Set the response HTTP header
    res.writeHead(success ? 200 : 400, {'Content-Type': 'application/json'});
    // Write the response content
    res.end(JSON.stringify(
        { status: success ? 'success' : 'failed', ...body }
    ));
}

// Create the server
const server = http.createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/up') {
        // Respond to /up route with JSON
        reply(res, true, { message: "Server is up and running!" })
    } else if (req.method === "POST" && req.url === "/") {
        // Set the response HTTP header
        reply(res, true, { message: "Not yet implemented!" })
    } else {
        // Handle unknown routes
        reply(res, false, { message: "URL and Method not supported" })
    }
});

// Start the server
server.listen(port, () => {
    console.log(`Server is listening on port :${port}`);
});
