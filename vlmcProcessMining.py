import numpy as np
import argparse
import os
import subprocess
import sys
import json
import re
from scipy.io import savemat
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
import pathlib
import shutil
import tqdm
import time
import glob

import warnings
import xml.parsers.expat
import warnings
from pm4py.objects.log.importer.xes import importer as xes_importer
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
from pm4py.statistics.variants.log import get as variants_module
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
import gzip
import tempfile
import atexit

temp_dir=None
ldir=pathlib.Path(__file__).parent/pathlib.Path("likelyhood")
	
def processData(inputFile,idCol=None,activityCol=None):
	print(f"processData {inputFile}")
	proc=pd.read_csv(inputFile)
	cIds=list(dict.fromkeys(proc[idCol]))
	
	cTrace=None
	for cId in tqdm.tqdm(cIds):
		trace=proc[proc[idCol]==cId][activityCol].to_list()
		
		if(len(trace)>0):
			t="!$"
			for smb in trace:
				t+=" "+re.sub(r"\s+", "", smb)+"$"
			t+=" end$"

			if(cTrace is None):
				cTrace=t
			else:
				cTrace+=" "+t

			if(len(trace)!=len(t.split(" "))-2 or len(t.split(" "))==2):
				raise ValueError(f"error while converting trace {t}, {trace}")

	traceFilePath=os.path.join("data", "converted", "%s.txt" % (pathlib.Path(inputFile).name.split(".")[0]))
	print(len(cIds))
	outfile = open(traceFilePath, "w+")
	outfile.write(cTrace)
	outfile.close()

	# Creazione della directory di lavoro e calcolo della likelihood
	cwd = (ldir/pathlib.Path(inputFile).name.split(".")[0])
	cwd.mkdir(parents=True, exist_ok=True)
	computeLikelyhoodTrace(inputTrace=cTrace.strip(),
						  name=pathlib.Path(inputFile).name.split(".")[0],
						  cwd=str(cwd.absolute()))

	return traceFilePath

def computeLikelyhoodTrace(inputTrace=None,name="data",cwd="."):
	N=len(inputTrace.split("!$ "))-1
	L=stochLanguage(trace=inputTrace)
	lik=[[f"{np.round(float(inputTrace.count(l))/N,6)},{len(l.split(' '))-1}"] for l in L ]
	
	#likelyhoo and stochastic language of trances
	lik_outpath=pathlib.Path(cwd).absolute()/pathlib.Path(f"{name}_trace.lik")
	lan_outpath=pathlib.Path(cwd).absolute()/pathlib.Path(f"{name}_trace.lan")
	np.savetxt(str(lik_outpath),lik,fmt="%s")
	np.savetxt(str(lan_outpath),[" ".join(L)],fmt="%s")


def processDCDTData(inputFile):
	inputFile=pathlib.Path(inputFile)
	inf=open(inputFile,"r")
	traces=inf.readlines()
	inf.close()
	
	lin_trace=""
	for t in traces:
		if(lin_trace==""):
			lin_trace=t.replace(",,"," ").strip()
		else:
			lin_trace+=" "+t.replace(",,"," ").strip()
	
	
	outfile = open(os.path.join("data", "converted", "%s.txt" % (inputFile.name.split(".")[0])), "w+")
	outfile.write(lin_trace)
	outfile.close()
	
	
	
def mineProcess(ecfFile=None, outFile="out.mat", infile=None, vlmcfile=None, nsim="0", ntime="1", alfa=None):
	# print("\n=== mineProcess Execution Details ===")
	# print(f"Input Parameters:")
	# print(f"  - ECF File: {ecfFile}")
	# print(f"  - Output File: {outFile}")
	# print(f"  - Input File: {infile}")
	# print(f"  - VLMC File: {vlmcfile}")
	# print(f"  - Number of Simulations: {nsim}")
	# print(f"  - Number of Time Steps: {ntime}")
	# print(f"  - Alpha: {alfa}")
	
	jar_path = os.path.join('scripts', 'jfitVlmc.jar')
	print(f"\nJAR File Path: {jar_path}")
	
	cmd = ['java', "-Xmx10g", '-jar', jar_path,
		   "--ecf", ecfFile, "--outfile", outFile,
		   "--infile", infile, "--vlmcfile", vlmcfile,
		   "--nsim", nsim, "--ntime", ntime, "--alfa", alfa]
	
	# print("\nFull Command:")
	# print("  " + " ".join(cmd))
	# print("=" * 50 + "\n")
	
	try:
		result = subprocess.run(cmd,
							   capture_output=True, text=True)
		
		# Print stdout if there is any
		# if result.stdout:
		# 	print("Command Output:")
		# 	print(result.stdout)
			
		# Print stderr if there is any
		if result.stderr:
			print("Error Output:")
			print(result.stderr)
			
		# Check if the command was successful
		if result.returncode != 0:
			raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
			
	except subprocess.CalledProcessError as e:
		print(f"\nError executing mineProcess: Command failed with return code {e.returncode}")
		print(f"Command that failed: {' '.join(e.cmd)}")
		if e.stdout:
			print(f"Standard output: {e.stdout}")
		if e.stderr:
			print(f"Error output: {e.stderr}")
		raise
	except FileNotFoundError as e:
		print(f"\nError: Required file not found. Check if jfitVlmc.jar exists in scripts directory")
		raise
	except Exception as e:
		print(f"\nUnexpected error in mineProcess: {str(e)}")
		raise


