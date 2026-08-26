import argparse
import json
import gearman

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", default=None, help="ip to scan")
parser.add_argument("-s", "--signature", default=None, help="scan signature")
args = parser.parse_args()

jobSpecs = [args.ip,args.signature]

def malwareScan(jobSpecs):
	gearmanClient = gearman.GearmanClient(["SERVER:4735"])
	malwareJob = gearmanClient.submit_job('malware',json.dumps(jobSpecs),wait_until_complete=False)
	
malwareScan(jobSpecs)