import re

expr="((http[s]?)?://)?[www][web][play]"
pattern=re.compile('(http[s]?://)?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
if pattern.match("http://www.cesco.coccco"):
    print "ok"
else:
    print "fail"
if pattern.match("https://www.cesco.coccco"):
    print "ok"
else:
    print "fail"

pat=re.compile("http[s]?://")
if pattern.match("www.cesco.coccco") :
    if pat.match("http://www.cesco.coccco"):
        print "doppio"
    else:
        print "singolo"
else:
    print "fail"
if pattern.match("cesco.coccco"):
    print "fail"
else:
    print "ok"
if pattern.match("www.cesco"):
    print "fail"
else:
    print "ok"
