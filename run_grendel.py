# Irfansha Shaik, 19.04.2021, Aarhus.

import os
from pathlib import Path
import argparse

# Main:
if __name__ == '__main__':
  text = "Generates and dispatches batch jobs for various domains and parameter sweep"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--mem", help="mem in GB, default 16 gb", default = '16')
  parser.add_argument("--time", help="estimated time in hours", default = '24')
  parser.add_argument("--mail_type", help="mail type", default = 'END')
  parser.add_argument("--mail_user", help="mail", default = 'irfansha.shaik@cs.au.dk')
  parser.add_argument("--typed", type =int, help=" typed/untyped domains [1/0] default 1", default = 1)
  parser.add_argument("--input_dir", help="directory path for input files", default = 'input_data')
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


  encoding_variants = ["s_UE_pre"]

  for encoding in encoding_variants:
    for domain_name in test_domains:

      # Generate batch script:
      f = open("run_" + encoding + "_" + domain_name + ".sh", "w")

      f.write("#!/bin/bash\n")
      f.write("#SBATCH --partition=" + args.partition + "\n")
      f.write("#SBATCH --mem=" + args.mem + "\n")
      f.write("#SBATCH --ntasks=1\n")
      f.write("#SBATCH --ntasks-per-node=1\n")
      f.write("#SBATCH --cpus-per-task=5\n")
      f.write("#SBATCH --time=" + args.time + ":00:00" + "\n")
      f.write("#SBATCH --mail-type=" + args.mail_type + "\n")
      f.write("#SBATCH --mail-user=" + args.mail_user + "\n\n")

      f.write("echo '========= Job started  at `date` =========='\n\n")

      # Go to the directory where this job was submitted
      f.write("cd $SLURM_SUBMIT_DIR\n\n")

      # copy inputdata and the executable to the scratch-directory
      f.write("cp * /scratch/$SLURM_JOB_ID\n\n")

      # change directory to the local scratch-directory, and run:
      f.write("cd /scratch/$SLURM_JOB_ID\n\n")
      f.write("export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}\n\n")

      if(encoding == 's_UE'):
        if (args.ue == 0):
          options = " -e s-UE "
      elif(encoding == 's_UE_pre'):
          options = " -e s-UE --preprocessing 2 --planner_path Q-Planner"

      # Updating the path for specific domain:
      cur_domain_path = os.path.join(args.input_dir, domain_name)

      f.write("time python3 run_benchmarks.py --path " + cur_domain_path + options + " --time_limit 1800 > out\n\n")

      # copy home the outputdata:
      f.write("cp out $SLURM_SUBMIT_DIR/out.$SLURM_JOB_ID\n\n")

      command = 'sbatch run_' + encoding + "_" + domain_name + ".sh"



      f.write("\necho '========= Job finished at `date` =========='\n")
      #f.write("\nrm ./intermediate_files/* \n")
      f.close()


      print(command)
      #os.popen(command)