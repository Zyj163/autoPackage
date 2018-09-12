
import requests
import argparse

# configuration for pgyer
PGYER_UPLOAD_URL = 'http://www.pgyer.com/apiv1/app/upload'
DOWNLOAD_BASE_URL = 'http://www.pgyer.com'
USER_KEY = 'a0fea86fb67c87ec2c2df245e3b63229'
API_KEY = '84cd5e9085a2d0fdb628a7bfb76e920d'
#设置从蒲公英下载应用时的密码
PGYER_PASSWORD = ''

def parserUploadResult(jsonResult):
    resultCode = jsonResult['code']
    if resultCode == 0:
        downUrl = 'http://www.pgyer.com' + '/' + jsonResult['data']['appShortcutUrl']
        print('Upload Success')
        print('DownUrl is:' + downUrl)
    else:
        print('Upload Fail!')
        print('Reason:' + jsonResult['message'])


def uploadIpaToPgyer(ipaPath, desc):
    print('ipaPath:' + ipaPath)

    files = {'file': open(ipaPath, 'rb')}
    headers = {'enctype': 'mutipart/form-data'}
    payload = {
        'uKey': USER_KEY,
        '_api_key': API_KEY,
        'publishRange': '2',
        'isPublishToPublish': '2',
        'password': PGYER_PASSWORD,
        'updateDescription': desc
    }
    print('update desc:' + '')
    print('uploading...')
    r = requests.post(PGYER_UPLOAD_URL, data=payload, files=files, headers=headers)
    if r.status_code == requests.codes.ok:
        result = r.json()
        parserUploadResult(result)
    else:
        print('HTTPError, code: ' + r.status_code)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--path',
        help='ipa path.',
        metavar='name.ipa'
    )
    parser.add_argument(
        '-m',
        '--desc',
        help='Pgyer update description.',
        metavar='description'
    )

    options = parser.parse_args()

    uploadIpaToPgyer(options.path, options.desc)


if __name__ == '__main__':
    main()
