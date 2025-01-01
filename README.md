# winhttp-pac-test

# Documentation
Simply start the Server or the Docker and go to
http://localhost:8080/apidocs/

# Engine <-> Core Interaction

The exact Object that's send from the Core to the Engine is defined in [EvalData#engine_payload](https://github.com/TimeForANinja/winhttp-pac-test/blob/main/core/mytypes.py#L45)
```
dest_url: string - link for which the pac is evaluated
src_ip: string - ip of the client that evaluates the pac, not supported by all engines
pac_url: string - url from which the pac can be fetched
pac_content: string - content of the pac
```

The Server then responds with either a 200, 4xx or 5xx Status Code.
The Response Body consists of:
```
status: failed | success - was the evaluation successfull?
message: string - mostly used for errors telling what exactly went wrong
proxy: any - resulting proxy that returned after the pac evaluation
```
