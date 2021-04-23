# Irfansha Shaik, 19.04.2021, Aarhus.

import os
from pathlib import Path
import argparse

# Main:
if __name__ == '__main__':
  text = "Generates and dispatches batch jobs for various domains and parameter sweep"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--nodes", help="no of nodes", default = '1')
  parser.add_argument("--mem", help="mem in GB, default 0 i.e. all of it", default = '0')
  parser.add_argument("--time", help="estimated time in hours", default = '24')
  parser.add_argument("--single_time_limit", help="time limit for single instance in seconds, default 1800", default = '1800')
  parser.add_argument("--mail_type", help="mail type", default = 'END')
  parser.add_argument("--mail_user", help="mail", default = 'irfansha.shaik@cs.au.dk')
  parser.add_argument("--typed", type =int, help=" typed/untyped domains [1/0] default 1", default = 1)
  parser.add_argument("--input_dir", help="directory path for input files", default = 'input_data')
  parser.add_argument("--output_dir", help="directory path for output files")
  args = parser.parse_args()

  if (args.typed == 1):
    test_domains = ["Blocks", "DriverLog", "Elevator",
                     "Hiking", "SATELLITE", "termes-opt18",
                    "Thoughtful", "tidybot-opt11-strips",
                    "visitall-opt11-strips"]
  else:
    test_domains = ["grid", "logistics00", "mystery",
                    "blocks-3op", "gripper",
                    "depot/", "freecell/", "movie/", "mprime/"]


  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)

  encoding_variants = ["sc_UE_pre"]

  for encoding in encoding_variants:
    for domain_name in test_domains:
      # Generate batch script:
      f = open("run_" + domain_name + "_" + encoding + ".sh", "w")

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
      f.write("echo 'Domain name: " + str(domain_name) + " Encoding type: " + str(encoding) + "'\n\n")

      f.write("cd $SLURM_SUBMIT_DIR\n\n")

      default_file_names = ' --encoding_out /scratch/$SLURM_JOB_ID/encoding_$SLURM_JOB_ID --preprocessed_encoding_out /scratch/$SLURM_JOB_ID/preprocessed_$SLURM_JOB_ID --intermediate_encoding_out /scratch/$SLURM_JOB_ID/intermediate_encoding_$SLURM_JOB_ID --solver_out /scratch/$SLURM_JOB_ID/solver_out_$SLURM_JOB_ID --plan_out /scratch/$SLURM_JOB_ID/plan_$SLURM_JOB_ID '

      if (encoding == 's_UE_pre'):
        options = " -e s-UE --preprocessing 2 --planner_path Q-Planner --time_limit " + str(args.single_time_limit) + " > "
      if (encoding == 'sc_UE_pre'):
        options = " -e sc-UE --preprocessing 2 --planner_path Q-Planner --time_limit " + str(args.single_time_limit) + " > "

      # Updating the path for specific domain:
      cur_domain_path = os.path.join(args.input_dir, domain_name)
      f.write("time python3 run_benchmarks.py --path " + cur_domain_path + " " + default_file_names + options + args.output_dir + "/out_" + domain_name + "_$SLURM_JOB_ID\n")
      command = 'sbatch run_' + domain_name + "_" + encoding + ".sh"



      f.write("\necho '========= Job finished at `date` =========='\n")
      #f.write("\nrm ./intermediate_files/* \n")
      f.close()


      print(command)
      #os.popen(command)