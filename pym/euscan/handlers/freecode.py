import urllib.request, urllib.parse, urllib.error
import re

import portage

from euscan import mangling, helpers, output

HANDLER_NAME = "freecode"
CONFIDENCE = 100
PRIORITY = 90


def can_handle(pkg, url=None):
    return False


def scan_pkg(pkg, options):
    cp, ver, rev = portage.pkgsplit(pkg.cpv)

    package = options['data'].strip()

    output.einfo("Using FreeCode handler: " + package)

    fp = urllib.request.urlopen("http://freecode.com/projects/%s/releases" % package)
    content = str(fp.read())

    result = re.findall(
        r'<a href="/projects/%s/releases/(\d+)">([^<]+)</a>' % package,
        content
    )

    ret = []
    for release_id, up_pv in result:
        pv = mangling.mangle_version(up_pv, options)
        if helpers.version_filtered(cp, ver, pv):
            continue
        fp = urllib.request.urlopen("http://freecode.com/projects/%s/releases/%s" %
                            (package, release_id))
        content = str(fp.read())
        download_page = re.findall(r'<a href="(/urls/[^"]+)"', content)[0]
        fp = urllib.request.urlopen("http://freecode.com%s" % download_page)
        content = str(fp.read())
        url = re.findall(
            r'In case it doesn\'t, click here: <a href="([^"]+)"',
            content
        )[0]
        ret.append((url, pv, HANDLER_NAME, CONFIDENCE))
    return ret
