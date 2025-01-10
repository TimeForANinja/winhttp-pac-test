// eslint-disable-next-line no-unused-vars
function FindProxyForURL(url, host)
{
	if (host == 'google.com')
	{
		return 'PROXY proxy02;';
	}
	return 'PROXY intproxy01;';
}
