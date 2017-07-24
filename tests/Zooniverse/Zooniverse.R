library(dplyr)
library(stringr)
#images
all<-read.csv("C:/Users/Ben/Desktop/all_images.csv")

#gold standard classified
gold<-read.csv("C:/Users/Ben/Desktop/gold_standard_data.csv")

gold<-merge(all,gold)

#base url
base<-"https://snapshotserengeti.s3.msi.umn.edu"

gold$URL<-paste(base,gold$URL_Info,sep="/")

gold<-droplevels(gold)

#get capture groups that have atleast 3 images
sample_groups<-gold %>% group_by(CaptureEventID) %>% summarize(n=n()) %>% filter(n>2) %>% head(200)

sample_data <- gold %>% filter(CaptureEventID %in% sample_groups$CaptureEventID)

#get filename
sample_data$filename<-str_match(sample_data$URL_Info,pattern="(\\w+.JPG)")[,2]

#download and save to the drive.
write.csv(sample_data,"Zooniverse.csv")

#where to save
setwd("F:")
for(x in 1:nrow(sample_data)){
  row<-sample_data[x,]
  download.file(url=row$URL,row$filename,mode="wb")
}

