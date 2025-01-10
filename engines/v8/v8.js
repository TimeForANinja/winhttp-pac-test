import http from 'http';
import vm from 'vm';
import { buildPredefinedFuncs, build_cmd, ValidateIP, ValidateHostname } from  './util.js';

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

// Create the server
const server = http.createServer(async (req, res) => {
    if (req.method === 'GET' && req.url === '/up') {
        // Respond to /up route with JSON
        reply(res, true, { message: "Server is up and running!" })
    } else if (req.method === "POST" && req.url === "/") {
        try {
            const body = await parseRequestBody(req);

            // Validate that the "pac_content" field exists in the request body
            if (!body.pac || !body.pac.content) {
                reply(res, false, { message: "Request body must contain a 'pac.content' field." })
                return;
            }

            // Validate that the "dest_host" field exists in the request body
            if (!body.dest_host || !ValidateHostname(body.dest_host)) {
                reply(res, false, { message: "Request body must contain a 'dest_host' field, which is a valid hostname." })
                return;
            }

            // Validate that the "src_ip" field exists in the request body
            if (!body.src_ip || !ValidateIP(body.src_ip)) {
                reply(res, false, { message: "Request body must contain a 'src_ip' field, which is a valid IP address." })
                return;
            }

            const results = evalPac(body.pac.content, body.dest_host, body.src_ip);

            // Respond with the results as JSON
            reply(res, true, results)
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

const evalPac = (pacContent, testHost, src_ip) => {
    try {
        const predefinedFuncs = buildPredefinedFuncs(src_ip);
        let ctx = vm.createContext(Object.assign({}, predefinedFuncs));
        vm.runInContext(pacContent, ctx);
        if (typeof ctx.FindProxyForURL !== 'function') {
            throw new Error('FindProxyForURL is not defined');
        }

        vm.runInContext(build_cmd(testHost), ctx);

        // post-process returned proxy
        let proxy = []
        if (ctx.test && typeof ctx.test === 'string') {
            const parts = ctx.test.split(';');
            for (const part of parts) {
                if (part === "DIRECT") {
                    proxy.push("DIRECT");
                } else if (part.startsWith('PROXY ')) {
                    proxy.push(part.substr(6));
                } else if (part === "") {
                    // do nothing / skip
                } else{
                    return proxy.push(part);
                }
            }
        } else {
            proxy.push('<no proxy>');
        }

        return { status: 'success', proxy: proxy.join(';') };
    } catch (err) {
        return { status: 'failed', message: err.message };
    }
}
