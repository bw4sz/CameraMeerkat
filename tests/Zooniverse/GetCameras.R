library(dplyr)
library(stringr)

images<-read.csv("G:/Zooniverse/all_images.csv")
labels<-read.csv("G:/Zooniverse/consensus_data.csv")

#get all images from the same site and location, ordered by time.
images$CameraEvent<-str_match(images$URL_Info,"/(\\w+)_PICT\\w+.JPG")[,2]

#get full url
#append base url
base<-"https://snapshotserengeti.s3.msi.umn.edu"
images$URL<-paste(base,images$URL_Info,sep="/")

#assign file name
images$filename<-str_match(images$URL_Info,pattern="(\\w+.JPG)")[,2]

table(images$CameraEvent)

WriteImages<-function(x){
  towrite<-images %>% dplyr::filter(CameraEvent %in% x)
  #where to save
  setwd("G:/Zooniverse")
  
  #create a folder with the name
  dir.create(x)
  
  
  for(img in 1:nrow(towrite)){
    row<-towrite[img,]
    try(download.file(url=row$URL,paste(x,"/",row$filename,sep=""),mode="wb"))
  }
  
}

#get first five
cams<-unique(images$CameraEvent)[sample(1:length(unique(images$CameraEvent)),1)]
sapply(cams,function(y) WriteImages(y))
