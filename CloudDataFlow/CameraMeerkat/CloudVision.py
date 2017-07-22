#!/usr/bin/env python

import argparse
import io
import os
from urlparse import urlparse
import fnmatch
import glob

import csv
import numpy as np
from PIL import Image
from google.cloud import vision
from google.cloud import storage
from google.cloud.vision.feature import Feature
from google.cloud.vision.feature import FeatureTypes

class CloudVision:
    
    def __init__(self):
        
        #Vision Client
        self.vision_client = vision.Client()

    def label(self):
        
        #Query Cloud Vision API
        results={}
        features = [Feature(FeatureTypes.LABEL_DETECTION, 5)]
        for x in self.images_to_label:
            self.vision_client.image(source_uri=x)
            results[x] = image.detect(features)
                
        #Show results
        counter=0
        for path in results:
            image=results[path]

            for label in image:
                print("=" * 40)
                print("%s : %.3f " % (label.description,label.score))
                
                #save outputs
                label_output.append([path,label.description,label.score])

        return label_output                
    def write(self):
        
        with open("annotations.csv", 'w',newline="") as f:  
            writer = csv.writer(f,)
            
            #write header
            writer.writerow(["Image","Description","Score"])
            
            #write labels
            writer.writerows(self.label_output)
    
    def cleanup(self):
        
        if self.parsed.scheme=="gs":
            for x in self.images_to_run:
                blob = self.bucket.blob(x)                
        
if __name__ == '__main__':
    
    #parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', default="gs://api-project-773889352370-ml/cameratrap/")    
    parser.add_argument('-google_account',default="C:/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json")    
    parser.add_argument('-bucket',default="api-project-773889352370-ml", help="Google Cloud Storage Bucket. Required if -input points to a local directory")    
    
    #TODO CHECK IF ARGS INCLUSIVE
    
    args = parser.parse_args()

    #Create instance
    cv=CloudVision(args)
    
    #Create list of images to annotate
    #upload images to bucket if needed
    cv.find()
    
    #label images
    cv.label()
    
    #write annotations file
    cv.write()
    
    #delete images if they came from local
    cv.cleanup()