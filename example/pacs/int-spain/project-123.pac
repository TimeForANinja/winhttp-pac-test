// eslint-disable-next-line no-unused-vars
function FindProxyForURL(url, host)
{
	if (host == 'google.com')
	{
		return 'proxy02';
	}
	return 'DIRECT';
}
