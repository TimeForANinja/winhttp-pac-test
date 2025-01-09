# winhttp-pac-test

This project provides a rest-based tool to test PAC (Proxy Auto-Configuration) files.
It's easy to deploy using the provided Docker Image, and can be used by doing simple REST-Requests.
Follow the instructions below for setup and usage.

# Project Setup
The Project is made up multiple modular Webservers, split into two main components.
1. Core Server  
This Server, located in the `/app`-Folder, is the Main Entrypoint for the End-User.  
It hosts an api (and swagger docs) for running tests on PAC Files.
2. Engines  
The Engines, various subfolders in the `/engines` Directory, are individual Web-Servers that do a single evaluation on the PAC.
This includes Engines like the `v8` as a std javascript engine or `winhttp` to test the microsoft stack.
3. Examples
En example unit test script, including the required python code to interact with the api and csv test-data can be found in the `/example`-Folder.

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
For the "Main" Server you can find relevant auto-generated swagger docs under `/docs`.

The Engines feature only two Endpoints:
1. **GET /up/**: A simple Health-Check Endpoint to check if the Engine is running.
2. **POST /**: Submit a PAC file for evaluation.
   - **Body Parameters**:
     ```
     {
       "pac": {
         "url": "string",     // URL of the PAC file
                              // WinHTTP fetches it via POST from the Core-Server
         "content": "string"  // Content of the PAC file
                              // Other APIs can work directly with the content
       },
       "dest_url": "string",    // URL to evaluate
       "src_ip": "string"       // Client IP (only some engines support this)
     }
     ```
   - **Returns**:
     ```
     {
       "status": "success",       // Status of evaluation (success or failed)
       "error": "XYZ is invalid", // Explanation for the error (if failed)
       "error_code": -1,          // Error Code if it failed (if failed)
       "message": "string",       // Error message (if failed)
       "proxy": "any"             // Proxy result from evaluation (if success)
     }
     ```

# Engines
The following Engines are packaged with the Library, and support the following Features.

| Name   | Description                                       | Validation<br>(Is the Syntax valid) | Evaluation<br>(Simulate a PAC evaluation for a given dest host) | SRC_IP<br>(simulate a specific source ip for a pac resolution) |
|--------|---------------------------------------------------|-------------------------------------|-----------------------------------------------------------------|----------------------------------------------------------------|
| v8     | Generic Javascript v8 Engine (Nodejs Environment) | yes                                 | yes                                                             | yes                                                            |
| eslint | Linting of the PAC File                           | yes                                 | no                                                              | no                                                             |
| winhttp | WinHTTP evaluation of the PAC                    | yes                                 | yes                                                             | no                                                             | 
