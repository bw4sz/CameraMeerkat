#!/usr/bin/env python

import argparse
import io
import os
from urllib.parse import urlparse
import fnmatch
import glob
import csv

from google.cloud import vision
from google.cloud import storage
from google.cloud.vision.feature import Feature
from google.cloud.vision.feature import FeatureTypes

class CloudVision:
    
    def __init__(self,args):
        print("Welcome to CameraMeerkat")
        
        #assign args
        self.image_path=args.image_path
        self.auth_path=args.auth_path

        #set credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.auth_path
    
        #Vision Client
        self.vision_client = vision.Client()
    
        #Storage Client
        self.storage_client = storage.Client()    
            
        if not len(args.bucket)== 0:
            self.bucket=self.storage_client.get_bucket(args.bucket)
                
    def find(self):
        
        self.images_to_run=[]
        
        self.parsed = urlparse(self.image_path)

        if self.parsed.scheme=="gs":
        
            #parse gcp path
            self.bucket = self.storage_client.get_bucket(self.parsed.hostname)    
            imgs=self.bucket.list_blobs(prefix=self.parsed.path[1:])
            
            #image list
            self.image_list=[]
            for img in imgs:
                self.image_list.append("gs://" + self.bucket.name +"/"+ str(img.name))
        
            #only get .jpgs
            jpgs=fnmatch.filter(self.image_list,"*.jpg")
            
            for x in jpgs:
                jpg = self.vision_client.image(source_uri=x) 
                self.images_to_run.append(jpg)
        else:
            
            #get image paths
            self.image_list=glob.glob(self.image_path + "/*jpg")
                        
            for image in self.image_list:

                #construct filename
                splitname=os.path.split(image)
                filename=splitname[len(splitname)-1]
                blob = self.bucket.blob(self.parsed.path[1:] + "/" + filename.lower())
                
                #TODO CHECK IF EXISTS
                if not blob.exists():
                    blob.upload_from_filename(filename=image)                        
                    #upload to gcp                
                    print("Uploaded " + image)
                else:
                    print(image + " already exists in bucket")
                
                #create image instance
                jpg = self.vision_client.image(source_uri="gs://" + self.bucket.name + "/" + self.parsed.path + "/" + filename.lower())   
                self.images_to_run.append(jpg)
            
    def label(self):
        
        #Query API
        results=[]
        for x in self.images_to_run:
            results.append(x.detect_labels())
        
        self.label_output=[]
        #Show results
        counter=0
        for image in results:
            print("Image: %s" % self.image_list[counter])
            for label in image:
                print("=" * 40)
                print("%s : %.3f " % (label.description,label.score))
                
                #save outputs
                self.label_output.append([self.image_list[counter],label.description,label.score])
            
            #Show next image
            counter=counter+1
                        
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
    parser.add_argument('-image_path', default="gs://api-project-773889352370-ml/cameratrap/")    
    parser.add_argument('-auth_path',default="C:/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json")    
    parser.add_argument('-bucket',default="api-project-773889352370-ml", help="Google Cloud Storage Bucket. Required if -image_path points to a local directory")    
    
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