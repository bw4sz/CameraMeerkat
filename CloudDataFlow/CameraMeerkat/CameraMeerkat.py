import CommandArgs
import CloudVision
from PIL import Image
import os
from datetime import datetime
from collections import defaultdict
import subprocess
import glob
import csv
import cv2
import random
from google.cloud import storage
import tempfile

class CameraMeerkat:
    
    def __init__(self):
        self.args=CommandArgs.CommandArgs()
        #Google Credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.args.google_account
        
    #parse exif information
    def findSequences(self):
        
        print("Extracting EXIF information")
        #find files with exif info
        command=['exiftool', '-T','-r',self.args.input,'-Directory','-filename' ,'-DateTimeOriginal', '>','metadata.txt']
        p=subprocess.Popen(command,shell=True)
        p.wait()
        
        #paths
        self.image_paths=[]
        #stamps
        timestamp=[]
        
        with open("metadata.txt") as f:
            reader=csv.reader(f,delimiter='\t')
            for line in reader:
                self.image_paths.append(os.path.join(self.args.input,line[0],line[1]))
                timestamp.append(line[2])
        
        print("Found " + str(len(self.image_paths)) + " images")
        
        #create burst sequences
        self.sequences=defaultdict(list)
        counter=0
        
        #first image is by definition in a new sequence
        self.sequences[counter]=[self.image_paths[0]]

        #difference in minutes among consecutive images
        for x,stamp in enumerate(timestamp[1:]):
                a = datetime.strptime(timestamp[x], '%Y:%m:%d %H:%M:%S')
                b = datetime.strptime(timestamp[x+1], '%Y:%m:%d %H:%M:%S')
                diff=b-a
                if diff.seconds < 60:
                    self.sequences[counter].append(self.image_paths[x+1])
                else:
                    counter+=1
                    self.sequences[counter].append(self.image_paths[x+1])    
        if self.args.testing:
            self.sequences=dict(random.sample(self.sequences.items(),20))
            
    #Parse Files
    def parseFiles(self):
        
        #File Manifest
        newline=""
        f=open("Hayder/Sequences.txt",'w')
        for x in self.sequences:
            f.write(newline+str(x)+".txt")
            newline="\n"
        
        #sequence files
        for x,items in self.sequences.items():
            newline=""            
            f=open("Hayder/"+str(x) + ".txt",'w')
            for item in items:            
                f.write(newline+str(item))
                newline="\n"

    #Run Annotations
    def analyze(self):
        os.chdir("Hayder/")
        p=subprocess.Popen("HumanAnimal.exe Sequences.txt")
        p.wait()
        p.kill()
        
        #load files
        annotated_files=glob.glob("Sequ_*.txt")
        
        #parse bounding boxes
        self.bounding_boxes=defaultdict(list)
        
        for f in annotated_files:
            freader=csv.reader(open(f),delimiter='\t')
            for image in freader:
                if len(image)==2:
                    continue
                counter=0
                for box in range(int(image[-1])):
                    try:
                        self.bounding_boxes[image[0]].append(BoundingBox(path=image[0],label=image[1+5*counter],x=image[2+5*counter],y=image[3+5*counter],length=image[4+5*counter]))
                    except:
                        continue
                    counter+=1
                    
    def show(self):
        
        #box colors
        colors=[(0,0,255),(0,255,0)]
        sorted_keys = sorted(self.bounding_boxes.keys())
        
        for path in sorted_keys:
            image=cv2.imread(path)
            #draw boxes
            cv2.namedWindow("image", flags=cv2.WINDOW_NORMAL)
            boxes=self.bounding_boxes[path]
            for box in boxes:
                cv2.rectangle(image, (box.x,box.y), (box.x+box.length,box.y+box.length), colors[int(box.label)],2)
            #cv2.imshow("image",image)
            #cv2.waitKey(0)
            
            destination=os.path.join(self.args.output,"CameraMeerkat")
            
            if not os.path.exists(destination):
                os.mkdir(destination)
            fn=os.path.join(destination,os.path.basename(path))
            cv2.imwrite(fn,image)
        
        #clean up old files
        ##outputs
        annotated_files=glob.glob("Sequ_*.txt")        
        for x in annotated_files:
            os.remove(x)
        
        ##list files
        for x,items in self.sequences.items():
            os.remove(str(x) + ".txt")        
    
    def crop(self):
        
        sorted_keys = sorted(self.bounding_boxes.keys())            
        self.clips=defaultdict(list)
        
        for path in sorted_keys:
            image=cv2.imread(path)
            #draw boxes
            cv2.namedWindow("image", flags=cv2.WINDOW_NORMAL)
            boxes=self.bounding_boxes[path]
            for box in boxes:
                self.clips[path].append(image[box.y:(box.y+box.length),box.x:(box.x+box.length)])
    
    def upload(self):

        #Google Cloud Storage
        storage_client = storage.Client()
        
        bucket = storage_client.bucket("CameraMeerkat")
        if not bucket.exists():
            bucket.create()
        
        #Where to write clips to upload to bucket
        temp_destination=os.path.join(self.args.output,"CameraMeerkat")
        if not os.path.exists(destination):
            os.mkdir(destination)
        
        #for each clip, check if it exists and upload to bucket        
        for path in self.clips.keys():
            clips=self.clips[path]
    
            for index,clip in enumerate(clips):
                fn=os.path.splitext(path)+index+".jpg"
                blob = self.bucket.blob(fn)
    
                if not blob.exists(fn):
                    
                    #write temp file                                            
                    fn=os.path.join(destination,"Box_",index,"_",os.path.basename(path))
                    cv2.imwrite(fn,clip)
                    
                    #Upload and delete
                    blob.upload_from_filename(filename=fn)                                    
                    print("Uploaded " + clip)
                    
                    os.remove(fn)
    
    def cloudVision(self):
        
        #Create instance
        cv=CloudVision(self.args)
                
        #label images
        cv.label()
    
    def writeCsv(self):
        pass
 
class BoundingBox:
    def __init__(self,path,x,y,length,label):
        self.x=int(x)
        self.y=int(y)
        self.length=int(length)
        self.label=label
        self.path=path
              
     
if __name__=="__main__":
    
    CM=CameraMeerkat() #Class
    CM.findSequences() #Aggregate images by date taken
    CM.parseFiles() #Generate files for Hayder's application
    CM.analyze() #Run Hayder application
    CM.show()
    CM.upload() #Upload to google cloud
    #CM.cloudVision() #Run CloudVision API
    #CM.writeCsv() #Write local csv
    

