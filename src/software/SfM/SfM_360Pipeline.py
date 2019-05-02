#!/usr/bin/python
#! -*- encoding: utf-8 -*-

# This file is part of OpenMVG (Open Multiple View Geometry) C++ library.

# Python implementation of the bash script written by Romuald Perrot
# Created by @vins31
# Modified by Pierre Moulon
#
# this script is for easy use of OpenMVG
#
# usage : python openmvg.py image_dir output_dir
#
# image_dir is the input directory where images are located
# output_dir is where the project must be saved
#
# if output_dir is not present script will create it
#

# Indicate the openMVG binary directory

OPENMVG_SFM_BIN = "/home/liguan/Src/openMVG_build/Linux-x86_64-Release"
OPENMVG_SOFTWARE_SFM_SRC_DIR = "/home/liguan/Src/openMVG/src"

import os
import subprocess
import sys

if len(sys.argv) < 3:
    print ("Usage %s image_dir output_dir" % sys.argv[0])
    sys.exit(1)

project_dir = sys.argv[1]
input_dir = os.path.join(project_dir, "images")
output_dir = sys.argv[2]

matches_dir = os.path.join(output_dir, "matches")
reconstruction_dir = os.path.join(output_dir, "reconstruction")
cubic_dir = os.path.join(output_dir, "cubic")

print ("Using input dir  : ", input_dir)
print ("      output_dir : ", output_dir)

# Create the ouput/matches folder if not present
if not os.path.exists(output_dir):
  os.mkdir(output_dir)
if not os.path.exists(matches_dir):
  os.mkdir(matches_dir)

print ("0. Prepare frames")
pFrames = subprocess.Popen( ["ffmpeg", "-i", sys.argv[1] + "/original_video.MP4", "-vf", "fps=3", input_dir+"/%04d.png"] )
pFrames.wait();

print ("1. Intrinsics analysis")
pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-c", "7", "-f", "1"] )
pIntrisics.wait()

print ("2. Compute features")
pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT", "-p", "HIGH", "-n", "30"] )
pFeatures.wait()

print ("3. Compute matches")
pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-g", "a"] )
pMatches.wait()

# Create the reconstruction if not present
if not os.path.exists(reconstruction_dir):
    os.mkdir(reconstruction_dir)

print ("4. Do Sequential/Incremental reconstruction")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_IncrementalSfM"),  "-i", matches_dir+"/sfm_data.json", "-m", matches_dir, "-o", reconstruction_dir, "-a", "0011.png", "-b", "0020.png"] )
pRecons.wait()

print ("5. Colorize Structure")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
pRecons.wait()

print ("6. Convert images to cubic")
pCubics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVGSpherical2Cubic"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", cubic_dir] )
pCubics.wait()

if not os.path.exists(output_dir+"scene_undistorted_images"):
    os.mkdir(output_dir+"scene_undistorted_images")

print ("7. Convert to OpenMVS format")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2openMVS"),  "-i", cubic_dir+"/sfm_data_perspective.bin",  "-o", output_dir+"./scene.mvs", "-d",  output_dir, "-n", "6"] )
pOpenMVS.wait()
