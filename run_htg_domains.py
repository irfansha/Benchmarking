# Irfansha Shaik, 27.02.2022, Aarhus.

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
  text = "Generates and dispatches batch jobs for various domains and parameter sweep"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--nodes", help="no of nodes", default = '1')
  parser.add_argument("--mem", help="mem in GB, default 0 i.e. all of it", default = '0')
  parser.add_argument("--time", help="estimated time in hours", default = '7')
  parser.add_argument("--mail_type", help="mail type", default = 'END')
  parser.add_argument("--mail_user", help="mail", default = 'irfansha.shaik@cs.au.dk')
  parser.add_argument("--input_dir", help="directory path for input files")
  parser.add_argument("--output_dir", help="directory path for output files")

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
      f = open("run_" + domain_path.replace("/", "_") + "_" + file_name + ".sh", "w")

      print(domain_path)

      f.write("#!/bin/bash\n")
      f.write("#SBATCH --partition=" + args.partition + "\n")
      f.write("#SBATCH --nodes=" + args.nodes + "\n")
      f.write("#SBATCH --mem=" + args.mem + "\n")
      # Exclusive flag:
      f.write("#SBATCH --exclusive\n")
      f.write("#SBATCH --time=" + args.time + ":00:00" + "\n")
      f.write("#SBATCH --mail-type=" + args.mail_type + "\n")
      f.write("#SBATCH --mail-user=" + args.mail_user + "\n\n")

      f.write("echo '========= Job started  at `date` =========='\n\n")

      f.write("cd $SLURM_SUBMIT_DIR\n\n")

      default_file_names = ' --encoding_out /scratch/$SLURM_JOB_ID/encoding_$SLURM_JOB_ID --preprocessed_encoding_out /scratch/$SLURM_JOB_ID/preprocessed_$SLURM_JOB_ID --intermediate_encoding_out /scratch/$SLURM_JOB_ID/intermediate_encoding_$SLURM_JOB_ID --solver_out /scratch/$SLURM_JOB_ID/solver_out_$SLURM_JOB_ID --plan_out /scratch/$SLURM_JOB_ID/plan_$SLURM_JOB_ID '

      options = " --single_instance_run 1 -e s-UE --preprocessing bloqqer-qdo --solver caqe --planner_path Q-Planner --time_limit 10800 --step 5 > "

      f.write("time python3 run_benchmarks.py --path " + os.path.join(args.input_dir,domain_path) + " --problem_name " + file_name + " " + default_file_names + options + args.output_dir + "/out_" + domain_path.replace("/", "_") + "_" +file_name  + "_$SLURM_JOB_ID\n")

      command = 'sbatch run_' + domain_path.replace("/", "_") + "_" + file_name + ".sh"



      f.write("\necho '========= Job finished at `date` =========='\n")
      #f.write("\nrm ./intermediate_files/* \n")
      f.close()


      print(command)
      #os.popen(command)
