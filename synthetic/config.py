"Set up paths to files and other one-time or platform-dependent settings."

from os.path import join,exists
import getpass

from synthetic.util import makedirs

##################
# VARIABLES
##################
VOCyear = '2007'
kernels = ['linear', 'rbf']
pascal_classes = ['aeroplane','bicycle', 'bird','boat','bottle','bus','car',
                  'cat','chair','cow','diningtable','dog', 'horse',
                  'motorbike','person','pottedplant','sheep','sofa','train',
                  'tvmonitor']
# TODO: formalize the below path
dpm_may25_dirname = '/tscratch/tmp/sergeyk/object_detection/dets_may25_DP/'

##################
# CODE PATHS
# - nothing in data_dir should be tracked by the code repository.
#   it should be tracked by its own repository
# - temp_data_dir is for large files and can be on temp filespace
##################
# Determine environment
if exists('/home/tobibaum'):
  env = 'tobi_home'
elif exists('/Users/sergeyk'):
  env = 'sergeyk_home'
elif exists('/u/vis/'):
  user = getpass.getuser()
  if user=='tobibaum':
    env = 'tobi_icsi'
  if user=='sergeyk':
    env = 'sergeyk_icsi'
else:
  raise RuntimeError("Can't set paths correctly")

# repo_dir, data_dir, temp_data_dir
# temp_data_dir is not propagated between machines!
paths = {
  'tobi_home':    ['/home/tobibaum/Documents/Vision/timely/',
                   '/home/tobibaum/Documents/Vision/timely/data/',
                   '/home/tobibaum/Documents/Vision/timely/data/temp/'],
  'tobi_icsi':    ['/u/tobibaum/timely/',
                   '/u/vis/x1/tobibaum/data/',
                   '/tscratch/tmp/tobibaum/timely/'],
  'sergeyk_home': ['/Users/sergeyk/research/timely/',
                   '/Users/sergeyk/research/timely/data/',
                   '/Users/sergeyk/research/timely/data/temp/'],
  'sergeyk_icsi': ['/u/sergeyk/research/timely/',
                   '/u/sergeyk/research/timely/data',
                   '/tscratch/tmp/sergeyk/timely/'],                   
}
repo_dir, data_dir, temp_data_dir = paths[env]
makedirs(data_dir)
makedirs(temp_data_dir)

##################
# DERIVED PATHS
##################
# Code
script_dir = join(repo_dir, 'synthetic')

# Input data
test_support_dir = join(script_dir, 'test_support')
data1 = join(test_support_dir,'data1.json')
VOC_dir = join(data_dir, 'VOC%(year)s/')%{'year':VOCyear}
pascal_paths = {
    'test_pascal_train':    join(test_support_dir,'train.txt'),
    'test_pascal_val':      join(test_support_dir,'val.txt'),
    'test_pascal_train_tobi':    join(test_support_dir,'train_tobi.txt'),
    'test_pascal_val_tobi':      join(test_support_dir,'val_tobi.txt'),
    'full_pascal_train':    join(VOC_dir,'ImageSets/Main/train.txt'),
    'full_pascal_val':      join(VOC_dir,'ImageSets/Main/val.txt'),
    'full_pascal_trainval': join(VOC_dir,'ImageSets/Main/trainval.txt'),
    'full_pascal_test':     join(VOC_dir,'ImageSets/Main/test.txt')}
config_dir = join(script_dir,'configs')
eval_support_dir = join(script_dir, 'eval_support')
eval_template_filename = join(eval_support_dir, 'dashboard_template.html')

# Result data
res_dir = makedirs(join(data_dir, 'results'))
temp_res_dir = makedirs(join(data_dir, 'temp_results'))
dets_configs_dir = makedirs(join(res_dir,'det_configs'))

# ./results/sliding_windows_{dataset}
def get_sliding_windows_dir(dataset_name):
  return makedirs(join(res_dir, 'sliding_windows_%s'%dataset_name))

# ./results/sliding_windows_{dataset}/metaparams
def get_sliding_windows_metaparams_dir(dataset_name):
  return makedirs(join(get_sliding_windows_dir(dataset_name), 'metaparams'))

