# Irfansha Shaik, 18.04.2021, Aarhus.

import argparse
import glob
import os
import re
import textwrap
from pathlib import Path
from resource import *


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def run_instance(domain_file, problem_file, args, iteration):
    print("---------------------------------------------------------------------------------------------")
    print("Running " + problem_file + ", iteration " + str(iteration+1))
    print("---------------------------------------------------------------------------------------------")
    k = 0
    remaining_time = args.time_limit
    while(1):
      # Handing testcases with no solution:
      if (k >= 500):
        print("Large K\n")
        break
      k = k + args.step
      file_name = problem_file.strip(".pddl")

      planner_command_path = os.path.join(args.planner_path, 'qplanner.py')

      # domain and problem files are new:
      command = 'python3 ' + planner_command_path + ' --path ' + args.path + \
                ' --domain ' + domain_file + ' --problem ' + problem_file + \
                ' --planner_path ' + args.planner_path + ' --ignore_noop ' + str(args.ignore_noop) + \
                ' --restricted_forall ' + str(args.restricted_forall) + \
                ' -e ' + args.e + ' --run ' + str(args.run) + ' --plan_length ' + str(k) + \
                ' --val_testing ' + str(args.val_testing) + ' --time_limit ' + str(remaining_time) + \
                ' --preprocessing ' + str(args.preprocessing) + ' --solver ' + str(args.solver) + \
                ' --encoding_out ' + args.encoding_out + "_" + file_name + "_" + str(k) + \
                ' --preprocessed_encoding_out ' + args.preprocessed_encoding_out + "_" + file_name + "_" + str(k) + \
                ' --intermediate_encoding_out ' + args.intermediate_encoding_out + "_" + file_name + "_" + str(k) + \
                ' --solver_out ' + args.solver_out + "_" + file_name + "_" + str(k) + \
                ' --plan_out ' + args.plan_out + "_" + file_name + "_" + str(k)

      plan_status = os.popen(command).read()
      ls = plan_status.strip("\n").split("\n")

      for line in ls:
        print(line)
        # Getting time used for one call:
        if ("Solving time" in line):
          parsed_line = line.strip("\n").split(": ")
          remaining_time -= float(parsed_line[1])

      if ("Plan found" in plan_status):
          print("Plan found for length: " + str(k))
          print("Peak Memory used (in MB): " + str(getrusage(RUSAGE_CHILDREN).ru_maxrss/1024.0))
          if (args.run == 2):
            if ("Plan valid" in plan_status):
              print("Plan valid\n")
            else:
              print("Plan invalid! Error. <---------------------------------------\n")
          return 0
      else:
          print("Plan not found for length: " + str(k) + "\n")
          if ('Time out' in plan_status):
              print("Peak Memory used (in MB): " + str(getrusage(RUSAGE_CHILDREN).ru_maxrss/1024.0))
              print("Time out occured\n")
              return 1
          elif ('Memory out occurred' in plan_status):
              print("Peak Memory used (in MB): " + str(getrusage(RUSAGE_CHILDREN).ru_maxrss/1024.0))
              return 1


# Main:
if __name__ == '__main__':
  text = "A tool to benchmark Q-Planner on PDDL domains"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--path", help="path for domain and problem files", default = 'testing/testcases/Blocks/')
  parser.add_argument("--planner_path", help="Path for planner, for ex: qplanner", default= './Q-Planner')
  parser.add_argument("--plan_out", help="plan output file path", default = 'intermediate_files/cur_plan')
  parser.add_argument("--plan_length", type=int,default = 4)
  parser.add_argument("--step", help="step value for benchmarking, 5 default", type=int,default = 5)
  parser.add_argument("--single_instance_run", help="[0/1] default 0", type=int,default = 0)
  parser.add_argument("--problem_name", help="problem name")
  parser.add_argument("--num_iterations", help="1 default", type=int,default = 1)
  parser.add_argument("-e", help=textwrap.dedent('''
                                  encoding types:
                                  s-UE = Simple Ungrounded Encoding (default)
                                  rs-UE = Simple Ungrounded Encoding with reused parameter variables
                                  sc-UE = Strongly Constrained Ungrounded Encoding
                                  l-UE = Logarithmic Ungrounded Encoding (DQBF)'''),default = 's-UE')
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = test plan existence
                               2 = extract the plan if found'''),default = 2)
  parser.add_argument("--val_testing", type=int, help="[0/1], default 1", default = 1)
  parser.add_argument("--encoding_format", help=textwrap.dedent('''
                                       Encoding format:
                                       [qcir/ qdimacs (default)/ dqcir/ dqdimacs'''),default = 'qdimacs')
  parser.add_argument("--encoding_out", help="output encoding file",default = 'intermediate_files/encoding')
  parser.add_argument("--ignore_noop", type=int, help="[0/1] for optimal plans we can ignore noop action, default 0", default = 0)
  parser.add_argument("--preprocessed_encoding_out", help="preprocessed encoding file",default = 'intermediate_files/preprocessed_encoding')
  parser.add_argument("--intermediate_encoding_out", help="output intermediate encoding file",default = 'intermediate_files/intermediate_encoding')
  parser.add_argument("--solver", help=textwrap.dedent('''
                                       Solver:
                                       [quabs/ caqe (default)/ rareqs/ pedant/ qute]'''),default = 'caqe')
  parser.add_argument("--solver_out", help="solver output file",default = 'intermediate_files/solver_output')
  parser.add_argument("--restricted_forall", type=int, help=" Additional clause to restrict forall branches [0/1/2], default 0",default = 0)
  parser.add_argument("--preprocessing", help=textwrap.dedent('''
                                       Preprocessing:
                                       [off (default)/ bloqqer/ bloqqer-qdo/ hqspre/ qratpre+'''),default = 'off')
  parser.add_argument("--time_limit", type=int, help="Solving time limit in seconds, default 1800 seconds",default = 1800)

  args = parser.parse_args()
  # Checking if directory exists:
  if not Path(args.path).is_dir():
    print("Invalid directory path: " + args.path)
    exit

  # If single instance run is chosen, we do not run the whole directory:
  if (args.single_instance_run == 1):
    domain_name = "domain.pddl"
    for i in range(args.num_iterations):
      run_instance(domain_name, args.problem_name, args, i)
  else:
    files_list = glob.glob(os.path.join(args.path, "*"))
    files_list.sort(key=natural_keys)

    for file_path in files_list:
      if ('domain' in file_path):
        path, domain_name = os.path.split(file_path)
        assert(path == args.path)
        break

    count = 0

    # Running each instances with time limit:
    for file_path in files_list:
      # We assume rest of the testcases are too big as well:
      if (count > args.num_iterations * 4):
        break
      # Running each instance interation times:
      for i in range(args.num_iterations):
        # Only considering problem files:
        if ('domain' not in file_path and '.py' not in file_path):
          path, file_name = os.path.split(file_path)
          assert(path == args.path)
          timed_out = run_instance(domain_name, file_name, args, i)
          if (timed_out):
            count = count + 1
            continue
