@echo off
set "source_directory=C:\Users\thodoris"
set "destination_directory=C:\Users\thodoris\Documents\Python_Scripts\s3\s3\data"

rem Unzip all .zip files in the source directory
for %%F in ("%source_directory%\*.zip") do (
    "C:\Program Files\7-Zip\7z.exe" x "%%F" -o"%destination_directory%" -y
)

rem Move the .zip files to a different directory (optional)
move "%source_directory%\*.zip" "%destination_directory%"

rem Move a single file (if needed)
rem move "%source_directory%\file_name.ext" "%destination_directory%\"

rem Move multiple files with a specific extension (e.g., .txt) (if needed)
rem for %%F in ("%source_directory%\*.txt") do (
rem     move "%%F" "%destination_directory%\"
rem )
