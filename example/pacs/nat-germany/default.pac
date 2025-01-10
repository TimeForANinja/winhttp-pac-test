// eslint-disable-next-line no-unused-vars
function FindProxyForURL(url, host)
{
	if (host == 'google.com')
	{
		return 'proxy02';
	}
	if (convert_addr(myIpAddress()) % 2 == 0)
	{
		return 'natproxy01';
	}
	else
	{
		return 'natproxy02';
	}
}
