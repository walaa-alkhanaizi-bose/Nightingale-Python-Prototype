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
import os

#instantiate global variables
number_of_steps = 0
gain = 0
write_data = '0'
cur_vol_lev = 4 #fix this sketchy math to figure out the multiplier for current volume level
cur_vol_gain = lambda cur_vol_lev: math.pow(10, (-100+cur_vol_lev)/10) / math.pow(10, 1/10)
last_meas_time = time.clock()
n = 0
N = 0
avg_noise = 0
avg_noise_relative_no_gain = 0
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
NOISE_PERSISTENCE = 5
GAIN_STEP = 2
GAIN_lIMIT = 20
#flags for graphing
Flags = [0,0,0,0,0]
BAR_GRAPH_MIC = Flags[0]
GRAPH_MIC = Flags[1]
GRAPH_AVG_NOISE= Flags[2]
GRAPH_ORIG_MUSIC = Flags[3]
GRAPH_MOD_MUSIC = Flags[4]
#flag for printing the data arrays
PRINT_DATA_ARRAYS = 1
#define some events for the SM
NOISE = 1
NOEVENT = 0
QUIET = -1
#define states for the state machine
idle = 0
noise_ct = 1
quiet_ct = 2
#inititlize the state of SM to idle
state = idle
#CONSTANTS FOR VOLUME CONTROL
CHANGE_VOLUME_COMMAND = "NirCmd changesysvolume "
VOLUME_STEP = 655.35

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
    global write_data, music_avg, gain, orig_music_avg
    #get raw music data
    music_data = struct.unpack(format_string, wf.readframes(NUM_FRAMES))
    #apply the relevant gain to all the data entries
    write_data = np.multiply(music_data, 1)#math.pow(10, gain/10))
    #limit each entry in write_Data to the bounds of a Short type
    write_data = np.clip(write_data, a_min=-32768, a_max=32767)
    #send the music to the speaker audio stream
    output_stream.write(struct.pack(format_string, *write_data.astype(int)))
    orig_music_avg = np.mean(np.square(music_data))
    music_avg = np.mean(np.square(write_data))
    # manage plots and update datapoints
    music_xdata.append(N)
    music_ydata.append(math.sqrt(orig_music_avg))
    if (GRAPH_MOD_MUSIC):
        mod_music_xdata.append(N)
        mod_music_ydata.append(math.sqrt(music_avg))
        mod_music_line.set_xdata(mod_music_xdata)
        mod_music_line.set_ydata(mod_music_ydata)
        plt.draw()
        plt.pause(.00001)
    if (GRAPH_ORIG_MUSIC):
        music_xdata.append(N)
        music_ydata.append(math.sqrt(orig_music_avg))
        music_line.set_xdata(music_xdata)
        music_line.set_ydata(music_ydata)
        plt.draw()
        plt.pause(.00001)

def record():
    global mic_avg, N
    mic_avg = 0
    short_mic_data = struct.unpack(format_string, input_stream.read(NUM_FRAMES))
    mic_avg = np.mean(np.square(short_mic_data))
    # manage plots and update datapoints
    N += 1
    mic_xdata.append(N)
    mic_ydata.append(math.sqrt(mic_avg))
    if (BAR_GRAPH_MIC):
        #mic data bar chart
        mic_bar[0].set_height(math.qrt(mic_avg)*50000)
        plt.pause(.00001)
    if (GRAPH_MIC):
        mic_line.set_xdata(mic_xdata)
        mic_line.set_ydata(mic_ydata)
        plt.draw()
        plt.pause(.00001)

