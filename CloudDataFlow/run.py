import logging
from CameraMeerkat import CameraMeerkat

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
    CM=CameraMeerkat() #Class
    CM.findSequences() #Aggregate images by date taken
    CM.parseFiles() #Generate files for Hayder's application
    CM.analyze() #Run Hayder application
