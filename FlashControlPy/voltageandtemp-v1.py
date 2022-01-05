import webbrowser
import datetime
from tkinter import filedialog, scrolledtext

import nidaqmx
import pandas as pd
import pyvisa
import time
import matplotlib
from matplotlib import pyplot as plt

import os
from tkinter import *


def try_to_start():
    try:
        initialise()
    except Exception as ex:
        template = "Error: {0}. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        result.delete(0.0, END)
        result.insert(END, message)
    return


def freeze_acquisition():
    time.sleep(10)
    return


def run_all():
    global f
    try:
        notifications2()
        measure()
        notifications3()
    except Exception as ex:
        template2 = "Error: {0}. Arguments:\n{1!r}"
        message2 = template2.format(type(ex).__name__, ex.args)
        result.delete(0.0, END)
        result.insert(END, message2)
    return


def write_data():
    try_to_start()
    global f
    fname = output_filepath + "\\" + file_name + '.csv'
    f = open(fname, "w")
    f.write("Time" + '\t' + "Keithley_Voltage" + "\t" + "Source_Voltage" + "\t" + "Temperature" + "\n")
    # f.write("0" + '\t' + "0" + "\t" + "0" + "\t" + "0" + "\n")


def initialise():
    global voltage_scale, temperature_channel, voltage_channel, daq_max_voltage, output_filepath, file_name

    voltage_channel = str(volt_channel.get())
    temperature_channel = str(t_channel.get())
    PS_max_voltage = int(Supply_Voltage.get())
    daq_max_voltage = int(DAQ_Voltage.get())
    voltage_scale = PS_max_voltage / daq_max_voltage

    output_filepath = file_path
    file_name = str(file_name.get())


def notifications1():
    result.delete(0.0, END)
    result.insert(END, 'Start Acquisition?')
    return


def notifications2():
    result.delete(0.0, END)
    result.insert(END, 'Running')
    return


def notifications3():
    result.delete(0.0, END)
    result.insert(END, 'Data Saved!')
    return


def stop_running():
    try:
        f.close()
        exit()
    except Exception as ex:
        result.delete(0.0, END)
        result.insert(END, ex)
        window.destroy()

    return


def read_temperature():
    task = nidaqmx.Task()
    task.ai_channels.add_ai_voltage_chan(temperature_channel, min_val=0, max_val=daq_max_voltage)
    task.start()
    value = task.read()
    temperature = (value * 230) + 250

    # Terminate DAQ Device
    task.stop()
    task.close()

    return temperature


def read_voltage():
    task = nidaqmx.Task()
    task.ai_channels.add_ai_voltage_chan(voltage_channel, min_val=0, max_val=daq_max_voltage)
    task.start()
    raw_value = task.read()
    value = raw_value * voltage_scale

    # Terminate DAQ Device
    task.stop()
    task.close()

    return value


def screen_output(time_in, voltage1, voltage2, temp):
    time_output.delete(0, END)
    time_output.insert(END, str(round(time_in, 3)))
    voltage_output.delete(0, END)
    voltage_output.insert(END, str(round(voltage1, 5)))
    voltage2_output.delete(0, END)
    voltage2_output.insert(END, str(round(voltage2, 5)))
    temp_output.delete(0, END)
    temp_output.insert(END, str(round(temp, 3)))
    return


def measure():
    global timeList, Voltage1List, Voltage2List, TempList
    multimeter = pyvisa.ResourceManager().open_resource('GPIB0::1::INSTR', )
    multimeter.write(":ROUTe:CLOSe (@101)")
    multimeter.write(":SENSE:FUNCtion 'VOLTage'")
    print(multimeter.query(':SENSe:DATA:FRESh?'))

    timeList = []
    VoltageList = []
    Voltage2List = []
    TempList = []
    startTime = time.time()

    fig, axs = plt.subplots(2, sharex=True)
    fig.suptitle("Voltage and Temperature Profiles", fontsize=18)

    axs[0].set_ylabel("Voltage ($V$)", color='blue', fontsize=14)
    axs[0].tick_params(axis='y', labelcolor="blue")
    axs[1].set_xlabel("Time ($s$)", fontsize=14)
    axs[1].set_ylabel("Temperature (\N{DEGREE SIGN}C)", color='red', fontsize=14)
    axs[1].tick_params(axis='y', labelcolor="red")

    while True:
        VoltageReading = float(multimeter.query(':SENSE:DATA:FRESh?'))  # .split(',')[0][:-2])
        VoltageReading1 = abs(VoltageReading)
        VoltageList.append(VoltageReading1)
        timeList.append(float(time.time() - startTime))
        voltage_value = read_voltage()
        Voltage2List.append(voltage_value)
        temp_value = read_temperature()
        TempList.append(temp_value)
        time.sleep(0.01)
        screen_output(float(time.time() - startTime), (VoltageReading * 10 ** 3), voltage_value, temp_value)
        f.write(
            str(time.time() - startTime) + '\t' + str(VoltageReading1) + "\t" + str(abs(voltage_value)) + '\t' + str(
                temp_value) + "\n")
        axs[0].plot(timeList, VoltageList, color='blue', linewidth=3)
        axs[1].plot(timeList, TempList, color='red', linewidth=3)
        fig.tight_layout()
        plt.pause(0.01)
    return

    fig.close()


