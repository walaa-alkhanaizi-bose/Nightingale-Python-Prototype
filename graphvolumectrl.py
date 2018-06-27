import array
import math
import sys
import time
import wave

import matplotlib.pyplot as plt
import numpy
import pyaudio

import _thread

#instantiate global variables
gain = 0
write_data = '0'
cur_vol_lev = 4
last_meas_time = time.clock()
n = 0
N = 0
avg_noise = 0

#instantiate arrays to store data to be plotted
mic_xdata = []
mic_ydata = []
avg_mic_xdata = []
avg_mic_ydata = []
music_xdata = []
music_ydata = []
mod_music_xdata = []
mod_music_ydata = []

#declare some constants for data exchange
NUM_FRAMES = 1024
NUM_CHANNELS = 2

#flags for graphing
BAR_GRAPH_MIC = True
GRAPH_MIC = True
GRAPH_AVG_MIC = True
GRAPH_ORIG_MUSIC = False
GRAPH_MOD_MUSIC = False

####### FUNCTION DEFINITIONS #######

def plot():
    fig = 0
    if (BAR_GRAPH_MIC):
        global mic_bar
        fig += 1
        plt.figure(num=fig)
        #bar chart for mic data:
        mic_bar = plt.bar(x=0,height=0,width=1)
        ax = plt.axes()
        ax.set_ylim([0,30000])
        ax.set_ylabel("amplitude of mic data")
        # plt.show(block=False)
    if (GRAPH_AVG_MIC or GRAPH_MIC or GRAPH_MOD_MUSIC or GRAPH_ORIG_MUSIC):
        global mic_line, avg_mic_line, music_line, mod_music_line
        global mic_xdata, mic_ydata, avg_mic_xdata, avg_mic_ydata, music_xdata, music_ydata, mod_music_xdata, mod_music_ydata
        fig += 1
        plt.figure(num=fig)

        plt.xlabel('time')
        plt.ylabel('amplitude')
        plt.title('Mic data')
        axes = plt.gca()
        axes.set_xlim(0,1000)
        axes.set_ylim(10000,30000)
        mic_line, = axes.plot(mic_xdata, mic_ydata, 'b-')
        avg_mic_line, = axes.plot(avg_mic_xdata, avg_mic_ydata, 'r-')
        music_line, = axes.plot(music_xdata, music_ydata, 'g-')
        mod_music_line, = axes.plot(mod_music_xdata, mod_music_ydata, 'y-')
        #plt.show()
        plt.pause(.5)
        #plt.draw()
    #    plt.show(block=False)

def play():
    global write_data, music_avg, gain
    #write_data = [min(255, d+gain) for d in wf.readframes(NUM_FRAMES)]
    #write_data = [min(255, int(d*(math.pow(10,(gain/10))))) for d in wf.readframes(NUM_FRAMES)]
    write_data = []
    orig_music_avg = 0
    for d in wf.readframes(NUM_FRAMES):
        orig_music_avg += d
        write_data.append(min(255,int(d*(math.pow(10,(gain/10))))))
    #print("write data: ", str(write_data))
    output_stream.write(array.array('B', write_data).tostring())
    music_avg = numpy.mean(write_data)
    #print("music_avg = "+str(music_avg))
    #add datapoint to the plot
    if (GRAPH_MOD_MUSIC):
        mod_music_xdata.append(N)
        mod_music_ydata.append(music_avg)
        #print("xdata= ",mic_xdata)
        #print("ydata= ",mic_ydata)
        mod_music_line.set_xdata(mod_music_xdata)
        mod_music_line.set_ydata(mod_music_ydata)
        plt.draw()
        plt.pause(.00001)
    if (GRAPH_ORIG_MUSIC):
        music_xdata.append(N)
        music_ydata.append(orig_music_avg/len(write_data))
        #print("xdata= ",mic_xdata)
        #print("ydata= ",mic_ydata)
        music_line.set_xdata(music_xdata)
        music_line.set_ydata(music_ydata)
        plt.draw()
        plt.pause(.00001)


def listen():
    global mic_avg, N
    mic_avg = 0
    for d in input_stream.read(NUM_FRAMES):
        mic_avg += d*d
    mic_avg = mic_avg/(NUM_FRAMES*NUM_CHANNELS*3)
    
    if (BAR_GRAPH_MIC):
        #mic data bar chart
        mic_bar[0].set_height(mic_avg)
        # plt.draw()
        plt.pause(.00001)

    #print("mic_avg = "+str(mic_avg))
    #add datapoint to the plot
    N += 1
    if (GRAPH_MIC):
        mic_xdata.append(N)
        mic_ydata.append(mic_avg)
        #print("xdata= ",mic_xdata)
        #print("ydata= ",mic_ydata)
        mic_line.set_xdata(mic_xdata)
        mic_line.set_ydata(mic_ydata)
        plt.draw()
        plt.pause(.00001)


def adjust_volume():
    global mic_avg, music_avg, gain, last_meas_time, n, avg_noise, N#, avg_mic_line
    #this math is sketchy. Check and come up with a a better calculation
    noise = mic_avg - (music_avg * ((cur_vol_lev)/100)) #FIX
    avg_noise += noise
    n += 1
    if time.clock() >= last_meas_time + 1:
        avg_noise = avg_noise/n
        
        #add datapoint to the plot
        #N += 1
        if (GRAPH_AVG_MIC):
            avg_mic_xdata.append(N)
            avg_mic_ydata.append(avg_noise)
            #print("xdata= ",avg_mic_xdata)
            #print("ydata= ",avg_mic_ydata)
            avg_mic_line.set_xdata(avg_mic_xdata)
            avg_mic_line.set_ydata(avg_mic_ydata)
            plt.draw()
            plt.pause(.00001)

        print("noise val =",str(avg_noise))
        print("mic val =",str(mic_avg))
        #print("music val =",str(music_avg))
        # if avg_noise > 10:
        #     gain += 1
        #     print("NOISE!!!! and gain = ", gain)
        # if avg_noise < -20:
        #     gain -= 1
        #     print("QUIET!!!! and gain = ", gain)
        gain = max(-10, min(gain, 10)) #clip the gain to the max and min values
        n = 0
        avg_noise = 0
        last_meas_time = time.clock()


####### MAIN CODE ######
# instantiate PyAudio
p = pyaudio.PyAudio()

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

# open stream to record mic data
input_stream = p.open(format = pyaudio.paInt24,
                channels = NUM_CHANNELS,
                rate = 44100,
				frames_per_buffer = NUM_FRAMES,
				input=True)

# open stream to play audio through
output_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
				output=True)

#code that is going to run
plot()

while len(write_data) > 0:
    play()
    listen()
    adjust_volume()

#plt.show()
# stop streams
output_stream.stop_stream()
output_stream.close()
input_stream.stop_stream()
input_stream.close()

# close PyAudio
p.terminate()
