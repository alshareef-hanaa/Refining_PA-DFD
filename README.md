
Prerequisites
------------

 - DFD Refinery is written in Python, which can be run by interpreter that is Python 3.7 or later. Python 3.7 can be dowmload from (https://www.python.org/downloads/) 
 
 - Download draw.io from (https://about.draw.io/integrations/#integrations_offline) for drawing DFDs
 
 - Draw.io does not come with dedicated libraries for DFDs, download libraries for DFD from  (https://github.com/michenriksen/drawio-threatmodeling)

Usage
------------

1- Draw your DFD by using draw.io

2- Export xml files of DFDs from draw.io

3- Clone the [GitHub repository](https://github.com/alshareef-hanaa/Refining_PA-DFD.git):
  
  $ git clone https://github.com/alshareef-hanaa/Refining_PA-DFD.git

4- DFD Refinery tool comprises three algorithms: Refinement Checking, Refinement Search and Refinement Transformation. DFD Refinery also includes an updated version
of our previous tool for transforming B-DFDs into PA-DFDs. 


   Refinement Checking:
   -------------------
   
   1- Go into the directory where the script (Refinement_Checking.py) and the xml files of DFDs (abstract and concrete), which you have exported in step 2 in             Usage.
   
   2- To run the script (Refinement_Checking.py) from the terminal, you need to provide the file names of the csv files for DFDs (abstract and concrete), xml files      for DFDs (abstract and concrete) and csv files for abstraction DFDs (nodes and flows) as arguments, use the following command:
   
     $ python Refinement_Checking.py "the name of DFD abstract level xml file" "the name of DFD abstract level csv file" "the name of DFD concrete level xml file"          "the name of DFD concrete level csv file" "the name of nodes abstraction DFDs csv file" "the name of flows abstraction DFDs csv file"
    

   Refinement Search:
   ------------------
   
   

   Refinement Transformation:
   --------------------------
   
   
   1- To obtain the abstraction of PA-DFDs first, we transform the abstract and concrete DFDs. Go into the directory where the script (Transformation_DFD_PADFD.py)       and the xml files of DFDs (abstract and concrete), which you have exported in step 2 in Usage.
   
   2- For each DFD run the script (Transformation_DFD_PADFD.py) from the terminal, you need to provide the file names of csv file for DFD, csv file for PA-DFD, csv       file for tracking maps and xml file for DFD as arguments, use the following command:
   
    $ python Transformation_DFD_PADFD.py "the name of DFD xml file" "the name of DFD csv file" 
      "the name of PA-DFD csv file" "the name of tracking maps csv file" 
      
   3- To run the script (Refinement_Transformation.py) from the terminal, you need to provide the file names of the csv files for tracking maps and csv files for        PA-DFDs, which are produced from the previous step, as arguments. Also, csv file for abstraction DFDs obtained from executing Refinement Checking or
     Refinement Search. The last argument that needs to be provided is csv file for abstraction PA-DFDs, use the following command:
     
    $ python Refinement_Transformation.py "the name of tracking map (DFD abstract level) csv file" "the name of tracking map (DFD concrete level) csv file" 
      "the name of PA-DFD abstract level csv file" "the name of PA-DFD concrete level csv file" "the name of nodes abstraction DFDs csv file" "the name of flows            abstraction DFDs csv file" "the name of abstraction PA-DFDs csv file" 
      
      
     
      
   
   
    