# ./results/sliding_windows_{dataset}/stats.pickle
def get_window_stats_results(dataset_name):
  return join(get_sliding_windows_dir(dataset_name), 'stats.pickle')

# ./results/sliding_windows/{stat}/{cls}.png
def get_window_stats_plot(dataset_name, stat, cls):
  window_stats_plot_dir = makedirs(join(get_sliding_windows_dir(dataset_name), stat))
  return join(window_stats_plot_dir, '%s.png'%cls)

# ./results/sliding_windows_{dataset}/params
# NOTE: in temp_res_dir!
def get_sliding_windows_cached_dir(dataset_name):
  sliding_windows_dir = join(temp_res_dir, 'sliding_windows_%s'%dataset_name)
  return makedirs(join(sliding_windows_dir, 'cached'))

# ./results/sliding_windows_{dataset}/params
def get_sliding_windows_params_dir(dataset_name):
  return makedirs(join(get_sliding_windows_dir(dataset_name), 'params'))

# ./results/jumping_windows_{dataset}/
def get_jumping_windows_dir(dataset_name):
  return makedirs(join(res_dir, 'jumping_windows_%s'%dataset_name))

def get_windows_params_grid(dataset_name):
  return join(get_sliding_windows_params_dir(dataset_name), 'window_params_grid.csv')

def get_window_params_json(dataset_name):
  return join(get_sliding_windows_params_dir(dataset_name), '%s.txt')

# ./results/evaluations
evals_dir = makedirs(join(res_dir, 'evals'))

# ./results/evaluations/{dataset_name}
def get_evals_dir(dataset_name):
  return makedirs(join(evals_dir,dataset_name))

# ./results/evaluations/{dataset_name}/{dp_config_name}
def get_evals_dp_dir(dataset_policy):
  dirname = get_evals_dir(dataset_policy.dataset.get_name())
  return makedirs(join(dirname, dataset_policy.get_config_name()))

# ./results/evaluations/{dataset_name}/{dp_config_name}/cached_dets.npy
def get_dp_dets_filename(dataset_policy):
  return join(get_evals_dp_dir(dataset_policy), 'cached_dets.npy')

# ./results/evaluations/{dataset_name}/{dp_config_name}/cached_clses.npy
def get_dp_clses_filename(dataset_policy):
  return join(get_evals_dp_dir(dataset_policy), 'cached_clses.npy')

# results/evaluations/{dataset_name}/{dp_config_name}/weights/
def get_dp_weights_dirname(dataset_policy):
  dirname = get_evals_dp_dir(dataset_policy)
  return makedirs(join(dirname,'weights'))

def get_cached_dataset_filename(name):
  assert(name in pascal_paths)
  dirname = makedirs(join(res_dir,'cached_datasets'))
  return join(dirname, str(VOCyear)+'_'+name+'.pickle')

# ./res_dir/ext_dets/{dataset}_*.npy
def get_ext_dets_foldname(dataset):
  dirname = makedirs(join(res_dir,'ext_dets'))
  return dirname

def get_ext_dets_vector_foldname(dataset):
  dirname = makedirs(join(res_dir,'ext_dets',dataset.name,'feat_vect'))
  return dirname

  
def get_ext_dets_filename(dataset, suffix):
  if dataset == None:
    # TODO:
    """
    Just load eeeevery image 
    """
    dataset_name = 'full_pascal_full'
  else:
    dataset_name = dataset.name # NOTE does not depend on # images
  dirname = makedirs(join(res_dir,'ext_dets'))  
  return join(dirname, '%s_%s.npy'%(dataset_name,suffix))

#####
# GIST
#####
# results/gist_features/

#####
# GIST
#####
gist_dir = makedirs(join(res_dir, 'gist_features'))

# results/gist_features/full_pascal_trainval.npy
def get_gist_dict_filename(dataset_name):
  return join(gist_dir, dataset_name + '.npy')

# results/gist_features/svm/
def get_gist_svm_filename(for_cls):
  dirname = makedirs(join(gist_dir,'svm'))
  return join(dirname,for_cls)

def get_gist_fastinf_table_name(dataset, cls):
  savedir = join(res_dir, 'gist', dataset)
  makedirs(savedir)
  if cls == None:
    savefile = join(savedir,'cls_gt')
  else:
    savefile = join(savedir,'cls_gt_%s'%cls)
  return savefile
