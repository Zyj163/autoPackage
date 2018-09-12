#!/usr/local/bin/python3

# http://liumh.com/2015/11/25/ios-auto-archive-ipa/

import argparse
import subprocess
from pgyer import uploadIpaToPgyer

CONFIGURATION = 'Release'
EXPORT_OPTIONS_PLIST = 'exportOptions.plist'  # app-store, ad-hoc, enterprise, development
EXPORT_MAIN_DIRECTORY = '~/Desktop/'
# CODE_SIGN_IDENTITY = 'iPhone Distribution: Beijing Hot Video Technology Co., Ltd. (X6LR5SNFNR)'
CODE_SIGN_IDENTITY = None

UPLOAD_DESC = ''

IF_UPLOAD = False

def buildArchivePath(tmpName):
    process = subprocess.Popen('pwd', stdout=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate()
    archiveName = '%s.xcarchive' % tmpName

    return '%s/%s' % (stdoutdata.decode().strip(), archiveName)


def buildExportPath(scheme):
    cmd = 'date "+%Y-%m-%d_%H-%M-%S"'
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = process.communicate()
    return EXPORT_MAIN_DIRECTORY + scheme + stdoutdata.decode().strip()


def getIpaPath(exportPath):
    cmd = 'ls %s | grep *.ipa' % exportPath
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = process.communicate()
    ipaName = stdoutdata.decode().strip()
    return exportPath + '/' + ipaName


def cleanTmpFile(file):
    cleanCMD = 'rm -r %s' % file
    process = subprocess.Popen(cleanCMD, shell=True)
    process.wait()

    code = process.returncode
    if code != 0:
        print('clean file %s failed' % file)
    else:
        print('clean archive file: %s', file)


def exportArchive(scheme, archivbePath):
    dir = buildExportPath(scheme)
    cmd = 'xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s' % (
        archivbePath,
        dir,
        EXPORT_OPTIONS_PLIST
    )
    process = subprocess.Popen(cmd, shell=True)
    process.wait()

    code = process.returncode
    if code != 0:
        print('export %s failed' % scheme)
        return ''

    return dir


def buildWorkspace(workspace, scheme):
    archivePath = buildArchivePath(scheme)

    print('archivePath: %s' % archivePath)

    cmd = 'xcodebuild -workspace %s -scheme %s -configuration %s -sdk iphoneos build' \
                 ' archive -archivePath %s -destination generic/platform=iOS' % (
                     workspace,
                     scheme,
                     CONFIGURATION,
                     archivePath
                 )
    build(scheme, cmd, workspace)


def buildProject(project, scheme):
    archivePath = buildArchivePath(scheme)

    print('archivePath: %s' % archivePath)

    cmd = 'xcodebuild -project {p} -scheme {s} -configuration {c} archive -archivePath' \
          ' {a} -destination generic/platform=iOS'.format(p=project, s=scheme, c=CONFIGURATION, a=archivePath)

    build(scheme, cmd, project)


def build(scheme, cmd, name):
    archivePath = buildArchivePath(scheme)

    print('archivePath: %s' % archivePath)

    if CODE_SIGN_IDENTITY is not None:
        cmd.replace('-destination', 'CODE_SIGN_IDENTITY="%s"' % CODE_SIGN_IDENTITY + ' -destination')

    process = subprocess.Popen(cmd, shell=True, cwd='..')
    process.wait()

    code = process.returncode
    if code != 0:
        print('archive workspace %s failed' % name)
    else:
        exportDir = exportArchive(scheme, archivePath)
        if exportDir != '' and IF_UPLOAD:
            ipaPath = getIpaPath(exportDir)
            uploadIpaToPgyer(ipaPath, UPLOAD_DESC)

    cleanTmpFile(archivePath)


def xcbuild(options):
    project = options.project
    workspace = options.workspace
    scheme = options.scheme

    global UPLOAD_DESC

    UPLOAD_DESC = options.desc

    if project is None and workspace is None:
        pass
    elif project is not None:
        buildProject(project, scheme)
    elif workspace is not None:
        buildWorkspace(workspace, scheme)


def autoFindFiles(options):
    process = subprocess.Popen('ls ..', stdout=subprocess.PIPE, shell=True)
    stdoutdata, _ = process.communicate()
    files = stdoutdata.decode().strip().split('\n')

    workspace = None
    project = None

    for file in files:
        if file.endswith('.xcworkspace'):
            workspace = file
        elif file.endswith('.xcodeproj'):
            project = file
        if workspace is not None:
            break

    if workspace is not None:
        options.workspace = workspace
        options.scheme = workspace.split('.')[0]
    elif project is not None:
        options.project = project
        options.scheme = workspace.split('.')[0]
    else:
        print('no valid file found')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-w',
        '--workspace',
        help='Build the workspace name.xcworkspace.',
        metavar='name.xcworkspace'
    )
    parser.add_argument(
        '-p',
        '--project',
        help='Build the project name.xcodeproj.',
        metavar='name.xcodeproj'
    )
    parser.add_argument(
        '-s',
        '--scheme',
        help='Build the scheme specified by schemename. Required if building a workspace.',
        metavar='schemename'
    )
    parser.add_argument(
        '-m',
        '--desc',
        help='Pgyer update description.',
        metavar='description'
    )
    parser.add_argument(
        '-u',
        '--upload',
        help='if upload.',
        metavar='upload'
    )

    options = parser.parse_args()

    if options.upload is not None:
        global IF_UPLOAD
        IF_UPLOAD = options.upload

    if options.scheme is None and options.workspace is None and options.project is None:
        autoFindFiles(options)

    print('options: %s' % options)

    xcbuild(options)


main()
