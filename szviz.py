import vtk 
import xarray as xr
import numpy as np

# open the netcdf file
nc = xr.open_dataset('ds_climd03_sznalanomalies.nc')

# get the lon, lat
lon = nc['XLONG'][:].values
lat = nc['XLAT'][:].values

ny, nx = lat.shape # dimensions

lonRad = lon.reshape([nx*ny*1]) * np.pi/180. # convert to radians and flatten the array
latRad = lat.reshape([nx*ny*1]) * np.pi/180. # convert to radians and flatten the array

# get the field
sz = nc['sznanomaly1314'][:].values


# convert to Cartesian coordinates
xyz = np.zeros((nx*ny*1, 3), np.float64) # allocate space
radius = 1
xyz[:, 0] = radius * np.cos(latRad) * np.cos(lonRad) # x component
xyz[:, 1] = radius * np.cos(latRad) * np.sin(lonRad) # y component
xyz[:, 2] = radius * np.sin(latRad)

xyzArray = vtk.vtkDoubleArray() # VTK works only with VTK arrays
xyzArray.SetNumberOfComponents(3) # x, y, z
xyzArray.SetNumberOfTuples(nx*ny*1) # number of points
xyzArray.SetVoidArray(xyz, nx*ny*1*3, 1) # from numpy array to a VTK array
points = vtk.vtkPoints()
points.SetData(xyzArray)

# create a structured VTK grid
grid = vtk.vtkStructuredGrid()
grid.SetDimensions(nx, ny, 1)
grid.SetPoints(points)

# attach the field to the VTK grid
szArray = vtk.vtkDoubleArray()
szArray.SetNumberOfComponents(1) # scalar field
szArray.SetNumberOfTuples(nx*ny*1)
szArray.SetVoidArray(sz, nx*ny*1*1, 1)
szArray.SetName('sznanomaly1314')
grid.GetPointData().SetScalars(szArray)
print(f'min/max of sz: {sz.min()}/{sz.max()}')

# create a colourmap
lut = vtk.vtkLookupTable()
nc = 32
lut.SetNumberOfTableValues(nc)
for i in range(nc):
	x = i/(nc - 1) # in [0, 1]
	# negative part
	r = 0.
	g = 2*x
	b = 1.0
	alpha = 1.0 # opaque
	if x >= 0.5:
		# positive side
		r = 1.0
		g = 2*(1. - x)
		b = 0.
	lut.SetTableValue(i, r, g, b, alpha)
maxVal = 200.0
lut.SetRange(-maxVal, maxVal) # for runoff
lut.SetBelowRangeColor(0.5, 0.5, 0.5, 1.0)
lut.UseBelowRangeColorOn()
lut.SetAboveRangeColor(0., 1., 0., 1.0)
lut.UseAboveRangeColorOn()
lut.Build()
print(lut)

colorbar = vtk.vtkScalarBarActor()
colorbar.SetLookupTable(lut)
colorbar.Modified()

# create the VTK pipeline
gridMapper = vtk.vtkDataSetMapper() # this will colour your field
gridMapper.SetInputData(grid) # connect the grid with its field to the mapper
gridMapper.SetLookupTable(lut)
gridActor = vtk.vtkActor()
gridActor.SetMapper(gridMapper)

# render the field
# Create the graphics structure. The renderer renders into the render
# window. The render window interactor captures mouse events and will
# perform appropriate camera or actor manipulation depending on the
# nature of the events.
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(gridActor)
ren.AddActor(colorbar)
ren.SetBackground(1, 1, 1) # white
renWin.SetSize(900, 900)

# This allows the interactor to initalize itself. It has to be
# called before an event loop.
iren.Initialize()

renWin.Render()

# Start the event loop.
iren.Start()

