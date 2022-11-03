import argparse
from zipfile import ZipFile

import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', help='Version of Edge', required=True)
    args = parser.parse_args()

    edge_version = args.version
    
    print(f'Downloading Edge WebDriver version {edge_version}...')
    webdriver_url = f'https://msedgedriver.azureedge.net/{edge_version}/edgedriver_win64.zip'
    print('got: ', webdriver_url)
    webdriver_req = requests.get(webdriver_url, allow_redirects=True, timeout=10)
    with open('edgedriver_win64.zip', 'wb') as file:
        file.write(webdriver_req.content)

    print('Extracting...')
    with ZipFile('edgedriver_win64.zip', 'r') as zip:
        zip.extract('msedgedriver.exe')

    print('Done!')

    print('Downloading AutoDraw extension...')
    extension_url = f'https://clients2.google.com/service/update2/crx?response=redirect&prodversion={edge_version}&acceptformat=crx2,crx3&x=id%3D{"bpnefockcbbpkbahgkkacjmebfheacjb"}%26uc'
    extension_req = requests.get(extension_url, allow_redirects=True, timeout=10)
    with open('extension.crx', 'wb') as file:
        file.write(extension_req.content)


if __name__ == '__main__':
    main()
