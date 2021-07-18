import os

def find_files(path, year, jday):
    """
    Returns list of file names that match the given parameters.

    Parameter path: Path to directory of files
    Precondition: path is a str
    
    Parameter year: Year of file(s) to be found
    Precondition: year is a str
    
    Parameter jday: Julian day of file(s) to be found
    Precondition: jday is a str
    """
    files = []
    for file in os.listdir(path):
        sub = file[file.find('s'):-4]
        if sub[1:5] == year and sub[5:8] == jday:
            files.append(file)
    return files

def delete_files(path, year, jday):
    """
    Deletes all files from a given day in a given year.

    Parameter path: Path to directory of files
    Precondition: path is a str
    
    Parameter year: Year of file(s) to be found
    Precondition: year is a str
    
    Parameter jday: Julian day of file(s) to be found
    Precondition: jday is a str
    """
    for file in find_files(path, year, jday):
        os.remove(path + file)