def getLikelyhood(ecfFile=None, outFile="out.mat", infile=None, vlmcfile=None, nsim="1", ntime="1", alfa=None,
				  traces=None, vlmc=None, cwd="."):
	try:
		result = subprocess.run(['java', '-jar', (pathlib.Path(__file__).parent/pathlib.Path('scripts/jfitVlmc.jar')).absolute(),
							   "--ecf", ecfFile, "--outfile", outFile,
							   "--infile", infile, "--vlmcfile", vlmcfile,
							   "--nsim", nsim, "--ntime", ntime, "--alfa", alfa,
							   "--vlmc", vlmc, "--lik", traces],
							   capture_output=True, text=True, cwd=cwd)
		
		# Print stdout if there is any
		if result.stdout:
			print("Output:", result.stdout)
			
		# Print stderr if there is any
		if result.stderr:
			print("Error output:", result.stderr)
			
		# Check if the command was successful
		if result.returncode != 0:
			raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
			
	except subprocess.CalledProcessError as e:
		print(f"Error executing getLikelyhood: Command failed with return code {e.returncode}")
		print(f"Command that failed: {' '.join(e.cmd)}")
		if e.stdout:
			print(f"Standard output: {e.stdout}")
		if e.stderr:
			print(f"Error output: {e.stderr}")
		raise
	except FileNotFoundError as e:
		print(f"Error: Required file not found. Check if jfitVlmc.jar exists in scripts directory")
		raise
	except Exception as e:
		print(f"Unexpected error in getLikelyhood: {str(e)}")
		raise


def convertTrace(inputFile, outputFile):
	print(f"convert trace {inputFile} {outputFile}")
	try:
		result = subprocess.run(["java", "-Xmx5g", "-jar", "%s" % (os.path.join('scripts', 'trace2ecf.jar')),
							   "--ecfInDir", inputFile,
							   "--ecfOutDir", outputFile],
							   capture_output=True, text=True)
		
		# Print stdout if there is any
		if result.stdout:
			print("Output:", result.stdout)
			
		# Print stderr if there is any
		if result.stderr:
			print("Error output:", result.stderr)
			
		# Check if the command was successful
		if result.returncode != 0:
			raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
			
	except subprocess.CalledProcessError as e:
		print(f"Error executing convertTrace: Command failed with return code {e.returncode}")
		print(f"Command that failed: {' '.join(e.cmd)}")
		if e.stdout:
			print(f"Standard output: {e.stdout}")
		if e.stderr:
			print(f"Error output: {e.stderr}")
		raise
	except FileNotFoundError as e:
		print(f"Error: Required file not found. Check if trace2ecf.jar exists in scripts directory")
		raise
	except Exception as e:
		print(f"Unexpected error in convertTrace: {str(e)}")
		raise

	
def getPatientTrace(fileData):
	fid = open(fileData, "r");
	trace = fid.read();
	return trace

def stochLanguage(trace=None):
	matches = map(str.strip,re.findall(r'!\$ .*? end\$', trace))
	L=list(dict.fromkeys(matches))
	return L

	
def conformance(vlmc=None, traces=None, expName="conformance"):
	lik = None
	getLikelyhood(ecfFile=os.path.join("data", "VLMC",
									   "%s.ecf" % (vlmc)),
									   infile=os.path.join("data", "converted", "%s.txt" % (vlmc)),
				vlmcfile=os.path.join("data", "VLMC", "%s_2.vlmc" % (vlmc)),
				traces=traces,
				alfa="1.0", vlmc=os.path.join("data", "VLMC", "%s.vlmc" % (vlmc)))
	if(lik is None):
		lik = np.loadtxt("%s.vlmc.lik" % (vlmc), delimiter=",")
	else:
		lik = np.concatenate((lik, np.loadtxt("%s.vlmc.lik" % (vlmc), delimiter=",")), 1);

