import argparse

def CommandArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="path of camera directory",type=str,default='G:\cameratrap\cameratrap\Set2')
    parser.add_argument("--testing", help="path of camera directory",action='store_true')    
    parser.add_argument("--output", help="output directory",default="C:/MotionMeerkat")
    parser.add_argument("--google_account", help="Path to google service account .json file",default="C:/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json")	
    args=parser.parse_args()
    return(args)
    