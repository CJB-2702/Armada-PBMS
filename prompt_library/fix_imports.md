
# Renaming a file folder or class

you are a refactoring expert focused around fixing imports and changing the names of classes and files to better match what the objects and files do,

add the following files to context
/design/ApplicationDesign.md
/design/ApplicationStructure.json
/design/SystemDesign.md
app/utils/_build_structure_summary.py

Run build structure summary.py and update the current build structure FIRST

Then ask the user to describe the changes made 

review the System design structure
review the layered archetecture in the structure
do your best to scan associated files  with changes and fix imports and class names
work from the datalayer, buisness, services, then presentation/routes checking the routes and functions related to the changes first

attempt to pycompile files that appear effected

run z_clear_data
then do a 
activate venv
(venv) python app.py --build
then try 
to run the app
start an automated run debug fix cycle
if the same error pops up three times prompt the user to do a manual review , specify where you think the error might be
if the app runs without visable problems
prompt the user to run the application in their own terminal
if the user says the app appears ok, review the design docs above and integrate the changes to the documents. do not describe the changes made, remove old refrences to paths and files and update them to the new paths files and names


