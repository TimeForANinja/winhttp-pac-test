// Object for use as global context that includes all functions that can be used inside a PAC script
/* eslint-disable no-undef */
export const predefinedFuncs = {
    // taken from https://gist.github.com/nmoinvaz/82dd7e29e65e93ecd4ea6d2d2a5ccca1
    dnsDomainIs: (host, domain) => {
        return (host.length >= domain.length
            && host.substring(host.length - domain.length) === domain
        );
    },
    dnsDomainLevels: (host) => host.split('.').length - 1,
    convert_addr: (ipchars) => {
        var bytes = ipchars.split('.');
        var result = ((bytes[0] & 0xff) << 24)
            | ((bytes[1] & 0xff) << 16)
            | ((bytes[2] & 0xff) << 8)
            | (bytes[3] & 0xff);
        return result;
    },
    isValidIpAddress: (ipchars) => {
        var matches = ipchars.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/).exec(ipchars);
        if (matches === null) {
            return false;
        } else if (matches[1] > 255 || matches[2] > 255 || matches[3] > 255 || matches[4] > 255) {
            return false;
        }
        return true;
    },
    isInNet: (ipaddr, pattern, maskstr) => {
        if (!isValidIpAddress(pattern) || !isValidIpAddress(maskstr)) {
            return false;
        }
        if (!isValidIpAddress(ipaddr)) {
            ipaddr = dnsResolve(ipaddr);
            if (ipaddr == null) {
                return false;
            }
        }
        var host = convert_addr(ipaddr);
        var pat = convert_addr(pattern);
        var mask = convert_addr(maskstr);
        return (host & mask) == (pat & mask);
    },
    isPlainHostName: (host) => {
        return host.search('\\.') == -1;
    },
    localHostOrDomainIs: (host, hostdom) => {
        return (host == hostdom) || (hostdom.lastIndexOf(host + '.', 0) === 0);
    },
    shExpMatch: (url, pattern) => {
        pattern = pattern.replace(/\./g, '\\.');
        pattern = pattern.replace(/\*/g, '.*');
        pattern = pattern.replace(/\?/g, '.');
        var newRe = new RegExp('^' + pattern + '$');
        return newRe.test(url);
    },
    // dummy
    isResolvable: () => false,
    dnsResolve: () => '1.1.1.1',
    myIpAddress: () => '1.1.1.1',
    weekdayRange: () => false,
    dateRange: () => false,
    timeRange: () => false,
    alert: () => {},
}
/* eslint-enable no-undef */

// helper func to build a vm command to execute
export const build_cmd = (host, url=null) => {
    let must_url = url ? url : 'https://' + host + '/test'
    return `test = FindProxyForURL('${must_url}', '${host}');`
}