window = Tk()
window.geometry("400x500")

window.title("Acquisition |©Emmanuel Bamidele | 2021")
window.iconbitmap(
    r"C:\Users\AMI\Desktop\Emmanuel\Codes\Flash-Sintering-Software-Logo.ico")


def callback(url):
    webbrowser.open_new_tab(url)


Program_name1 = Label(window, font=('Verdana', 12, 'bold'), text='FLASH-ACQ-PY-v1.0', fg='blue')
Program_name1.place(relx=.02, rely=.005)

Program_info2 = Label(window, font=('Verdana', 7), text='Source Code', fg='blue', cursor="hand2")
Program_info2.place(relx=.8, rely=.01)
Program_info2.bind("<Button-2>", lambda e: callback("http://www.github.com/Rishi-Raj-Lab"))

# Input

column1_label = Label(window, text="Inputs", font=('Copperplate Gothic', 10, 'bold'))
column1_label.place(relx=.02, rely=.07)

channels_label = Label(window, text="Daq Channels", font=('Copperplate Gothic', 8), fg="red")
channels_label.place(relx=.02, rely=.11)

t_channel_label = Label(window, text="Temperature Channel", font=('Copperplate Gothic', 10))
t_channel_label.place(relx=.02, rely=.16)

t_channel = Entry(window)
t_channel.insert(END, 'Dev2/ai1')
t_channel.place(relx=.02, rely=.20)

volt_channel_label = Label(window, text="Voltage Channel", font=('Copperplate Gothic', 10))
volt_channel_label.place(relx=.02, rely=.25)

volt_channel = Entry(window)
volt_channel.insert(END, 'Dev2/ai0')
volt_channel.place(relx=.02, rely=.29)

dimension_label = Label(window, text="Dimension", font=('Copperplate Gothic', 8), fg="red")
dimension_label.place(relx=.02, rely=.33)

file_name_label = Label(window, text="File Name", font=('Copperplate Gothic', 10))
file_name_label.place(relx=.02, rely=.37)

file_name = Entry(window)
file_name.insert(END, datetime.datetime.now().strftime("%Y_%m_%d-%I-%M-%p-"))
file_name.place(relx=.02, rely=.42)

Supply_Voltage_label = Label(window, text="Peak Power Supply (V)", font=('Copperplate Gothic', 10))
Supply_Voltage_label.place(relx=.02, rely=.46)

Supply_Voltage = Entry(window)
Supply_Voltage.insert(END, '30')
Supply_Voltage.place(relx=.02, rely=.51)

DAQ_Voltage_label = Label(window, text="Max DAQ Voltage", font=('Copperplate Gothic', 10))
DAQ_Voltage_label.place(relx=.02, rely=.55)

DAQ_Voltage = Entry(window)
DAQ_Voltage.insert(END, '5')
DAQ_Voltage.place(relx=.02, rely=.60)

# Output

column2_label = Label(window, text="Outputs", font=('Copperplate Gothic', 10, 'bold'))
column2_label.place(relx=.6, rely=.07)

time_output_label = Label(window, text="Time (s)", font=('Copperplate Gothic', 10))
time_output_label.place(relx=.6, rely=.16)

time_output = Entry(window, fg='red')
time_output.insert(END, "0.00")
time_output.place(relx=.6, rely=.21)

voltage_output_label = Label(window, text="Keithley Voltage (mV)", font=('Copperplate Gothic', 10))
voltage_output_label.place(relx=.6, rely=.25)

voltage_output = Entry(window, fg='red')
voltage_output.insert(END, "0.00")
voltage_output.place(relx=.6, rely=.29)

voltage2_output_label = Label(window, text="Source Voltage", font=('Copperplate Gothic', 10))
voltage2_output_label.place(relx=.6, rely=.33)

voltage2_output = Entry(window, fg='red')
voltage2_output.insert(END, "0.00")
voltage2_output.place(relx=.6, rely=.38)

temp_output_label = Label(window, text="Temperature (\N{DEGREE SIGN}C)", font=('Copperplate Gothic', 10))
temp_output_label.place(relx=.6, rely=.42)

temp_output = Entry(window, fg='red')
temp_output.insert(END, "250")
temp_output.place(relx=.6, rely=.47)

Start_Acquisition = Button(window, text="Start Acquisition", command=run_all, bg="green",
                           fg='white')  # link this to the function
Start_Acquisition.place(relx=.10, rely=.68)

Pause_Acquisition = Button(window, text="Freeze (10s)", command=freeze_acquisition,
                           bg='#E39E7F', fg='black')  # link this to the function
Pause_Acquisition.place(relx=.41, rely=.68)

Stop_Acquisition = Button(window, text="Close Acquisition", command=stop_running,
                          bg='red', fg='white')  # link this to the function
Stop_Acquisition.place(relx=.65, rely=.68)

# Display section

result = scrolledtext.ScrolledText(window, height=5, width=45, wrap=WORD, fg="red")
notifications1()
result.place(relx=.02, rely=.75)

file_path = filedialog.askdirectory()
write_data()

window.mainloop()
