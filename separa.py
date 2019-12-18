import os
import datetime

def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)



FimT=7070 #duração em segundos para 1:57:50 
intervaloT=2  
startT=2400
endT=startT + intervaloT

count = 0

while (endT<=2460):
	num =  ("{:0>5}".format(count))
	fileOut = "HomemFormiga_" + num + ".mkv" 	
	comando = "ffmpeg -v quiet -y -i Homem_Formiga.mkv -vcodec copy -acodec copy -ss " + humanize_time(startT) + " -t " + humanize_time(intervaloT) + " -sn " + fileOut
	print (comando)
	os.system(comando)
	count= count + 1
	startT=  endT+1
	endT= endT + intervaloT
	
	print ("start=",startT," endT=",endT)
	


#ffmpeg -vcodec copy -acodec copy -ss 00:10:00 -t 00:10:10 -i Tomb.Raider.A.Origem.2018.mkv teste1.mkv
# Rest after the first 20 Minutes





