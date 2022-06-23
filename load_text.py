import numpy as np
import matplotlib.pyplot as plt
import os, errno

# Script was written to plot information recorded by HWINFO64 if benchmarking computer

class loaded_text: # Generalized class to load txt files and store relevant data

	def __init__(self,filename):
		self.filename = filename
		# self.array = np.genfromtxt(filename, delimiter=',',names=True,skip_header=1,skip_footer=2,dtype=None)
		# for i in range(len(self.array)):
		# 	print(self.array[i])
		file = open(filename,"r")
		lines = file.readlines()
		self.headers = lines[0].split(",")
		self.footer1 = lines[-2].split(",")
		self.footer2 = lines[-1].split(",")
		lines = lines[1:-2]
		# self.array = [[] for _ in range(len(self.headers))]
		# for i in range(len(lines)):
		# 	for j in range(len(self.array)):
		# 		self.array[j].append(lines[i].split(",")[j])

		for i in range(len(lines)): # Handle reading dates and times
			lines[i] = lines[i].split(",")
			date_converter = lines[i][1].split(":")
			year_converter = lines[i][0].split(".")
			date_template = [2,2,6]
			year_template = [4,2,2]
			delimiter = [":",":",""]
			year_delimiter = ["-","-",""]
			date_new = ""
			year_new = ""
			for j in range(len(date_converter)):
				if len(date_converter[j]) < date_template[j]:
					date_converter[j] = "0"+date_converter[j]
				date_new += date_converter[j]+delimiter[j]
				if len(year_converter[-j-1]) < year_template[j]:
					year_converter[-j-1] = "0"+year_converter[-j-1] 
				year_new += year_converter[-j-1]+year_delimiter[j]
			lines[i][-1] = year_new+"T"+date_new

		#### WEIRD TROUBLESHOOTING ####
		# print(np.array(lines[:294])[-1,-1])
		# print(np.array(lines[294:])[0,-1])

		self.array = np.array(lines[100:])
		# print(self.array[:,-1])

		###############################

		# self.array = np.array(lines)
		
		# self.array = [[] for _ in range(len(self.headers))]
		# for line in file:
		# 	for i in range(len(self.headers)):
		# 		self.array[i].append(line.split(",")[i])

	def search(self,tag): # Find particular header and associated column. I forgot if numpy handles this natively or not
		tags = []
		for i in range(len(self.headers)):
			if tag in self.headers[i]:
				tags.append([self.headers[i],i])
		return tags

	def plot_xy(self,tag,x_column=-1,y_column=2,x_label="x",y_label="y"): # Plots any x vs. y and makes a png file based on filename
		tag_list = self.search(tag)
		if len(tag_list) != 1:
			print("Found 0 or 2+ results, please pick one:")
			for i in range(len(tag_list)):
				print(tag_list[i][0],end=" at column: ")
				print(tag_list[i][1])
			return
		else:
			y_column = tag_list[0][1]

		x_data = np.array(self.array[:,x_column],dtype='datetime64[ms]')
		y_data = self.array[:,y_column]

		x_label = self.headers[1]
		y_label = self.headers[y_column]

		fig = plt.figure()

		ax = fig.add_subplot(111)
		fig.subplots_adjust(top=0.85)


		ax.set_xlabel(r"{}".format(x_label))
		ax.set_ylabel(r"{}".format(y_label))

		plt.plot(x_data,y_data,linestyle="-",marker=".")
		plt.savefig(self.filename+'_xy.png')
		plt.close()

	def plot_xyy(self,x_column=0,y1_column=1,y2_column=2,x_label="x",y1_label="y1",y2_label="y2"): # Plots multiple y variables against x and makes a png file based on filename
		y1_data = self.array[:,y1_column]
		y2_data = self.array[:,y2_column]
		x_data = self.array[:,x_column]

		fig = plt.figure()

		ax = fig.add_subplot(111)
		fig.subplots_adjust(top=0.85)

		color = 'tab:blue'
		ax.set_xlabel(r"{}".format(x_label))
		ax.set_ylabel(r"{}".format(y1_label),color=color)
		ax.plot(x_data,y1_data,linestyle="",marker="o",color=color)
		ax.tick_params(axis='y', labelcolor=color)

		ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis

		color = 'tab:red'
		ax2.set_ylabel(r"{}".format(y2_label),color=color)  # we already handled the x-label with a
		ax2.plot(x_data,y2_data,linestyle="",marker="o",color=color)
		ax2.tick_params(axis='y', labelcolor=color)

		fig.tight_layout()  # otherwise the right y-label is slightly clipped

		plt.savefig(self.filename+'_xyy.png')
		plt.close()

	def plot_mobo_temps(self): # Plots voltage vs. voltage and makes a png file based on filename

		mobo_temperatures = [["System1 [°C]","Chipset [°C]", "VRM MOS [°C]", "VSOC MOS [°C]"], [79,80,83,84]]
		cpu_temperatures = [["Core 0 Clock (perf #3/3) [MHz]","Core 1 Clock (perf #4/6) [MHz]", "Core 2 Clock (perf #5/5) [MHz]", \
		"Core 3 Clock (perf #1/2) [MHz]"], [79,80,83,84]]

		x_raw = np.array(self.array[:,-1],dtype='datetime64[m]')
		x_data = [x_raw[i] - x_raw[0] for i in range(len(x_raw))]
		y_data = [ np.array(np.float16(self.array[:,i])) for i in mobo_temperatures[1]]

		x_label = self.headers[1]
		y_label = "Temperature [°C]"

		fig = plt.figure()

		ax = fig.add_subplot(111)
		# fig.subplots_adjust(top=0.85)

		ax.set_xlabel(r"{}".format(x_label))
		ax.set_ylabel(r"{}".format(y_label))
		axes = plt.gca()
		# axes.set_xlim([xmin,xmax])
		axes.set_ylim([25,70])

		for i in range(len(y_data)):
			# ax.set_ylim([25,80])
			plt.plot(x_data,y_data[i],linestyle="-",marker="",label=mobo_temperatures[0][i])
		ax.legend()
		plt.savefig(self.filename.split('.csv')[0]+'_mobo.png')
		plt.close()

	def plot_cpu_clock(self): # Plotting CPU clock speed

		mobo_temperatures = [["System1 [°C]","Chipset [°C]", "VRM MOS [°C]", "VSOC MOS [°C]"], [79,80,83,84]]
		cpu_freq = [["Core 0 T0 Effective Clock [MHz]","Core 0 T1 Effective Clock [MHz]", "Core 1 T0 Effective Clock [MHz]", \
		"Core 1 T1 Effective Clock [MHz]","Core 2 T0 Effective Clock [MHz]","Core 2 T1 Effective Clock [MHz]",\
		"Core 3 T0 Effective Clock [MHz]","Core 3 T1 Effective Clock [MHz]","Core 4 T0 Effective Clock [MHz]",\
		"Core 4 T1 Effective Clock [MHz]","Core 5 T0 Effective Clock [MHz]","Core 5 T1 Effective Clock [MHz]"],\
		 [22,23,24,25,26,27,28,29,30,31,32,33]]

		x_raw = np.array(self.array[:,-1],dtype='datetime64[m]')
		x_data = [x_raw[i] - x_raw[0] for i in range(len(x_raw))]
		y_data = [ np.array(np.float16(self.array[:,i])) for i in cpu_freq[1]]

		x_label = self.headers[1]
		y_label = "Frequency [MHz]"

		fig = plt.figure()

		ax = fig.add_subplot(111)
		# fig.subplots_adjust(top=0.85)

		ax.set_xlabel(r"{}".format(x_label))
		ax.set_ylabel(r"{}".format(y_label))
		axes = plt.gca()
		# axes.set_xlim([xmin,xmax])
		axes.set_ylim([500,4200])

		for i in range(len(y_data)):
			# ax.set_ylim([25,80])
			# plt.plot(x_data,y_data[i],linestyle="-",marker="",label=cpu_freq[0][i])
			plt.plot(x_data,y_data[i],linestyle="-",marker="")
		ax.legend()
		plt.savefig(self.filename.split('.csv')[0]+'_cpu.png')
		plt.close()


directory = "../HWiNFO/"

#hwinfo = loaded_text(directory+"HWiNFO_twogpu-intake.csv")
#hwinfo.plot_mobo_temps()
#hwinfo.plot_cpu_clock()
#print(hwinfo.search("[MHz]"))

# print(hwinfo.array)
# files=os.listdir(directory) # Lists all files in the current directory/flder

residual = loaded_text("residuals.csv")
print(residual.array)

# saving_fig = loaded_text(directory+files[0])
# saving_fig.plot_xy()
# saving_fig.plot_xyy()

# print(array)

# for i in range(len(files)):
# 	try:
# 		saving_fig = loaded_text(directory+files[i])
# 		saving_fig.plot_xy()
# 		saving_fig.plot_xyy()
# 	except ValueError:
# 		continue
