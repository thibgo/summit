#!/usr/bin/env python

""" Script to perform feature parameter optimisation """

# Import built-in modules
import datetime                         # for TimeStamp in CSVFile
import time                             # for time calculations
import argparse                         # for acommand line arguments
import os                               # to geth path of the running script

# Import 3rd party modules

# Import own modules
import DBCrawl			# Functions to read Images from Database
import ExportResults            # Functions to render results
import FeatExtraction           # Functions to extract the features from Database   

# Author-Info
__author__ 	= "Nikolas Huelsmann"
__status__ 	= "Development" #Production, Development, Prototype
__date__	= 2016-03-10

### Argument Parser

parser = argparse.ArgumentParser(
description='This methods permits to export one or more features at the same time for a database of images (path, name). To extract one feature activate it by using the specific argument (e.g. -RGB). For each feature you can define the parameters by using the optional arguments (e.g. --RGB_Hist 32). The results will be exported to a CSV-File.', 
formatter_class=argparse.ArgumentDefaultsHelpFormatter)

groupStandard = parser.add_argument_group('necessary arguments:')
groupStandard.add_argument('--name', metavar='STRING', action='store', help='Select a name of DB, e.g. Caltech (default: %(default)s)', default='DB')
groupStandard.add_argument('--path', metavar='STRING', action='store', help='Path to the database (default: %(default)s)', default='D:\\CaltechMini')


groupRGB = parser.add_argument_group('RGB arguments:')
groupRGB.add_argument('-RGB', action='store_true', help='Use option to activate RGB')
groupRGB.add_argument('--RGB_Bins', metavar='INT', action='store', help='Number of bins for histogram', type=int, default=16)
groupRGB.add_argument('--RGB_CI', metavar='INT', action='store', help='Max Color Intensity [0 to VALUE]', type=int, default=256)
groupRGB.add_argument('-RGB_NMinMax', action='store_true', help='Use option to actvate MinMax Norm instead of Distribution')

groupHSV = parser.add_argument_group('HSV arguments:')
groupHSV.add_argument('-HSV', action='store_true', help='Use option to activate HSV')
groupHSV.add_argument('--HSV_H_Bins', metavar='INT', action='store', help='Number of bins for Hue', type=int, default=16)
groupHSV.add_argument('--HSV_S_Bins', metavar='INT', action='store', help='Number of bins for Saturation', type=int, default=4)
groupHSV.add_argument('--HSV_V_Bins', metavar='INT', action='store', help='Number of bins for Value', type=int, default=4)
groupHSV.add_argument('-HSV_NMinMax', action='store_true', help='Use option to actvate MinMax Norm instead of Distribution')

groupSIFT = parser.add_argument_group('SIFT arguments:')
groupSIFT.add_argument('-SIFT', action='store_true', help='Use option to activate SIFT')
groupSIFT.add_argument('--SIFT_Cluster', metavar='INT', action='store', help='Number of k-means cluster', type=int, default=50)
groupSIFT.add_argument('-SIFT_NMinMax', action='store_true', help='Use option to actvate MinMax Norm instead of Distribution')
        
groupSURF = parser.add_argument_group('SURF arguments:')
groupSURF.add_argument('-SURF', action='store_true', help='Use option to activate SURF')
groupSURF.add_argument('--SURF_Cluster', metavar='INT', action='store', help='Number of k-means cluster', type=int, default=50)
groupSURF.add_argument('-SURF_NMinMax', action='store_true', help='Use option to actvate MinMax Norm instead of Distribution')

groupHOG = parser.add_argument_group('HOG arguments:')
groupHOG.add_argument('-HOG', action='store_true', help='Use option to activate HOG')
groupHOG.add_argument('--HOG_CellD', metavar='INT', action='store', help='CellDimension for local histograms', type=int, default=5)
groupHOG.add_argument('--HOG_Orient', metavar='INT', action='store', help='Number of bins of local histograms', type=int, default=8)
groupHOG.add_argument('--HOG_Cluster', metavar='INT', action='store', help='Number of k-means cluster', type=int, default=12)
groupHOG.add_argument('--HOG_Iter', metavar='INT', action='store', help='Max. number of iterations for clustering', type=int, default=100)
groupHOG.add_argument('--HOG_cores', metavar='INT', action='store', help='Number of cores for HOG', type=int, default=1)

