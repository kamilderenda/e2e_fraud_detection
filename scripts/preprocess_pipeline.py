import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.preprocessing import *


if __name__ == "__main__":
    run_preprocessing_pipeline()