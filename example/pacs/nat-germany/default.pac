// eslint-disable-next-line no-unused-vars
function FindProxyForURL(url, host)
{
	if (host == 'google.com')
	{
		return 'PROXY proxy02';
	}

	if (convert_addr(myIpAddress()) % 2 == 0)
	{
		return 'PROXY natproxy01';
	}
	else
	{
		return 'PROXY natproxy02';
	}
}
