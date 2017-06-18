
off_path="/home/cesco/Documenti/Stuff/botTelegram/offset.txt"
fileobj= open(off_path,"r+")
offset=int( fileobj.read().splitlines()[0] )
fileob.close()
