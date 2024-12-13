function FindProxyForURL(url, host) {
    // Block specific domains
    if (dnsDomainIs(host, "restricted.com")) {
        return "PROXY blocked.proxy.com:8080";
    }

    // Bypass proxy for specific domains
    if (shExpMatch(host, "*.example.com")) {
        return "DIRECT";
    }

/*
    var myip = myIpAddress()
    var myIpInt = convert_addr(myip)
    if (myIpInt % 2 == 0) {
        return "PROXY even:8080"
    }
*/

    // Test Multi-Proxy
    if (host === "google.com") {
        return "PROXY proxy01:8080; PROXY proxy02:8080";
    }

    // Use a specific proxy for all other requests
    return "PROXY proxyserver.company.com:8080";
}