# Register cleanup for when the process ends
def cleanup():
	global temp_dir
	print(f"Cleaning up temporary directory: {temp_dir.name}")
	temp_dir.cleanup()

def processGzXes(gzXesfile=None):
	global temp_dir
	# Create a temporary directory
	temp_dir = tempfile.TemporaryDirectory()
	atexit.register(cleanup)

	# Specify the output file path in the temporary directory
	extracted_file_path = os.path.join(temp_dir.name, ".".join(gzXesfile.name.split(".")[0:-1]))

	# Open and extract the .gz file
	with gzip.open(gzXesfile, 'rb') as gz_file:
		with open(extracted_file_path, 'wb') as extracted_file:
			extracted_file.write(gz_file.read())

	print(f".gz file extracted to: {extracted_file_path}")

	return extracted_file_path

def processXesFile(inputFile=None,idCol=None,activityCol=None,timestapCol=None):
	# Perform operations on the extracted file
	log = pm4py.read_xes(str(inputFile))

	log['case:concept:name'] = log['case:concept:name'].astype(str)
	log['concept:name']      = log['concept:name'].astype(str)

	if(timestapCol in log.columns):
		log['time:timestamp'] = pd.to_datetime(log['time:timestamp'], format="%Y-%m-%dT%H:%M:%S", utc=True)
		# Sort the DataFrame by 'time:timestamp' in ascending order
		log=log.sort_values(by=timestapCol, ascending=True)

	#converting traces to vlmc input format
	cTrace=None
	for case_id, group in tqdm.tqdm(log.groupby(f'{idCol}')):
		trace = group[activityCol].tolist()
		#trace=log[log[idCol]==cId][activityCol].to_list()
		if(len(trace)>0):
			t="!$"
			for smb in trace:
				t+=" "+re.sub(r"[\s_&$(){}\[\]\-\+\.;']+", "", smb) + "$"
			t+=" end$"

			if(cTrace is None):
				cTrace=t
			else:
				cTrace+=" "+t

			if(len(trace)!=len(t.split(" "))-2 or len(t.split(" "))==2):
				raise ValueError(f"error while converting trace {t}, {trace}")
	
	print(f"Number of cases:{len(cTrace.split('!$ '))-1}")

	traceFilePath=os.path.join("data", "converted", f"{'.'.join(inputFile.name.split('.')[0:-1])}.txt")
	outfile = open(traceFilePath, "w+")
	outfile.write(cTrace)
	outfile.close()

	cwd=(ldir/pathlib.Path(inputFile.name.split(".")[0]))
	cwd.mkdir(parents=True, exist_ok=True)
	computeLikelyhoodTrace(inputTrace=cTrace.strip(),
						   name=".".join(inputFile.name.split(".")[0:-1]),
						   cwd=str(cwd.absolute()))

	return traceFilePath

def computeMuEMSC(traceLik,modelLik):	
	data_types = {'lik': float, 'len': int}
	tl=pd.read_csv(str(traceLik),header=None, names=["lik","len"],dtype=data_types)
	ml=pd.read_csv(str(modelLik),header=None, names=["lik","len"],dtype=data_types)

	muemsc=1-np.sum(np.maximum(np.round(tl["lik"],6)-np.round(ml["lik"],6),0))

	return muemsc



def readInputFile(inputFile):
	iPath=pathlib.Path(inputFile)
	if(not iPath.is_file()):
			raise ValueError(f"{iPath} is not a valid file!")
	print(iPath)
	ext=iPath.suffix

	while True:
		if(ext==".csv"):
			# Read the CSV file to check for required columns
			df = pd.read_csv(inputFile)
			required_columns = ["case:concept:name", "concept:name"]
			missing_columns = [col for col in required_columns if col not in df.columns]
			if missing_columns:
				raise ValueError(f"Missing required columns in CSV file: {', '.join(missing_columns)}")
			iPath=pathlib.Path(processData(inputFile,idCol="case:concept:name",activityCol="concept:name"))
			break
		elif(ext==".dcdt"):
			processDCDTData(inputFile)
			break
		elif(ext==".txt"):
			shutil.copy(iPath, pathlib.Path(f"{pathlib.Path(__file__).parent}/data/converted/"))
			break
		elif(ext==".xes"):
			iPath=pathlib.Path(processXesFile(iPath,idCol="case:concept:name",activityCol="concept:name",timestapCol="time:timestamp"))
			break
		elif(ext==".gz"):
			iPath=pathlib.Path(processGzXes(gzXesfile=iPath))
			if(not iPath.is_file()):
				raise ValueError(f"{iPath} is not a valid file!")
			ext=iPath.suffix
		else:
			raise ValueError(f"File extension {ext} not supported")
	
	outputFile=f"{pathlib.Path(__file__).parent}/data/VLMC/{'.'.join(iPath.name.split('.')[0:-1])}.ecf"
	convertTrace(inputFile=iPath, outputFile=outputFile)
	

