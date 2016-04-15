#!/usr/bin/python3
#import libxml2
import subprocess
import os
import datetime
import time
from lxml import etree
from distlib.compat import raw_input

sshfs_enabled = raw_input('mount a server? (y/n): ')

pwd = os.getcwd()
success_path = os.path.join(pwd, "success.txt")
error_path = os.path.join(pwd, "error.txt")

with open(success_path, "w"):
    pass
with open(error_path, "w"):
    pass


def checker():
    for root, dirs, files in os.walk(basedir):

        for file in files:
            if file.endswith("mets.xml"):
                file_path = os.path.join(root, file)
                directory = root
                os.chdir(directory)
                try:
                    doc = etree.parse(file_path)

                except Exception as e:
                    print(e)
                    print("could not parse %s .. skipping..." % file_path)
                    with open(error_path, "a") as error_out_file:
                            error_out_file.write("Aw Snap %s is not parsable :s \n" % file_path)
                    continue

                md5list = list()
                reflist = list()
                filelist = list()

                for md5s in doc.xpath("//@CHECKSUM"):
                    md5list.append(md5s.upper())
                #print(md5list)
                for ref in doc.xpath('//@xlink:href',namespaces={'xlink': 'http://www.w3.org/1999/xlink'}):
                    # figure out how one can avoid echo -n to not have b and  \n (new lines and breaks) in output
                    cal_md5 = subprocess.Popen(["echo -n $(md5sum %s | cut -d' ' -f 1)" % ref],
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               shell=True, universal_newlines=True)
                    (out, err) = cal_md5.communicate()
                    reflist.append(out.upper())
                    file_to_check = os.path.join(directory, ref)
                    filelist.append(file_to_check)
                for key in md5list:
                    ts = time.time()
                    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    if key not in reflist:
                        id = md5list.index(key)
                        faulty_file = filelist[id]
                        print("%s error %s for file %s is not ok" % (st, key, faulty_file))
                        with open(error_path, "a") as error_out_file:
                            error_out_file.write("%s Aw Snap %s for file %s is not ok \n" % (st, key, faulty_file))
                    elif key in reflist:
                        id = md5list.index(key)
                        good_file = filelist[id]
                        #print("%s success %s for file %s is ok" % (st, key, good_file))
                        with open(success_path, "a") as good_out_file:
                            good_out_file.write("%s Wee! %s for file %s is ok \n" % (st, key, good_file))

if sshfs_enabled == 'y':

    temp_dir_src = 'metchecker'
    source_user = raw_input('user for sshfs: ')
    source_srv = raw_input('source server: ')
    fs = raw_input('/filesystem/path/on/src_server:')
    temp_dir_src = os.path.abspath(temp_dir_src)
    basedir = temp_dir_src



    if not os.path.exists(temp_dir_src) and not os.path.ismount(temp_dir_src):
        os.mkdir(temp_dir_src,mode=0o777)


    def sshmount():
        print("mounting server...")
        subprocess.call(["sshfs  -o nonempty -o allow_other  %s@%s:%s %s ; mount | grep %s" % (
            source_user, source_srv, fs, temp_dir_src, fs)], shell=True)

    def fuserunmount():
        print("unmounting server...")
        subprocess.call(["fusermount -u %s" % temp_dir_src], shell=True)

    sshmount()
    checker()
    fuserunmount()

elif sshfs_enabled == 'n':
    pass
    basedir = raw_input('full path to start dir: ')
    checker()
else:
    print("please type y or n")
    quit()












