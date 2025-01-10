var force_direct = [
	'facebook.com',
	'heise.com'
];

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

// eslint-disable-next-line no-unused-vars
function FindProxyForURL(url, host)
{
	if (host == 'google.com')
	{
		return 'proxy02';
	}
//	if (arrayIncludes(force_direct, host))
//	{
//		return 'DIRECT';
//	}
	return 'intproxy01';
}