### Read args
args = parser.parse_args()

nameDB = args.name
path = args.path

### Helper-Function to transform the boolean deciscion of norm into a string
def boolNormToStr(norm):
        if(norm):
                return "MinMax"
        else:
                return "Distr"

### Main Programm

print "### Main Programm for Feature Extraction ###"
features = ""
if(args.RGB):
        features = features + "RGB "
if(args.HSV):
        features = features + "HSV "
if(args.SIFT):
        features = features + "SIFT "
if(args.SURF):
        features = features + "SURF "
if(args.HOG):
        features = features + "HOG"

print "Infos:\t NameDB=" + nameDB + ", Path=" + path  + ", Features=" + features

################################ Read Images from Database
# Determine the Database to extract features

print "Start:\t Exportation of images from DB"

t_db_start = time.time()

# get dictionary to link classLabels Text to Integers
sClassLabels = DBCrawl.getClassLabels(path)

# Get all path from all images inclusive classLabel as Integer
dfImages,nameDB = DBCrawl.imgCrawl(path, sClassLabels, nameDB)
t_db  = time.time() - t_db_start
print "Done:\t Exportation of images from DB in:" + str(t_db) +"[s]"


################################ Feature Extraction
print "Start:\t Features Extraction"

### Setup RGB
if(args.RGB):
        
        print "RGB:\t Start"
        t_rgb_start = time.time()
                
        # Infos
        print "RGB:\t NumberOfBins=" + str(args.RGB_Bins) + ", MaxColorIntensity=" + str(args.RGB_CI) + ", Norm=" + boolNormToStr(args.RGB_NMinMax)
         
        # Extract Feature from DB
        rgb_feat_desc,rgb_f_extr_res = FeatExtraction.calcRGBColorHisto(nameDB, dfImages, args.RGB_Bins, args.RGB_CI, args.RGB_NMinMax)

        t_rgb = time.time() - t_rgb_start
        print "RGB:\t Done in: " + str(t_rgb) + "[s]"


### Setup HSV
if(args.HSV):
        print "HSV:\t Start"
        t_hsv_start = time.time()
        
        h_bins = args.HSV_H_Bins
        s_bins = args.HSV_S_Bins
        v_bins = args.HSV_V_Bins
        histSize = [h_bins, s_bins, v_bins]
        
        # Infos
        print "HSV:\t HSVBins=[" + str(h_bins) + "," + str(s_bins) + "," + str(v_bins) + "], Norm=" + boolNormToStr(args.HSV_NMinMax)

        # Extract Feature from DB
        hsv_feat_desc,hsv_f_extr_res = FeatExtraction.calcHSVColorHisto(nameDB, dfImages, histSize, args.HSV_NMinMax)
        t_hsv = time.time() - t_hsv_start
        print "HSV:\t Done in: " + str(t_hsv) + "[s]"



### Setup SIFT
if(args.SIFT):
        print "SIFT:\t Start"
        t_sift_start = time.time()
        
        boolSIFT = True
        
        print "SIFT:\t Cluster=" + str(args.SIFT_Cluster) + ", Norm=" + boolNormToStr(args.SIFT_NMinMax)

        sift_descriptors,sift_des_list = FeatExtraction.calcSURFSIFTDescriptors(dfImages, boolSIFT)
        sift_feat_desc,sift_f_extr_res = FeatExtraction.calcSURFSIFTHisto(nameDB, dfImages, args.SIFT_Cluster, args.SIFT_NMinMax, sift_descriptors, sift_des_list, boolSIFT)
        t_sift = time.time() - t_sift_start 
        print "SIFT:\t Done in: " + str(t_sift) + "[s]"


