import array
import math
import sys
import time
import wave
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
# import sounddevice as sd
import struct
# import _thread


#instantiate global variables
gain = 0
write_data = '0'
cur_vol_lev = 4 #fix this sketchy math to figure out the multiplier for current volume level
cur_vol_gain = math.pow(10, (-100+cur_vol_lev)/10) / math.pow(10, 1/10)
last_meas_time = time.clock()
n = 0
N = 0
avg_noise = 0
#instantiate arrays to store data to be plotted
mic_xdata = []
mic_ydata = []
avg_noise_xdata = []
avg_noise_ydata = []
music_xdata = []
music_ydata = []
mod_music_xdata = []
mod_music_ydata = []
#declare some constants for data exchange
NUM_FRAMES = 1024
NUM_CHANNELS = 2
#flags for graphing
Flags = [0,0,0,0,0]
BAR_GRAPH_MIC = Flags[0]
GRAPH_MIC = Flags[1]
GRAPH_AVG_NOISE= Flags[2]
GRAPH_ORIG_MUSIC = Flags[3]
GRAPH_MOD_MUSIC = Flags[4]


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
        ax.set_ylim([0,45000])
        ax.set_ylabel("amplitude of mic data")
    if (GRAPH_AVG_NOISE or GRAPH_MIC or GRAPH_MOD_MUSIC or GRAPH_ORIG_MUSIC):
        global mic_line, avg_noise_line, music_line, mod_music_line
        global mic_xdata, mic_ydata, avg_noise_xdata, avg_noise_ydata, music_xdata, music_ydata, mod_music_xdata, mod_music_ydata
        fig += 1
        plt.figure(num=fig)
        plt.xlabel('time')
        plt.ylabel('amplitude')
        plt.title('Mic data')
        axes = plt.gca()
        axes.set_xlim(0,1000)
        axes.set_ylim(0,30000)
        mic_line, = axes.plot(mic_xdata, mic_ydata, 'b-', label="mic data")
        avg_noise_line, = axes.plot(avg_noise_xdata, avg_noise_ydata, 'r-', label="average noise data")
        music_line, = axes.plot(music_xdata, music_ydata, 'g-', label="music data")
        mod_music_line, = axes.plot(mod_music_xdata, mod_music_ydata, 'y-', label="modified music data")
        axes.legend()
        plt.pause(.5)

def play():
    global write_data, music_avg, gain
    music_data = struct.unpack(format_string, wf.readframes(NUM_FRAMES))
    write_data = np.multiply(music_data, math.pow(10, gain/10))
    #limit the entries in write_Data to the bounds of a Short type
    write_data = np.clip(write_data, a_min=-32768, a_max=32767)
    # print("write data: ", str(write_data))
    output_stream.write(struct.pack(format_string, *write_data.astype(int)))
    orig_music_avg = np.mean(np.square(music_data))
    music_avg = np.mean(np.square(write_data))
    #print("music_avg = "+str(music_avg))
    # manage plots and update datapoints
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
        music_ydata.append(orig_music_avg)
        #print("xdata= ",mic_xdata)
        #print("ydata= ",mic_ydata)
        music_line.set_xdata(music_xdata)
        music_line.set_ydata(music_ydata)
        plt.draw()
        plt.pause(.00001)

def listen():
    global mic_avg, N
    mic_avg = 0
    short_mic_data = struct.unpack(format_string, input_stream.read(NUM_FRAMES))
    # print("short mic data: ",short_mic_data)
    mic_avg = np.mean(np.square(short_mic_data))
    # print("mic_avg = "+str(mic_avg))
    # manage plots and update datapoints
    N += 1
    if (BAR_GRAPH_MIC):
        #mic data bar chart
        mic_bar[0].set_height(mic_avg)
        plt.pause(.00001)
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
    global mic_avg, music_avg, gain, last_meas_time, n, avg_noise, N
    #this math is sketchy. Check and come up with a a better calculation
    noise = math.sqrt(mic_avg) - (math.sqrt(music_avg) * cur_vol_gain)#((cur_vol_lev)/100)) #FIX
    avg_noise += noise
    n += 1
    if time.clock() >= last_meas_time + 1:
        avg_noise = avg_noise/n
        print("noise val =",str(avg_noise))
        print("mic val =",str(math.sqrt(mic_avg)))
        print("music val =",str(math.sqrt(music_avg)))
        # print("orig music val =",str(orig_music_avg))
        
        # manage plots and update datapoints
        if (GRAPH_AVG_NOISE):
            avg_noise_xdata.append(N)
            avg_noise_ydata.append(avg_noise)
            #print("xdata= ",avg_mic_xdata)
            #print("ydata= ",avg_mic_ydata)
            avg_noise_line.set_xdata(avg_noise_xdata)
            avg_noise_line.set_ydata(avg_noise_ydata)
            plt.draw()
            plt.pause(.00001)
        # update the gain/volume based on noise value
        if avg_noise > 10:
            gain += 1
            print("NOISE!!!! and gain = ", gain)
        if avg_noise < -20:
            gain -= 1
            print("QUIET!!!! and gain = ", gain)
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
# details for the channel number, format, and rate are located at:
# Manage Audio Devices > Recording > Microphone Properties > Advanced > Default Format
# I changed the default format to 16 bits instead of 24 for ease of conversion to int
input_stream = p.open(format = pyaudio.paInt16,
                    channels = NUM_CHANNELS,
                    rate = 48000,
                    frames_per_buffer = NUM_FRAMES,
                    input=True)
#create the format string for unpacking the bytestring input correctly
format_string = '<'+'h'*NUM_CHANNELS*NUM_FRAMES

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

# stop streams
output_stream.stop_stream()
output_stream.close()
input_stream.stop_stream()
input_stream.close()

# close PyAudio
p.terminate()
