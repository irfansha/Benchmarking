# Irfansha Shaik, 28.02.2022, Aarhus.

'''
Dispatches batch jobs of state-of-the-art grounded planners on hard-to-ground benchmarks
'''

import argparse
import glob
import os
import re
import textwrap
from pathlib import Path


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


# Main:
if __name__ == '__main__':
  text = "Generates and dispatches batch jobs for various domains and parameter sweep with SOA planners"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--nodes", help="no of nodes", default = '1')
  parser.add_argument("--mem", help="mem in GB, default 0 i.e. all of it", default = '0')
  parser.add_argument("--time", help="estimated time in hours", default = '3')
  parser.add_argument("--mail_type", help="mail type", default = 'END')
  parser.add_argument("--mail_user", help="mail", default = 'irfansha.shaik@cs.au.dk')
  parser.add_argument("--input_dir", help="directory path for input files")
  parser.add_argument("--output_dir", help="directory path for output files", default = 'out_data/')
  parser.add_argument("--planner", help=textwrap.dedent('''
                                  Planners:
                                  M = madagascar
                                  FDS  = Fast Downward soup 18
                                  PL  = Powerlifted'''))


  args = parser.parse_args()


  domain_paths = ["blocksworld-large-simple", "childsnack-contents/parsize1", "childsnack-contents/parsize2",
                   "childsnack-contents/parsize3", "childsnack-contents/parsize4" , "genome-edit-distance",
                  "logistics-large-simple", "pipesworld-notankage-nosplit", "visitall-multidimensional/3-dim-visitall",
                  "visitall-multidimensional/5-dim-visitall","visitall-multidimensional/5-dim-visitall"]


  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)

  for domain_path in domain_paths:
    files_list = glob.glob(os.path.join(args.input_dir, domain_path ,"*"))
    files_list.sort(key=natural_keys)

    for file_path in files_list:
      if ('domain' in file_path):
        path, domain_name = os.path.split(file_path)
        print(path, domain_name)
        break

    for file_path in files_list:
      if ('domain' not in file_path and '.py' not in file_path):
        path, file_name = os.path.split(file_path)
        print(path, file_name)
      else:
        continue

      # Generate batch script:
      f = open("run_" + args.planner + "_"+ domain_path.replace("/", "_") + "_" + file_name + ".sh", "w")

      print(domain_path)

      f.write("#!/bin/bash\n")
      f.write("#SBATCH --partition=" + args.partition + "\n")
      f.write("#SBATCH --nodes=" + args.nodes + "\n")
      f.write("#SBATCH --mem=" + args.mem + "\n")
      # Exclusive flag:
      f.write("#SBATCH --exclusive\n")
      f.write("#SBATCH --time=" + args.time + ":02:00" + "\n")
      f.write("#SBATCH --mail-type=" + args.mail_type + "\n")
      f.write("#SBATCH --mail-user=" + args.mail_user + "\n\n")

      f.write("echo '========= Job started  at `date` =========='\n\n")

      f.write("cd $SLURM_SUBMIT_DIR\n\n")

      if (args.planner == 'FDS'):
        options = " --alias seq-sat-fdss-1   --overall-time-limit 10800s --overall-memory-limit 300g --portfolio-single-plan --sas-file /scratch/$SLURM_JOB_ID/plan_$SLURM_JOB_ID "
        f.write("time python3 downward/fast-downward.py " + options + os.path.join(path, domain_name) + " " + os.path.join(path, file_name) + " > "+ args.output_dir + "out_" + domain_name + "_$SLURM_JOB_ID\n")

      elif (args.planner == 'M'):
        options = " -t 10800 -m 300000 -M 1 "
        f.write("time ./tools/M " + options + os.path.join(path, domain_name) + " " + os.path.join(path, file_name) + " > "+ args.output_dir + "out_" + domain_name + "_$SLURM_JOB_ID\n")

      elif (args.planner == 'PL'):
        options = " -s lazy-po -e add -g yannakakis --translator-output-file /scratch/$SLURM_JOB_ID/translator_$SLURM_JOB_ID --datalog-file /scratch/$SLURM_JOB_ID/datalog_$SLURM_JOB_ID"
        f.write("time ./powerlifted.py -d " + os.path.join(path, domain_name) + " -i " + os.path.join(path, file_name) + " " + options + " > "+ args.output_dir + "out_" + domain_name + "_$SLURM_JOB_ID\n")

      command = 'sbatch run_' + args.planner + "_" + domain_path.replace("/", "_") + "_" + file_name + ".sh"



      f.write("\necho '========= Job finished at `date` =========='\n")
      #f.write("\nrm ./intermediate_files/* \n")
      f.close()


      print(command)
      #os.popen(command)
