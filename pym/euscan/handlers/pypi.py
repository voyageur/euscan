import json
import re

import portage

from euscan import mangling, helpers, output

HANDLER_NAME = "pypi"
CONFIDENCE = 100
PRIORITY = 90


def can_handle(pkg, url=None):
    return url and url.startswith('mirror://pypi/')


def guess_package(cp, url):
    match = re.search('mirror://pypi/\w+/(.*)/.*', url)
    if match:
        return match.group(1)

    cat, pkg = cp.split("/")

    return pkg


def scan_url(pkg, url, options):
    'https://warehouse.pypa.io/api-reference/json.html'

    package = guess_package(pkg.cpv, url)
    return scan_pkg(pkg, {'data': package})


def scan_pkg(pkg, options):
    package = options['data']

    output.einfo("Using PyPi API: " + package)

    url = 'https://pypi.python.org/pypi/%s/json' % package

    try:
        fp = helpers.urlopen(url)
    except urllib.error.URLError:
        return []
    except IOError:
        return []

    if not fp:
        return []

    data = fp.read()
    data = json.loads(data)

    if 'releases' not in data:
        return []

    ret = []

    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    ret = []
    for up_pv in data['releases']:
        pv = mangling.mangle_version(up_pv, options)
        if helpers.version_filtered(cp, ver, pv):
            continue
        urls = [entry['url'] for entry in data['releases'][up_pv]]
        urls = " ".join([mangling.mangle_url(url, options)
                         for url in urls])
        ret.append((urls, pv, HANDLER_NAME, CONFIDENCE))
    return ret
