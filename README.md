# Display Polygon Information

This tool is a utility tool for maya artists to easily visualize mesh specific information
on the viewport. It will display information such as the vertex, face or edge id's for the
specified component on a selected mesh in the viewport

## Instructions on loading the tool

- Extract the src, images and Videos files to a relevant folder path on your local machine
- Open the maya python editor in a running maya session
- Within the src folder, copy the precision_tool.py file
- Paste this into the python editor and run the tool
- Optionally, create a new shelf button, within the python tab, paste this script
- Then click Apply and OK.
- This will create a shelf button which will activate this script in future maya sessions
- If the tool prompts you with an empty field
- Paste the path to the src, images and Videos main folder path into this field and click OK
- This will load the tool in successfully
  
## Instructions on using the tool

- Toggle on a relevant mesh component you want to visualize by clicking on its
  name in the tool's user interface. For instance, if you want to display all vertices on the
  currently selected mesh, click this toggle on and give it time to simulate.
- Toggle 1-2 component displays at once. Further displays can cause viewport lag or
  crash the current maya session
- Type in a specific name into the name empty field while selecting a mesh component to rename
  the component to a desired name

## Further improvements

- Improving viewport lag performance issues
- Creating a custom context tool using OpenMaya libraries
- Binding the displays to the mesh as it moves around the viewport.

