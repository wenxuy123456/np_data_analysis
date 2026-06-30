os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "np_attachment"))

import os
import matplotlib

if os.environ.get("CI"):
    matplotlib.use("Agg")

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "np_attachment"))

import attachment_compare_4M24_scfv as system_4M24
import attachment_compare_4M53_scfv as system_4M53
import attachment_compare_4420_anti as system_4420_anti
import attachment_compare_4420_scfv_mrfp as system_4420_scfv_mrfp
import attachment_compare_4420_scfv as system_4420_scfv
import attachment_compare_biotin as system_biotin
import attachment_compare_VIII_scfv_mrfp as system_VIII_scfv_mrfp
import attachment_compare_VIII_scfv as system_VIII_scfv
import np_attachment_percent_distance as percent_distance
import np_attachment_analysis as analysis


def run_all():
    system_4M24.main()
    system_4M53.main()
    system_4420_anti.main()
    system_4420_scfv_mrfp.main()
    system_4420_scfv.main()
    system_biotin.main()
    system_VIII_scfv_mrfp.main()
    system_VIII_scfv.main()
    percent_distance.main()
    analysis.main()


if __name__ == "__main__":
    run_all()
