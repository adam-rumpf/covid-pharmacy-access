"""COVID-19 Vaccine accessibility project preprocessing scripts.

The code below includes various scripts for collecting data from a variety of
assorted raw data files and collecting them into summary files with a standard
format. The Google Maps API is used to convert addresses to coordinates where
needed.

Since each location included in the study organizes its data slightly
differently, a different function has been defined to perform the preprocessing
for each location.
"""

import os.path
import re

#==============================================================================
# Global Constants
#==============================================================================

# Population center file header (including column labels)
POP_HEADER = "id\tname\tlat\tlon\tpop\tvacc\tadi\t\n"

# Facility file header (including column labels)
FAC_HEADER = "id\tname\tlat\tlon\tcap\t\n"

#==============================================================================
# Common Functions
#==============================================================================

def point_to_coords(point):
    """Extracts the latitude/longitude from a GIS POINT object.
    
    Positional arguments:
        point (str) -- String of the format "POINT (LON LAT)".
    
    Returns:
        (tuple(float)) -- Latitude/longitude of the given address.
    """
    
    s = re.findall("[-.\d]+", point)
    return (float(s[1]), float(s[0]))

#==============================================================================
# Location-Specific Preprocessing Scripts
#==============================================================================

def process_chicago(popfile="chicago_pop.tsv", facfile="chicago_fac.tsv"):
    """Preprocessing scripts for the Chicago data.
    
    Optional keyword arguments:
        popfile (str) -- Population output file path. Defaults to a local file
            named "chicago_pop.tsv".
        facfile (str) -- Facility output file path. Defaults to a local file
            named "chicago_fac.tsv".
    """
    
    # Define location-specific file names
    case_file = os.path.join("chicago",
                           "COVID-19_Cases__Tests__and_Deaths_by_ZIP_Code.csv")
    fac_file = os.path.join("chicago", "COVID-19_Vaccination_Locations.csv")
    vacc_file = os.path.join("chicago","COVID-19_Vaccinations_by_ZIP_Code.csv")
    adi_file = os.path.join("chicago", "IL_2020_ADI_9 Digit Zip Code_v3.2.csv")
    
    # Initialize population center dictionary
    pop = dict()
    
    # Gather ZIP code locations and populations
    with open(case_file, 'r') as f:
        
        for line in f:
            
            # Skip comment line
            if line[0].isdigit() == False:
                continue
            
            s = line.split(',')
            zc = int(s[0]) # current row's ZIP code
            
            # Initialize empty entry for a new ZIP code
            if zc not in pop:
                pop[zc] = [0 for i in range(5)]
            
            # Gather coordinates and population
            pop[zc][0], pop[zc][1] = point_to_coords(s[-1])
            pop[zc][2] = max(pop[zc][2], int(s[18]))
    
    # Gather vaccination rates
    with open(vacc_file, 'r') as f:
        
        for line in f:
            
            # Skip comment line
            if line[0].isdigit() == False:
                continue
            
            s = line.split(',')
            zc = int(s[0]) # current row's ZIP code
            
            # Gather cumulative vaccinations
            try:
                pop[zc][3] += int(s[4])
            except ValueError:
                pass
    
    # Gather ADI rankings
    with open(adi_file, 'r') as f:
        
        # Initialize dictionary to group 9-digit ZIP codes by 5-digit code
        adi = dict([(zc, [0, 0]) for zc in pop])
        
        for line in f:
            
            s = line.replace('"', '').split(',')
            
            # Skip comment line
            if s[0][0].isdigit() == False:
                continue
            
            # Take 5-digit header
            zc = int(s[0][:5])
            if zc not in pop:
                continue
            
            # Add ADI ranking to tally
            try:
                adi[zc][0] += int(s[4])
                adi[zc][1] += 1
            except ValueError:
                pass
        
        # Average 9-digit values across 5-digit codes
        for zc in pop:
            if adi[zc][1] > 0:
                pop[zc][4] = adi[zc][0]/adi[zc][1]
    
    # Write population output file
    with open(popfile, 'w') as f:
        f.write(POP_HEADER)
        sk = sorted(pop.keys())
        for i in range(len(sk)):
            line = str(i) + '\t' + str(sk[i]) + '\t'
            for item in pop[sk[i]]:
                line += str(item) + '\t'
            f.write(line + '\n')
    
    # Initialize facility dictionary
    fac = dict()
    
    # Write facility output file
    with open(facfile, 'w') as f:
        f.write(FAC_HEADER)
        ###

#------------------------------------------------------------------------------

def process_santa_clara(popfile="santa_clara_pop.tsv",
                        facfile="santa_clara_fac.tsv"):
    """Preprocessing scripts for the Santa Clara data.
    
    Optional keyword arguments:
        popfile (str) -- Population output file path. Defaults to a local file
            named "santa_clara_pop.tsv".
        facfile (str) -- Facility output file path. Defaults to a local file
            named "santa_clara_fac.tsv".
    """
    
    # Define location-specific file names
    adi_file = os.path.join("santa_clara",
                            "CA_2020_ADI_Census Block Group_v3.2.csv")
    census_file = os.path.join("santa_clara", "CensusTract2020.csv")
    vacc_file = os.path.join("santa_clara",
             "COVID-19_Vaccination_among_County_Residents_by_Census_Tract.csv")
    
    ###
    
    # Write population output file
    with open(popfile, 'w') as f:
        f.write(POP_HEADER)
        ###
    
    # Write facility output file
    with open(facfile, 'w') as f:
        f.write(FAC_HEADER)
        ###

#==============================================================================
# Execution
#==============================================================================

# Comment or uncomment the function calls below to process each location.
process_chicago()
process_santa_clara()
