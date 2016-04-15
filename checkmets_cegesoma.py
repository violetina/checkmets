#!/usr/bin/python3.4
import subprocess
import os
import datetime
import time
from distlib.compat import raw_input
from lxml import etree






basedir = raw_input('full path to start dir: ')
#basedir = '/home/tina/onderwijs/ARA_G05607_1915-02-08_01_000/'
pwd = os.getcwd()
success_path = os.path.join(pwd, "success.txt")
error_path = os.path.join(pwd, "error.txt")

if not basedir:
    print('please give a start path as argument!')
    quit()
#clear files
with open(success_path, "w"):
    pass
with open(error_path, "w"):
    pass
for root, dirs, files in os.walk(basedir):
   # print ("dirs: %s files: %s" % (dirs, files))
    for file in files:
        if file.endswith("mets.xml"):
            file_path = os.path.join(root, file)
            directory = root
            os.chdir(directory)
            try:
                md5list = list()
                doc = etree.parse(file_path)
                #print(file_path)
                tree = etree.parse(file_path)
                root = tree.getroot()
                expr = "//*[local-name() = $name]"
                expr2 = "count(//*[local-name() = $name])"
                count_elements = root.xpath(expr2, name="messageDigest")
                x = int(float(count_elements))

                for i in range(0,x):
                    #print(i)
                    md5 = root.xpath(expr, name = "messageDigest")[i].text
                    md5list.append(md5.upper())
                #print(md5list)

            except Exception as e:
                print(e)
                print("could not parse %s .. skipping..." % file_path)
                with open(error_path, "a") as error_out_file:
                        error_out_file.write("Aw Snap %s can not parse :s \n" % file_path)
                continue

            reflist = list()
            filelist = list()

            for ref in root.xpath('//@xlink:href', namespaces={'xlink': 'http://www.w3.org/1999/xlink'}):
                ref = ref.replace("file:///./" , "")
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
                    print("%s error md5: %s for file %s is not ok" % (st, key, faulty_file))
                    with open(error_path, "a") as error_out_file:
                        error_out_file.write("%s Aw Snap md5: %s for file %s is not ok \n" % (st, key, faulty_file))
                elif key in reflist:
                    id = md5list.index(key)
                    good_file = filelist[id]
                    # print("%s success %s for file %s is ok" % (st, key, good_file))
                    with open(success_path, "a") as good_out_file:
                        good_out_file.write("%s Wee! md5: %s for file %s is ok \n" % (st, key, good_file))
