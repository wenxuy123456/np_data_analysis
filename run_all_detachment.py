import os
import matplotlib

if os.environ.get("CI"):
    matplotlib.use("Agg")

import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(script_dir, "np_detachment"))
sys.path.insert(0, os.path.join(script_dir, "np_detachment"))

import detach_compare_4420 as system_4420
import detach_compare_4M24 as system_4M24
import detach_compare_4M53 as system_4M53
import detach_compare_biotin as system_biotin
import np_detachment_analysis as analysis
import np_detachment_beta_histogram as beta_histogram
import np_detachment_percent_distance as percent_distance


def run_all():
    system_4420.main()
    system_4M24.main()
    system_4M53.main()
    system_biotin.main()
    analysis.main()
    beta_histogram.main()
    percent_distance.main()


if __name__ == "__main__":
    run_all()