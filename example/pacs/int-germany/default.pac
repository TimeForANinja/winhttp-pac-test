const force_direct = [
    'google.com',
    'heise.com'
]

function arrayIncludes(array, item)
{
    for (var i = 0; i < array.length; i++)
    {
        if (array[i] == item)
        {
            return true;
        }
    }
    return false;
}

function FindProxyForURL(url, host) {
    if (arrayIncludes(force_direct, host)) {
        return "DIRECT"
    }
    return "PROXY01"
}