#####
# Classifier
#####
# learning
def get_classifier_learning_dirname(classifier):
  name = classifier.name+'_svm'
  if len(classifier.suffix) >= 1:
    name += '_'+classifier.suffix
  return makedirs(join(res_dir,name))

def get_classifier_svm_learning_filename(classifier, cls,kernel,intervals,lower,upper,C):
  direct = get_classifier_dirname(classifier)
  name = '%s_%s_%f_%f_%f_%f'%(cls,kernel,intervals,lower,upper,C)
  return join(direct,name)

def get_classifier_learning_filename(classifier,cls,kernel,intervals,lower,upper,C):
  dirname = makedirs(join(get_classifier_learning_dirname(classifier), kernel, str(intervals)))
  return join(dirname, "%s_%d_%d_%d"%(cls,lower,upper,C))
    
def get_classifier_learning_eval_filename(classifier,cls,kernel,intervals,lower,upper,C):
  dirname = makedirs(join(get_classifier_learning_dirname(classifier), kernel, str(intervals)))
  return join(dirname, "eval_%d_%d_%d"%(lower,upper,C))

def get_classifier_svm_name(cls, C, gamma, current_fold):
  dirname = join(res_dir, 'classify_svm')
  makedirs(dirname) 
  if current_fold == -1: 
    filename = join(dirname, '%s_%f_%f'%(cls, C, gamma))
  else:
    filename = join(dirname, '%s_%f_%f_%d'%(cls, C, gamma, current_fold)) 
  return filename

# final
def get_classifier_dirname(classifier):
  name = classifier.name+'_svm'
  if len(classifier.suffix) >= 1:
    name += '_'+classifier.suffix
  return makedirs(join(res_dir,name))

def get_classifier_filename(classifier,cls):
  return join(get_classifier_dirname(classifier), cls)

def get_classifier_featvect_name(img):
  dirname = join(res_dir, 'classify_featvects')
  makedirs(dirname) 
  return join(dirname, img.name[:-4])

def get_classifier_score_name(img):
  dirname = join(res_dir, 'classify_scores')
  makedirs(dirname) 
  return join(dirname, img.name[:-4])

def get_classifier_crossval(cls):
  dirname = join(res_dir, 'classify_scores')
  makedirs(dirname) 
  return join(dirname, 'crossval_%s.txt'%cls)

#####
# Feature Extraction
#####
def get_image_path(image):
  return join(VOC_dir, 'JPEGImages/', image.name)

def get_assignments_path(feature, image):
  dirname = join(data_dir, feature, 'assignments/')
  makedirs(dirname)
  return join(dirname, image.name[0:-4])

def get_codebook_path(feature):
  dirname = join(data_dir, feature, 'codebooks')
  makedirs(dirname)
  return join(dirname, 'codebook')

#####
# External detections
#####
def get_dets_test_wholeset_dir():
  return join(res_dir, 'dets_test_original_wholeset')

def get_dets_nov19():
  return join(res_dir, 'dets_nov19')

#####
# Inference
#####
fastinf_dir = join(res_dir, 'fastinf')
fastinf_bin = join(repo_dir, 'fastInf/build/bin/infer_timely')
makedirs(fastinf_dir)
def get_fastinf_mrf_file(dataset, suffix):
  dirname = makedirs(join(fastinf_dir, dataset.name, suffix))
  return join(dirname, 'mrf.txt')

def get_mrf_bound_filename(dataset, suffix):
  dirname = makedirs(join(fastinf_dir, dataset.name, suffix))
  return join(dirname, 'bounds.txt')

def get_mrf_model(num_vars):
  return join(fastinf_dir, 'basic_model_%d'%num_vars)
  
def get_fastinf_data_file(dataset, suffix):
  dirname = makedirs(join(fastinf_dir, dataset.name, suffix))
  return join(dirname, 'data.txt')

def get_fastinf_res_file(dataset, suffix):
  dirname = makedirs(join(fastinf_dir, dataset.name, suffix))
  return join(dirname, 'res.txt')

def get_fastinf_cache_file(dataset,suffix):  
  dirname = makedirs(join(fastinf_dir, dataset.name, suffix))
  return join(dirname, 'cache.npy')