def adjust_volume():
    global mic_avg, music_avg, number_of_steps, gain, last_meas_time, n, avg_noise, N, cur_vol_lev, orig_music_avg, noise_relative_no_gain, avg_noise_relative_no_gain
    #this math is sketchy. Check and come up with a a better calculation
    noise = math.sqrt(mic_avg) - (math.sqrt(music_avg) * (cur_vol_gain(cur_vol_lev+number_of_steps)))
    noise = math.sqrt(mic_avg) - (math.sqrt(music_avg) * (cur_vol_gain(cur_vol_lev+(gain/20)*100)))
    avg_noise += noise
    
    noise_relative_no_gain = math.sqrt(mic_avg) - math.sqrt(orig_music_avg) * (cur_vol_gain(cur_vol_lev))
    avg_noise_relative_no_gain += noise_relative_no_gain
    
    n += 1
    if time.clock() >= last_meas_time + 1:
        avg_noise = avg_noise/n
        avg_noise_relative_no_gain = avg_noise_relative_no_gain/n
        print("noise val =",str(avg_noise))
        # print("noise relative no gain val =",str(avg_noise_relative_no_gain))
        # print("mic val =",str(math.sqrt(mic_avg)))
        # print("music val =",str(math.sqrt(music_avg)))
        # manage plots and update datapoints
        avg_noise_xdata.append(N)
        avg_noise_ydata.append(avg_noise)
        if (GRAPH_AVG_NOISE):

            avg_noise_line.set_xdata(avg_noise_xdata)
            avg_noise_line.set_ydata(avg_noise_ydata)
            plt.draw()
            plt.pause(.00001)
        # update the gain/volume based on noise value
        if avg_noise > 20:
            volume_adjustment_SM(NOISE)
            print("NOISE!!!!")# and gain = ", gain)
        elif avg_noise < 10 and number_of_steps > 0:
            print("QUIET down")#and gain = ", gain)
            # set_volume_to_original_level()
            volume_adjustment_SM(QUIET)
        #priority to if the noise has quieted down enough to return to original volume
        elif avg_noise_relative_no_gain < 20 and avg_noise_relative_no_gain > 10:
            print("QUIET!!!! and gain = ", gain)
            # set_volume_to_original_level()
            volume_adjustment_SM(QUIET)
        else:
            volume_adjustment_SM(NOEVENT)
        gain = max(0, min(gain, GAIN_lIMIT)) #clip the gain to the max and min values
        n = 0
        avg_noise = 0
        last_meas_time = time.clock()

def volume_adjustment_SM(event):
    global number_of_steps, gain, state, NOISE, QUIET, NOEVENT, idle, noise_ct, quiet_ct, count
    #make sure any noise or quiet persists for 5 seconds before altering the gain
    # print("event is: ", event)
    # print("state is: ", state)
    if (event == NOEVENT):
        count = 0
        state = idle
    elif (state == idle):
        count = 1
        state = noise_ct if (event == NOISE) else quiet_ct
    elif (state == noise_ct):
        count += 1
        if (event == QUIET):
            count = 0
            state = quiet_ct
        elif (count == NOISE_PERSISTENCE):
            state = idle
            count = 0
            gain += GAIN_STEP
            number_of_steps += 1
            cmd_arg = CHANGE_VOLUME_COMMAND + str(VOLUME_STEP)
            os.system(cmd_arg)
    elif (state == quiet_ct):
        count += 1
        if (event == NOISE):
            count = 0
            state = noise_ct
        elif (count == NOISE_PERSISTENCE):
            state = idle
            count = 0
            gain -= GAIN_STEP
            number_of_steps -= 1
            cmd_arg = CHANGE_VOLUME_COMMAND + str(-VOLUME_STEP)
            os.system(cmd_arg)

def set_volume_to_original_level():
    global gain, count
    gain =  0
    count = 0

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

plot()
while len(write_data) > 0:
    play()
    record()
    adjust_volume()

# if PRINT_DATA_ARRAYS:
print("avg_noise_xdata = ", avg_noise_xdata)
print("avg_noise_ydata = ", avg_noise_ydata)
print("music_xdata = ", music_xdata)
print("music_ydata = ", music_ydata)
print("mic_xdata = ", mic_xdata)
print("mic_ydata = ", mic_ydata)

# stop streams
output_stream.stop_stream()
output_stream.close()
input_stream.stop_stream()
input_stream.close()

# close PyAudio
p.terminate()
