#!/usr/bin/env python
"""
Wrapper script for running the final stages of our CVPR12 experiments.
"""
import shutil
import glob
import argparse
import matplotlib.pyplot as plt
import random
import string

from common_imports import *
from common_mpi import *
import synthetic.config as config

from synthetic.dataset import Dataset
from synthetic.dataset_policy import DatasetPolicy
from synthetic.sliding_windows import SlidingWindows 
from synthetic.evaluation import Evaluation

def load_configs(name):
  """
  If name is a file, calls load_config_file(name).
  If it's a directory, calls load_config_file() on every file in it.
  """
  def load_config_file(filename):
    """
    Load the config in json format and return as list of experiments.
    Look for config_dir/#{name}.json
    """
    print("Loading %s"%filename)
    assert(opexists(filename))
    with open(filename) as f:
      cf = json.load(f)
    
    # Gather multiple values of settings, if given
    num_conditions = 1
    bounds_list = []
    if 'bounds' in cf:
      bounds_list = cf['bounds'] \
        if isinstance(cf['bounds'][0], list) else [cf['bounds']]
      num_conditions *= len(bounds_list)
    
    if 'policy_mode' in cf:
      cp_modes_list = []
      cp_modes_list = cf['policy_mode'] \
        if isinstance(cf['policy_mode'], list) else [cf['policy_mode']]
      num_conditions *= len(cp_modes_list)

    configs = []
    for i in range(0,num_conditions):
      configs.append(dict(cf))
      if 'bounds' in cf:
        configs[i]['bounds'] = bounds_list[i%len(bounds_list)]
      configs[i]['policy_mode'] = cp_modes_list[i%len(cp_modes_list)]
    return configs

  dirname = opjoin(config.config_dir,name)
  filename = opjoin(config.config_dir,name+'.json')
  if os.path.isdir(dirname):
    filenames = glob.glob(dirname+'/*.json')
    configs = []
    for filename in filenames:
      configs += load_config_file(filename)
  else:
    configs = load_config_file(filename)
  return configs

def main():
  parser = argparse.ArgumentParser(
    description="Run experiments with the timely detection system.")

  parser.add_argument('--test_dataset',
    choices=['val','test'],
    default='val',
    help="""Dataset to use for testing. Run on val until final runs.
    The training dataset is inferred (val->train; test->trainval).""")

  parser.add_argument('--first_n', type=int,
    help='only take the first N images in the datasets')

  parser.add_argument('--config',
    help="""Config file name that specifies the experiments to run.
    Give name such that the file is configs/#{name}.json or configs/#{name}/
    In the latter case, all files within the directory will be loaded.""")

  parser.add_argument('--force', action='store_true', 
    default=False, help='force overwrite')

  parser.add_argument('--wholeset_prs', action='store_true', 
    default=False, help='evaluate in the final p-r regime')

  parser.add_argument('--no_apvst', action='store_true', 
    default=False, help='do NOT evaluate in the ap vs. time regime')

  parser.add_argument('--det_configs', action='store_true', 
    default=False, help='output detector statistics to det_configs')

  args = parser.parse_args()

  # TODO temp profiling
  #args.config = 'feb27'
  #args.first_n = 2
  #args.test_dataset = 'test'

  print(args)

  # If config file is not given, just run one experiment using default config
  if not args.config:
    configs = [DatasetPolicy.default_config]
  else:
    configs = load_configs(args.config)

  # Load the dataset
  dataset = Dataset('full_pascal_'+args.test_dataset)
  if args.first_n:
    dataset.images = dataset.images[:args.first_n]

  # Infer train_dataset
  if args.test_dataset=='test':
    train_dataset = Dataset('full_pascal_trainval')
  elif args.test_dataset=='val':
    train_dataset = Dataset('full_pascal_train')
  else:
    None # impossible by argparse settings

  dets_tables = []
  clses_tables = []
  all_bounds = []

  for config_f in configs:
    dp = DatasetPolicy(dataset, train_dataset, **config_f)
    ev = Evaluation(dp)
    all_bounds.append(dp.bounds)

    # output the det configs first
    if args.det_configs:
      dp.output_det_statistics()

    # evaluate in the AP vs. Time regime, unless told not to
    if not args.no_apvst:
      dets_table,clses_table = ev.evaluate_vs_t(None,None,force=args.force)
      dets_table_whole,clses_table_whole = ev.evaluate_vs_t_whole(None,None,force=args.force)
      if comm_rank==0:
        dets_tables.append(dets_table)
        clses_tables.append(clses_table)

    # optionally, evaluate in the standard PR regime
    if args.wholeset_prs:
      ev.evaluate_detections_whole(None,force=args.force)

  # and plot the comparison if multiple config files were given
  if not args.no_apvst and len(configs)>1 and comm_rank==0:
    # filename of the final plot is the config file name
    dirname = config.get_evals_dir(dataset.get_name())
    filename = args.config
    ff = os.path.join(dirname, '%s.png'%filename)
    ff_no_legend = os.path.join(dirname, '%s_no_legend.png'%filename)
    Evaluation.plot_ap_vs_t(dets_tables, ff, all_bounds, with_legend=True)
    Evaluation.plot_ap_vs_t(dets_tables, ff_no_legend, all_bounds, with_legend=False)
    
if __name__ == '__main__':
  main()
