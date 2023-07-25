#!/bin/bash

source_directory="C:/Users/thodoris"
destination_directory="C:/Users/thodoris/Documents/Python Scripts/s3/s3/data"



# Unzip all .zip files in the source directory
#for zip_file in "${source_directory}"/*.zip; do
chmod +r "C:\Users\thodoris\bisias.zip"
unzip -o "C:\Users\thodoris\bisias.zip" -d "${destination_directory}"
#done

# Move the .zip files to a different directory (optional)
mv "C:\Users\thodoris\bisias.zip" "${destination_directory}/"

# Move a single file (if needed)
# mv "${source_directory}/file_name.ext" "${destination_directory}/"

# Move multiple files with a specific extension (e.g., .txt) (if needed)
# for file in "${source_directory}"/*.txt; do
#     mv "$file" "${destination_directory}/"
# done
