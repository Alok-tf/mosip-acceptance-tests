import argparse
import logging
import os
import shutil
import sys
import urllib.request
import zipfile
import platform
import subprocess

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
rootPath = os.path.abspath(os.path.join(os.path.realpath(__file__), "../.."))
parser = argparse.ArgumentParser(description='Script to setup testrig')
logging.info("root path: " + rootPath)
# General Arguments
subparsers = parser.add_subparsers(dest='mode', help='sub-command help')
subparsers.required = True
subparsers_setup = subparsers.add_parser('setup', help='Setup testrig')
subparsers_run = subparsers.add_parser('run', help='Run testrig')
args = parser.parse_args()
print(args)
# global variables #
partnerDemoServiceUrl = "https://mosip.s3-us-west-2.amazonaws.com/0.9.1/authentication-partnerdemo-service.jar"
partnerDemoServiceJarPath = os.path.join(rootPath, "ivv-orchestrator/dependency_jars/authentication-partnerdemo-service.jar")

registrationServicesUrl = "https://mosip.s3-us-west-2.amazonaws.com/0.9.1/registration-services.jar"
registrationServicesJarPath = os.path.join(rootPath, "ivv-registration/services_jar/registration-services.jar")

databaseUrl = "https://mosip.s3-us-west-2.amazonaws.com/0.9.1/db.zip"
databaseLocalZipPath = os.path.join(rootPath, "ivv-orchestrator/db.zip")
databaseLocalFolderPath = os.path.join(rootPath, "ivv-orchestrator")


def checkPlatform():
    if platform.system() != 'Linux' and  platform.system() != 'Windows':
        logging.info("Current script not supported for "+platform.system())
        return
    logging.info("Your OS: "+platform.system())


def checkMaven():
    logging.info("Checking maven")
    try:
        ds = subprocess.run(["mvn", "-v"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if ds.returncode != 0:
            logging.error("Failed to check maven version")
            return

        if ds.stdout is None:
            logging.error("Maven not installed")
            return
    except subprocess.CalledProcessError:
        logging.error(subprocess.CalledProcessError.stderr)


def checkJavaHome():
    logging.info("Checking JAVA_HOME environment variable")
    try:
        ds = subprocess.run(["echo", "$JAVA_HOME"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if ds.returncode != 0:
            logging.error("Failed to check JAVA_HOME env")
            return

        if ds.stdout is None:
            logging.error("JAVA_HOME not set. Please set JAVA_HOME environment variable and try again.")
            return
    except subprocess.CalledProcessError:
        logging.error(subprocess.CalledProcessError.stderr)


def bytesToMB(v):
    return "%.2f" % round(v/1024/1024, 2)


def checkConfigFile():
    user_input = ''
    while user_input not in ['y', 'n']:
        logging.info("ivv-orchestrator/config.properties will be used to set the host and other user level credentials for testrig")
        user_input = input("Hello contributor, have you updated the ivv-orchestrator/config.properties (y/ n): ")
        if user_input == 'y':
            return
        elif user_input == 'n':
            logging.info("Please update ivv-orchestrator/config.properties, and run again")
            exit(0)
        else:
            logging.info("please enter y/ n")


def copydir(source, dest):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)
        for each_file in files:
            rel_path = root.replace(source, '').lstrip(os.sep)
            dest_path = os.path.join(dest, rel_path, each_file)
            shutil.copy(os.path.join(root, each_file), dest_path)


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)


def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize:  # near the end
            sys.stderr.write("\n")
    else:  # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))


def copyDependencies():
    src = os.path.join(rootPath, "dependencies")
    dest = os.path.join(rootPath, "ivv-orchestrator", "local")
    logging.info("Coping files from "+src+" to "+dest)
    copytree(os.path.join(rootPath, "dependencies"), os.path.join(rootPath, "ivv-orchestrator", "local"))
    logging.info("Coping files from "+src+" to "+dest+" done")


def copyConfigFile():
    src = os.path.join(rootPath, "ivv-orchestrator", "config.properties.example")
    dest = os.path.join(rootPath, "ivv-orchestrator", "config.properties")
    logging.info("Coping property file from "+src+" to "+dest)
    shutil.copyfile(src, dest)
    logging.info("Coping property file from "+src+" to "+dest+" done")


def downloadPartnerService():
    logging.info("Downloading Partner service from "+partnerDemoServiceUrl+" to "+partnerDemoServiceJarPath)
    urllib.request.urlretrieve(partnerDemoServiceUrl, partnerDemoServiceJarPath, reporthook)
    logging.info("Downloading Partner service from "+partnerDemoServiceUrl+" to "+partnerDemoServiceJarPath+" done")


def downloadRegistrationService():
    logging.info("Downloading Registration service from "+registrationServicesUrl+" to "+registrationServicesJarPath)
    urllib.request.urlretrieve(registrationServicesUrl, registrationServicesJarPath, reporthook)
    logging.info("Downloading Registration service from "+registrationServicesUrl+" to "+registrationServicesJarPath+" done")


def downloadLocalDatabase():
    logging.info("Downloading Local database from "+databaseUrl+" to "+databaseLocalZipPath)
    urllib.request.urlretrieve(databaseUrl, databaseLocalZipPath, reporthook)
    logging.info("Downloading Local database from "+databaseUrl+" to "+databaseLocalZipPath+" done")
    logging.info("Unzipping "+databaseLocalZipPath)
    with zipfile.ZipFile(databaseLocalZipPath, 'r') as zip_ref:
        zip_ref.extractall(databaseLocalFolderPath)
    logging.info("Removing "+databaseLocalZipPath)
    os.remove(databaseLocalZipPath)


def buildProject():
    try:
        ds = subprocess.Popen(['mvn', 'clean', 'install', '-f', rootPath+'/pom.xml', '-Dmaven.test.skip=true'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            output = ds.stdout.readline()
            if output == b'' and ds.poll() is not None:
                logging.info("break")
                break
            if output:
                logging.info(output.strip())
    except subprocess.CalledProcessError:
        logging.error(subprocess.CalledProcessError.stderr)
        exit(1)


def runTests():
    try:
        ds = subprocess.Popen(['mvn', 'test', '-f', rootPath+'/pom.xml'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logging.error(ds.stderr)
        while True:
            output = ds.stdout.readline()
            if output == b'' and ds.poll() is not None:
                break
                return
            if output:
                logging.info(output.strip())
    except subprocess.CalledProcessError:
        logging.error(subprocess.CalledProcessError.stderr)
        exit(1)


def setup():
    checkPlatform()
    checkMaven()
    checkJavaHome()
    copyDependencies()
    copyConfigFile()
    downloadPartnerService()
    downloadRegistrationService()
    downloadLocalDatabase()


def run():
    checkPlatform()
    checkMaven()
    checkJavaHome()
    checkConfigFile()
    buildProject()
    runTests()


if args.mode == 'setup':
    setup()
elif args.mode == 'run':
    run()
else:
    logging.warning("subcommand not found")
