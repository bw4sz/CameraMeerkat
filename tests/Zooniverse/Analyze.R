#Anaylze

library(dplyr)
library(ggplot2)
library(stringr)

#true state
true_state<-read.csv("Zooniverse.csv")

#predicted labels
pred_state<-read.csv("annotations.csv")

#merge 

head(pred_state)
head(true_state)

#match IDs
pred_state$filename<-  str_match(pred_state$Image,"\\w+.JPG")
dat<-merge(pred_state,true_state,by="filename")


#turn to characters
dat$Decription<-as.character(dat$Description)
dat$Species<-as.character(dat$Species)
dat$filename<-as.character(dat$filename)

#Label Diversity
dat %>% group_by(Description) %>% summarize(n=n()) %>% arrange(desc(n))

keep<-c("wildlife","water buffalo","tapir","hippopotamus","duck","pack animal","flightless bird","deer","pronghorn","ostrich","goose"," dog like mammal","antelope","water bird","springbok","giraffe","gazelle","bird","giraffidae","bison","impala","cow goat family","elephant","indian elephant","elephants and mammoths","wildebeest","rhinoceros","mare","mustang horse","zebra","bull","vertebrate","horse","cattle like mammal","horse like mammal","mammal","wildlife","fauna")

#how many labels were kept?
length(keep)/length(unique(dat$Description))

#number of species before
before<-true_state %>% group_by(Species) %>% summarize(before=n())

keepdat<-dat %>% filter(Description %in% keep)

#number of species after
prop<-true_state %>% filter(filename %in% keepdat$filename) %>% group_by(Species) %>% summarise(after=n()) %>% full_join(before)  %>% mutate(p=round(after/before,3)*100)

#list of images that should have been kept but were discarded.
missed<-true_state %>% filter(!filename %in% keepdat$filename) 

#ridiculous human label, there is a tiny human like a quarter mile away.
S4_U13_R2_IMAG0857.JPG
S4_U13_R2_IMAG0858.JPG

#proportion of exactly matches
sum(dat$Species==dat$Decription)/nrow(true_state) * 100
dat %>% filter(Species==Description) %>% group_by(Species) %>% summarize(n=n())

#humans
dat %>% filter(Species=="human") %>% group_by(filename) %>% group_by(Description) %>% summarize()

dat %>% filter(Species=="impossible")

#parse out the common shared labels #analogoeus to sorting out common words in text mining
common<-dat %>% group_by(Description) %>% summarize(n=n()) %>% arrange(desc(n)) %>% filter(n>250)

#grab labels of interest
