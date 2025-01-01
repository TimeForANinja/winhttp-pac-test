import { ESLint } from "eslint";
import http from "http";

// The port the server will run on
const port = 8083;

const eslint = new ESLint({
    overrideConfigFile: "eslint.config.js",
});

const reply = (res, success, body) => {
    // Set the response HTTP header
    res.writeHead(success ? 200 : 400, {'Content-Type': 'application/json'});
    // Write the response content
    res.end(JSON.stringify(
        { status: success ? 'success' : 'failed', ...body }
    ));
}

// Helper function to parse the body for POST requests
const parseRequestBody = (req) => {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk.toString();
    });
    req.on("end", () => {
      try {
        resolve(JSON.parse(body));
      } catch (err) {
        reject(err);
      }
    });
  });
};

// Create the server using native Node.js
const server = http.createServer(async (req, res) => {
    if (req.method === "GET" && req.url === "/up") {
        // Respond to /up route with JSON
        reply(res, true, { message: "Server is up and running!" })
    } else if (req.method === "POST" && req.url === "/") {
        try {
            const body = await parseRequestBody(req);

            // Validate that the "pac_content" field exists in the request body
            if (!body.pac_content) {
                reply(res, false, { message: "Request body must contain a 'pac_content' field." })
                return;
            }

            const results = await eslint.lintText(body.pac_content);
            const formatted = results[0].messages.filter(x => x.severity >= 2).map(m => `${m.line}:${m.column} ${m.message} (${m.ruleId})`);

            // Respond with the results as JSON
            if (formatted.length > 0) {
                reply(res, false, { messages: formatted })
            } else {
                reply(res, true, { messages: "No Problems Found" })
            }
        } catch (error) {
            console.error("Error processing request:", error.message);
            if (error instanceof SyntaxError) {
                reply(res, false, { message: "Invalid JSON in request body." })
            } else {
                reply(res, false, { message: "Internal Server Error" })
            }
        }
    } else {
        // Handle unknown routes
        reply(res, false, { message: "URL and Method not supported" })
    }
});

// Start the server
server.listen(port, () => {
  console.log(`Server is listening on port :${port}`);
});