import argparse
from zipfile import ZipFile
from os import path

import requests
from requests.exceptions import RequestException


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('browser', choices=['edge', 'chrome'], help='Browser to use')
    parser.add_argument('-v', '--version', help='Browser version', required=True)
    parser.add_argument('-p', '--platform', help='Platform', required=True)
    args = parser.parse_args()

    driver_folder = path.join(path.dirname(path.abspath(__file__)), 'lib', 'webdriver')
    extension_folder = path.join(path.dirname(path.abspath(__file__)), 'lib', 'autodraw')

    browser = args.browser
    browser_version = args.version
    platform = args.platform

    if browser == 'edge':
        print(f'Downloading Edge WebDriver version {browser_version}...')
        webdriver_url = f'https://msedgedriver.azureedge.net/{browser_version}/edgedriver_{platform}.zip'
        try:
            webdriver_req = requests.get(webdriver_url, allow_redirects=True, timeout=10)
        except RequestException as e:
            print(f'Error: {e}')
            return

        zip_path = path.join(driver_folder, f'edgedriver_{browser_version}_{platform}.zip')

        with open(zip_path, 'wb') as file:
            file.write(webdriver_req.content)

        print('Extracting...')
        with ZipFile(zip_path, 'r') as zip:
            zip.extractall(path=driver_folder)
        
    elif browser == 'chrome':
        print(f'Downloading Chrome WebDriver version {browser_version}...')
        webdriver_url = f'https://chromedriver.storage.googleapis.com/{browser_version}/chromedriver_{platform}.zip'
        try:
            webdriver_req = requests.get(webdriver_url, allow_redirects=True, timeout=10)
        except RequestException as e:
            print(f'Error: {e}')
            return

        zip_path = path.join(driver_folder, f'chromedriver_{browser_version}_{platform}.zip')

        with open(zip_path, 'wb') as file:
            file.write(webdriver_req.content)

        print('Extracting...')
        with ZipFile(zip_path, 'r') as zip:
            zip.extractall()

    print('Done!')

    print('Downloading AutoDraw extension...')
    extension_url = f'https://clients2.google.com/service/update2/crx?response=redirect&prodversion={browser_version}&acceptformat=crx2,crx3&x=id%3D{"bpnefockcbbpkbahgkkacjmebfheacjb"}%26uc'
    extension_req = requests.get(extension_url, allow_redirects=True, timeout=10)

    crx_path = path.join(extension_folder, f'autodraw.crx')

    with open(crx_path, 'wb') as file:
        file.write(extension_req.content)


if __name__ == '__main__':
    main()