parser = argparse.ArgumentParser(description='Mine a stochastic process from traces')
parser.add_argument('--inputFile', type=str, required=True, help='file  to convert', action="store")
parser.add_argument('--name', required=False, help='specify the name of the exeperiment', action="store")
parser.add_argument('--muemsc', required=False, help='specify to compute the muEMSC', action="store_true")
parser.add_argument('--con', required=False, help='specify to compute conformance ', action="store_true")
parser.add_argument('--mine', required=False, help='specify to compute conformance ', action="store_true")
parser.add_argument('--testset', required=False, help='test set to evaluate', type=str)
parser.add_argument('--inputVLMC', type=str, required=False, help='Name of VLMC to use for analysis', action="store")


if __name__ == '__main__':
	args = parser.parse_args()

	expName = args.name;
	if(args.mine):
		readInputFile(args.inputFile)
		vlmcName='.'.join(pathlib.Path(args.inputFile).name.split('.')[0:-1])
		print(vlmcName)
		mineProcess(ecfFile=f"{pathlib.Path(__file__).parent}/data/VLMC/{vlmcName}.ecf",
		 infile=f"{pathlib.Path(__file__).parent}/data/converted/{vlmcName}.txt",
		 vlmcfile=f"{pathlib.Path(__file__).parent}/data/VLMC/{vlmcName}.vlmc", 
		 nsim="1", ntime="1", alfa="1")
	elif(args.muemsc):
		vlmcName=args.inputVLMC
		if(vlmcName is None):
			raise ValueError(f"For computing muemsc args inputVLMC is required")
		tracefile=pathlib.Path(args.inputFile).absolute()
		if(not tracefile.is_file()):
			raise ValueError(f"inputFile {tracefile} not Found")
		if(not tracefile.suffix==".lan"):
			raise ValueError(f"inputFile {tracefile} should be .lan file")

		ecfFile=pathlib.Path(f"{pathlib.Path(__file__).parent}/data/VLMC/{vlmcName}.ecf").absolute()
		infile=pathlib.Path(f"{pathlib.Path(__file__).parent}/data/converted/{vlmcName}.txt").absolute()
		vlmcfile=pathlib.Path(f"{pathlib.Path(__file__).parent}/data/VLMC/{vlmcName}2.vlmc").absolute()
		vlmc=pathlib.Path(f"{pathlib.Path(__file__).parent}/data/VLMC/{vlmcName}.vlmc").absolute()
		
		cwd=(ldir/pathlib.Path(tracefile.name.split(".")[0]))
		cwd.mkdir(parents=True, exist_ok=True)

		getLikelyhood(
					ecfFile=str(ecfFile),
					infile=str(infile), #dataset used to learn the vlmc
					vlmc=str(vlmc), #input VLMC to use
					vlmcfile=str(vlmcfile),  #output VLMC
					traces=str(tracefile), #traces to compute likelyhood
					cwd=str(cwd),
					outFile="out.mat",nsim="1", ntime="1",alfa="1")

		traceLikName=".".join(tracefile.name.split(".")[0:-1])+".lik"
		traceLikFile=cwd/pathlib.Path(traceLikName)

		modelLikName=vlmc.name+".lik"
		modelLikFile=cwd/pathlib.Path(modelLikName)

		print(traceLikFile,modelLikFile)

		uEMSC=computeMuEMSC(traceLik=traceLikFile,modelLik=modelLikFile)
		print(uEMSC)


	elif(args.con):
		if(args.inputVLMC is None):
			raise ValueError("For conformance checking you need to specify an already learned VLMC")
		if(not pathlib.Path(f"./data/VLMC/{args.inputVLMC}.vlmc").exists()):
			raise ValueError("Vlmc does not exists")
		conformance(vlmc=args.inputVLMC, traces=args.testset, expName="conformance")      

#sh comte_uemsc_vlmc.sh  /home/root/SSSA_IMT/data/sldpn-reproducibility/experiments/2-splitlogs/Road_Traffic_Fine_Management_Process.xes.gz2.xes.gz /home/root/SSSA_IMT/data/sldpn-reproducibility/experiments/2-splitlogstest/Road_Traffic_Fine_Management_Process.xes.gz2_test.xes.gz Road_Traffic_Fine_Management_Process.xes.gz2 /home/root/SSSA_IMT/likelyhood/Road_Traffic_Fine_Management_Process/Road_Traffic_Fine_Management_Process.xes.gz2_test_trace.lan