### Setup SURF
if(args.SURF):
        print "SURF:\t Start"
        t_surf_start = time.time()
        
        boolSIFT = False
        
        print "SURF:\t Cluster=" + str(args.SURF_Cluster) + ", Norm=" + boolNormToStr(args.SURF_NMinMax)

        # Extract Feature from DB
        surf_descriptors,surf_des_list = FeatExtraction.calcSURFSIFTDescriptors(dfImages, boolSIFT)
        surf_feat_desc,surf_f_extr_res = FeatExtraction.calcSURFSIFTHisto(nameDB, dfImages, args.SURF_Cluster, args.SURF_NMinMax, surf_descriptors, surf_des_list, boolSIFT)
        t_surf = time.time() - t_surf_start 
        print "SURF:\t Done in: " + str(t_surf) + "[s]"

### Setup HOG
if(args.HOG):
        print "HOG:\t Start"
        t_hog_start = time.time()
        
        CELL_DIMENSION = args.HOG_CellD
        NB_ORIENTATIONS = args.HOG_Orient
        NB_CLUSTERS = args.HOG_Cluster
        MAXITER = args.HOG_Iter
        NB_CORES = args.HOG_cores
        
        print "HOG:\t CellDim=" + str(CELL_DIMENSION) + ", NbOrientations=" + str(NB_ORIENTATIONS) +", Cluster=" + str(NB_CLUSTERS) + ", MaxIter=" + str(MAXITER) + ", NbCores=" + str(NB_CORES)

        # Extract Feature from DB
        hog_feat_desc,hog_f_extr_res = FeatExtraction.calcHOGParallel(nameDB, dfImages.values, CELL_DIMENSION, NB_ORIENTATIONS, NB_CLUSTERS, MAXITER, NB_CORES)
        #hog_feat_desc,hog_f_extr_res = FeatExtraction.calcHOG(nameDB, dfImages.values, CELL_DIMENSION, NB_ORIENTATIONS, NB_CLUSTERS, MAXITER)   
        t_hog = time.time() - t_hog_start
        print "HOG:\t Done in: " + str(t_hog) + "[s]"

print "Done:\t Features Extraction"


################################ SAVE TO FEATURES DATABASES
print "Start:\t Save Features to CSV Databases"

dir = os.path.dirname(os.path.abspath(__file__)) + "/Results-FeatExtr/"

### Classlabels and Description
OutputfileNameClassLabels = datetime.datetime.now().strftime("%Y_%m_%d") + "-" + nameDB + "-ClassLabels"
ExportResults.exportNumpyToCSV(dfImages.classLabel, dir, OutputfileNameClassLabels, '%i')

fileNameClassLabels = datetime.datetime.now().strftime("%Y_%m_%d") + "-" + nameDB + "-ClassLabels-Description"
ExportResults.exportPandasToCSV(sClassLabels, dir, fileNameClassLabels)

format = '%1.30f'
### RGB
if(args.RGB):
        fileName = datetime.datetime.now().strftime("%Y_%m_%d") + "-" + rgb_feat_desc
        ExportResults.exportNumpyToCSV(rgb_f_extr_res, dir, fileName, format)
        

### HSV
if(args.HSV):
        fileName = datetime.datetime.now().strftime("%Y_%m_%d") + "-" + hsv_feat_desc
        ExportResults.exportNumpyToCSV(hsv_f_extr_res, dir, fileName, format)

### SIFT
if(args.SIFT):
        fileName = datetime.datetime.now().strftime("%Y_%m_%d") + "-" + sift_feat_desc
        ExportResults.exportNumpyToCSV(sift_f_extr_res, dir, fileName, format)

### SURF
if(args.SURF):
        fileName = datetime.datetime.now().strftime("%Y_%m_%d") + "-" + surf_feat_desc
        ExportResults.exportNumpyToCSV(surf_f_extr_res, dir, fileName, format)

### HOG
if(args.HOG):
        fileName = datetime.datetime.now().strftime("%Y_%m_%d") + "-" + hog_feat_desc
        ExportResults.exportNumpyToCSV(hog_f_extr_res, dir, fileName, format)

print "Done:\t Save Features to CSV Databases"