# winhttp-pac-test

This project provides a rest-based tool to test PAC (Proxy Auto-Configuration) files.
It's easy to deploy using the provided Docker Image, and can be used by doing simple REST-Requests.
Follow the instructions below for setup and usage.

# Project Setup
The Project is made up multiple modular Webservers, split into two main components.
1. Core Server  
This Server, located in the `/core`-Folder, is the Main Entrypoint for the End-User.  
It hosts an api (and swagger docs) for running tests on PAC Files.
2. Engines  
The Engines, various subfolders in the `/engines` Directory, are individual Web-Servers that do a single evaluation on the PAC.
This includes Engines like the `v8` as a std javascript engine or `winhttp` to test the microsoft stack.

All other Files are for supportive Roles, e.g. the `entrypoint.sh` and `healthcheck.sh` are art of the Docker build.

# Setting up with Docker

The easiest deployment is via Docker. Simply run the following:
1. Build the Docker image:
   ```
   docker build -t winhttp-pac-test .
   ```
2. Run the container:
   ```
   docker run -p 8080:8080 winhttp-pac-test
   ```
   
# Individual / Dev Setup
If you want to do development, or are unable to use the Docker build, you can run this Service as described below.
1) start the core server 
   1) Make sure you have Python installer
   2) go to `./core`
   3) run `pip install -r requirements.txt`
   4) start the server using `python3 server.py`
2) Start the individual engines
   1) javascript engines
      1) Make sure nodejs and npm are installed
      2) go to the desired engine in `./engines/*`
      3) run `npm install` to download dependencies
      4) run `npm start` to launch the server
   2) winhttp engine
      1) make sure you have python3 32bit installed and available
      2) make sure you are on windows os (or use wine, example for this is in the Dockerfile)
      3) go to the desired engine in `./engines/*`
      4) run `python32bit -m pip install -r requirements.txt` to download dependencies
      5) run `python32bit winhttp.py` to launch the Server

After the core Server and all required engines are launched, you can start using the Pac-Tester.

Engines that are offline will result in a "failed due to timeout" error when running tests.

# API Endpoints
These are the most relevant API endpoints.
1. **GET /apidocs/**: Retrieve API documentation.
2. **POST /eval/**: Submit a PAC file for evaluation.
   - **Body Parameters**:
     ```
     {
       "dest_url": "string",    // URL to evaluate
       "src_ip": "string",      // Client IP (engine-specific)
       "pac_url": "string",     // URL of the PAC file
       "pac_content": "string"  // Content of the PAC file
     }
     ```
   - **Returns**:
     ```
     {
       "status": "success",     // Status of evaluation
       "message": "string",     // Error message (if any)
       "proxy": "any"           // Proxy result from evaluation
     }
     ```

# Engine-to-Core Interaction
Detailed interaction between the Core and Engine is described below.
The Core sends an evaluation payload to the Engine in the following format:
The exact Object that's send from the Core to the Engine is defined in [EvalData#engine_payload](https://github.com/TimeForANinja/winhttp-pac-test/blob/main/core/mytypes.py#L45)
```
dest_url: string - link for which the pac is evaluated
src_ip: string - ip of the client that evaluates the pac, not supported by all engines
pac_url: string - url from which the pac can be fetched
pac_content: string - content of the pac
```

### Server Response Format
The server responds with an HTTP status code (200, 4xx, or 5xx).
The Response Body consists of:
```
status: failed | success - indicates whether the PAC evaluation was successful.
message: string - mostly used for errors telling what exactly went wrong
proxy: any - resulting proxy that returned after the pac evaluation
```
