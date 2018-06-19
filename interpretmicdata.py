import pyaudio
import time
import numpy

# instantiate PyAudio
p = pyaudio.PyAudio()

num_frames = 1024
num_channels = 2

# open stream to record or play audio through
stream = p.open(format = pyaudio.paInt24,
                channels = num_channels,
                rate = 44100,
				frames_per_buffer = num_frames,
				input=True)
	
	
	
#DEbug and investigate
while True:
	avg = 0
	for d in stream.read(num_frames):
		avg += d
		#print(type(d))
		#print(str(d))
	avg = avg/(num_frames*num_channels*3)
	print("avg of samples = "+str(avg))
	time.sleep(.5)
	
	
###################################################################################3
###################################################################################3
###################################################################################3
###################################################################################3
###################################################################################3
###################################################################################3

#still working on making this function
repl_chr = ['\'', 'r', 'n', 't', '"', '%', '&', '#', '*']

while True:
	micdata = stream.read(num_frames)
	#print("type of data we are receiving from the mic is: "+str(type(micdata)))
	#print("length of array is: "+str(len(micdata)))
	print("micdata : "+ str(micdata)+"\n")
	samples = str(micdata)
	for chr in repl_chr:
		samples = samples.replace(chr,' ')
	samples = samples.split('\\')[1:]
	print("SAMPLES:"+str(samples)+"\n\n")

	samples = [int(b.encode('utf-8'), 16) for b in samples]
	print("SAMPLES:"+str(samples)+"\n\n")
	#print("mean of samples = ", numpy.mean(samples))
	'''if numpy.mean(samples)>50:
		print("loud noise!")
	time.sleep(0.001)#.250)
	'''
	
#working code
while True:
	micdata = stream.read(num_frames)
	#print("type of data we are receiving from the mic is: "+str(type(micdata)))
	#print("length of array is: "+str(len(micdata)))
	print("micdata : "+ str(micdata)+"\n")
	samples = str(micdata).replace('\'',' ').split('\\')[1:]
	#samples = [int('0'+b, 16) for b in samples]
	#print("SAMPLES:"+str(samples))
	#print("mean of samples = ", numpy.mean(samples))
	'''if numpy.mean(samples)>50:
		print("loud noise!")
	time.sleep(0.001)#.250)
	'''
