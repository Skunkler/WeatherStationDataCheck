#This script was written by Warren Kunkler in support of the UHI project on February 27th 2020
#This script is designed to pull out air temperature weather station data and relate it back to the landsat surface temp
#data by asking the user for the specific landsat acquisition time and finding the closest gage reading for a given day

import os, arcpy, shutil
import datetime as dt
from arcpy import env


#This directory must point to gage csv data
rootDir = r"S:\LV_Valley_Imagery\UHII\UHI_KUNKLERU\StationData"


#prompting the user for inputs
listRef = []
month = raw_input("Please enter a month value (1-12): ")
day = raw_input("Please enter a day value (1-31): ")
Hr = raw_input("Please enter an hour(0-23): ")
Mn = raw_input("Please enter a minute(0-60): ")
Ss = raw_input("Please enter a second(0-60): ")

print type(month)

#must set up a geodatabase where the station points are as the workspace
arcpy.env = r"S:\LV_Valley_Imagery\UHII\UHI_KUNKLERU\test.gdb"

shp = r"S:\LV_Valley_Imagery\UHII\UHI_KUNKLERU\test.gdb\stations_x_2"

arcpy.MakeFeatureLayer_management(shp, "lyr")
#add the air temperature data field
arcpy.AddField_management("lyr", "airTemp", "LONG")







#This function loops through the dictionary, builds a list of values and finds
#and returns the minimum difference between weather station time and landsat acquisition time
def getNearestTime(DictObj):
    listVals = [DictObj[key] for key in DictObj.keys()]
    minVal= min(listVals)

    for key in DictObj:
        if DictObj[key] == minVal:
            return key
    

#This function takes a list of csv files, loops through each of them,
#finds the difference between each record and the input landsat acquisition time
#adds everything into a dictionary, passes that dictionary to getNearestTime
#and builds a final output dictionary containing the recods with the closest time for each gage
def findTemp(ListVals):

    dateComp = dt.datetime.strptime(month + "/" + day + "/2017 " + Hr+":"+Mn+":"+Ss, "%m/%d/%Y %H:%M:%S")
    inputDict = {}
    for i in ListVals:
        fileIn = root + '\\' + i
        fileName = open(fileIn,"r")
        lines = fileName.readlines()
        DateObjList = {}
        count = 1
        for line in lines:
            if line.split(',')[0] != '"Date"':
                elem = dt.datetime.strptime(line.split(',')[0].replace('"',''), "%m/%d/%Y %H:%M:%S")
                DateObjList[line.split(',')[0] + "_" + str(count)] = abs(elem-dateComp)
                count += 1
            else:
                count += 1
                
        
        
        
        
        ExcelRow = getNearestTime(DateObjList)
        inputDict[fileIn] = lines[int(ExcelRow.split("_")[1])-1]
    return inputDict
   


#loop through the directory of csv files
#check to see which files match our input month
for root, dirs, files in os.walk(rootDir):
    for filename in files:
        
        if filename.split('_')[-1][:-4] == "0" + month:
            listRef.append(filename)

#our variable storing our dictionary of csv weather gage data in a dictionary            
elem = findTemp(listRef)


#loop through the keys in the dictionary and grab each station ID and the associated value in degrees fahrenheit for air temp data
#store these values within the airTempField
for key in elem.keys():
    locId = int(key.split('\\')[-1][9:13])
    locIdVal = int(elem[key].split(',')[1].replace('"',''))
    print "STN_ID = {}".format(locId)
    arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", "STN_ID = {}".format(locId))
    
    
    arcpy.CalculateField_management("lyr", "airTemp", locIdVal, "PYTHON_9.3")
    





