# pyLessSDK Examples

## ForestSceneBuilder Examples

### Minimal: Create a forest scene from LAI and FCC

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from ForestSceneBuilder import ForestSceneBuilder, ForestType

builder = ForestSceneBuilder(r"D:\LESS", r"D:\Simulations", "broadleaf01")
builder.set_canopy_params(lai=3.0, fcc=0.6)
builder.set_forest_type(ForestType.BROADLEAF_NATURAL)
builder.build()
builder.run()
```

### Coniferous plantation with PROSPECT-D leaf optics

```python
from ForestSceneBuilder import ForestSceneBuilder, ForestType
from SimpleCrownGenerator import LAD

builder = ForestSceneBuilder(r"D:\LESS", r"D:\Simulations", "conifer01",
                              scene_x_size=50, scene_y_size=50)
builder.set_canopy_params(lai=4.5, fcc=0.7, lad=LAD.ERECTOPHILE)
builder.set_forest_type(ForestType.CONIFEROUS_PLANTATION)
builder.spectral_bands = [550, 650, 850]
builder.set_optical_from_prospect(N=1.8, Cab=40, Car=10, Cw=0.012, Cm=0.009)
builder.build()
```

### Mixed natural forest with custom species ratio

```python
builder = ForestSceneBuilder(r"D:\LESS", r"D:\Simulations", "mixed01")
builder.set_canopy_params(lai=4.0, fcc=0.7)
builder.set_forest_type(ForestType.MIXED_NATURAL)
builder.species_mix = {"broadleaf": 0.6, "coniferous": 0.4}
builder.build()
```

### Savanna with dense understory

```python
builder = ForestSceneBuilder(r"D:\LESS", r"D:\Simulations", "savanna01",
                              scene_x_size=80, scene_y_size=80)
builder.set_canopy_params(lai=0.8, fcc=0.15)
builder.set_forest_type(ForestType.SAVANNA)
builder.crown_diameter_mean = 5.0
builder.understory_lai = 1.2
builder.understory_height = 0.5
builder.build()
```

### Render a perspective image after building

```python
from Sensor import SensorPerspective
from Observation import ObservationPerspective

builder = ForestSceneBuilder(r"D:\LESS", r"D:\Simulations", "render01",
                              scene_x_size=40, scene_y_size=40)
builder.set_canopy_params(lai=3.5, fcc=0.65)
builder.set_forest_type(ForestType.BROADLEAF_NATURAL)
builder.spectral_bands = [650, 550, 450]  # RGB
builder.solar_zenith = 35
builder.build()

# Switch to perspective camera after build()
sim = builder.get_simulation()
scene = sim.get_scene()

sensor = SensorPerspective()
sensor.set_fov_x(50)
sensor.set_fov_y(40)
sensor.set_image_width(800)
sensor.set_image_height(640)
sensor.set_sample_per_pixel(16)
sensor.set_spectral_bands("650:1,550:1,450:1")
scene.set_sensor(sensor)

obs = ObservationPerspective()
obs.set_origin((-12, -12, 60))
obs.set_target((20, 20, 6))
scene.set_observation(obs)

sim.save_sim_project()
sim.start()
```

### Triangle mesh mode (non-turbid) with custom parameters

```python
builder = ForestSceneBuilder(r"D:\LESS", r"D:\Simulations", "mesh01")
builder.set_canopy_params(lai=3.0, fcc=0.5)
builder.set_forest_type(ForestType.CONIFEROUS_NATURAL)
builder.leaf_as_turbid = False        # use triangle mesh
builder.crown_diameter_mean = 4.0     # override auto-derived
builder.num_templates = 5             # 5 template trees
builder.has_understory = True
builder.understory_lai = 0.3
builder.build()
```

---

## Example 1: Basic Orthographic Image

Simulate a nadir spectral image of trees over flat terrain.

```python
import sys, os, random
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from SceneObjects import SceneObject
from OpticalProperty import OpticalItem
from Sensor import SensorOrthographic
from Observation import ObservationOrthographic
from PostProcessing import PostProcessing

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\ex01"
sim_helper = SimulationHelper(less_dir)
sim_helper.create_new_sim(sim_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()
landscape = scene.get_landscape()
landscape.clear_landscape_elements()
landscape.clear_user_defined_optical_properties()

# Optical properties: 3 bands (R, G, B)
op_leaf = OpticalItem("leaf_green", "0.05,0.45,0.05;0.05,0.45,0.05;0.02,0.40,0.02")
landscape.add_op_item(op_leaf)

# Add tree
obj = SceneObject("Tree01")
obj.add_component_from_file(r"D:\LESS\app\Database\3D_Objects\Trees\RAMI\ww_10.obj", "leaf_green")
landscape.add_object(obj)

# Random placement
for _ in range(80):
    landscape.place_object("Tree01", x=random.uniform(5, 95), y=random.uniform(5, 95))

# Terrain
terrain = landscape.get_terrain()
terrain.set_extent_width(100)
terrain.set_extent_height(100)
terrain.set_optical("dark_soil_mollisol")

# Sensor
sensor = SensorOrthographic()
sensor.set_spectral_bands("680:2,550:2,450:2")
sensor.set_image_width(512)
sensor.set_image_height(512)
sensor.set_sample_per_pixel(128)
scene.set_sensor(sensor)
scene.set_observation(ObservationOrthographic())

# Illumination
ill = scene.get_illumination()
ill.set_sun_zenith(30)
ill.set_sun_azimuth(180)

sim.save_sim_project()
sim.start()
PostProcessing.radiance2brf(sim.get_sim_dir())
```

---

## Example 2: Batch Simulation (Varying Sun Angles)

Run multiple simulations changing only the sun zenith angle.

```python
import sys, os
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from PostProcessing import PostProcessing

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\batch_sun"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()

for sza in [15, 30, 45, 60]:
    scene.get_illumination().set_sun_zenith(sza)
    sim.set_dist_file(os.path.join(sim.get_sim_dir(), "Results", f"output_sza{sza}"))
    sim.save_sim_project()
    sim.start()
    PostProcessing.radiance2brf(sim.get_sim_dir())
```

---

## Example 3: LiDAR Simulation (Airborne)

Simulate airborne LiDAR point cloud.

```python
import sys, os
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Sensor import SensorLiDAR
from LiDAR import ALSLiDAR, LiDARSimMode
from PostProcessing import PostProcessing

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\lidar"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()

# ALS configuration
sensor = SensorLiDAR()
als = ALSLiDAR()
als.platform.altitude = 800
als.platform.startX = 5
als.platform.startY = 50
als.platform.endX = 95
als.platform.endY = 50
als.platform.swathWidth = 90
als.platform.rangeResolution = 0.5
als.platform.yawResolution = 0.5
als.platform.minRange = 770
als.platform.maxRange = 805
als.beam.axialDivision = 30
als.beam.maxOrder = 2
als.set_lidar_sim_mode(LiDARSimMode.MultiRayPointCloud)
sensor.set_scanning_device(als)
scene.set_sensor(sensor)

sensor.set_spectral_bands("1064:2")  # LiDAR wavelength

sim.save_sim_project()
sim.start()

# Convert to LAS
terrain = scene.get_landscape().get_terrain()
PostProcessing.multiray_pointcloud_txt2las(
    os.path.join(sim.get_sim_dir(), "Results"),
    terrain.get_extent_height()
)
```

---

## Example 4: Multi-Angle BRF with Photon Tracing

Compute BRF at multiple viewing directions.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Sensor import SensorPhotonTracing
from Observation import ObservationPhotonTracing

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\brf"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()

sensor = SensorPhotonTracing()
sensor.set_spectral_bands("680:2,550:2,450:2")
sensor.enable_brf_product(True)
sensor.set_sun_ray_resolution(0.5)
sensor.set_number_of_directions(150)

# Virtual observation directions: zenith:azimuth pairs
directions = ";".join([f"{zen}:{azi}" for zen in range(0, 70, 10) for azi in [0, 90, 180, 270]])
sensor.set_virtual_directions(directions)
scene.set_sensor(sensor)
scene.set_observation(ObservationPhotonTracing())

sim.save_sim_project()
sim.start()
```

---

## Example 5: Perspective Camera Image

Generate a perspective view looking at the scene from a height.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Sensor import SensorPerspective
from Observation import ObservationPerspective

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\perspective"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()

sensor = SensorPerspective()
sensor.set_spectral_bands("680:2,550:2,450:2")
sensor.set_image_width(800)
sensor.set_image_height(600)
sensor.set_fov_x(60)
sensor.set_fov_y(45)
sensor.set_sample_per_pixel(256)
scene.set_sensor(sensor)

obs = ObservationPerspective()
obs.set_origin((10, 50, 80))     # camera position
obs.set_target((50, 50, 5))      # look-at point
scene.set_observation(obs)

sim.save_sim_project()
sim.start()
```

---

## Example 6: Fisheye Camera (Hemispherical Photo)

Simulate a hemispherical photograph from below canopy.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Sensor import SensorFisheye
from Observation import ObservationFisheye

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\fisheye"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()

sensor = SensorFisheye()
sensor.set_spectral_bands("550:2")
sensor.set_image_width(512)
sensor.set_image_height(512)
sensor.set_angular_fov(165)
sensor.set_projection_type("equisolid")
sensor.set_sample_per_pixel(256)
scene.set_sensor(sensor)

obs = ObservationFisheye()
obs.set_origin((50, 50, 1))      # 1m above ground at scene center
obs.set_target((50, 50, 100))    # looking up
scene.set_observation(obs)

sim.save_sim_project()
sim.start()
```

---

## Example 7: Turbid Medium (Abstract Crown)

Use turbid media for abstract crown representations (no explicit leaf geometry).

```python
import sys, random
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from SceneObjects import SceneObject
from OpticalProperty import OpticalItem
from Sensor import SensorOrthographic
from Observation import ObservationOrthographic

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\turbid"
sim_helper = SimulationHelper(less_dir)
sim_helper.create_new_sim(sim_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()
landscape = scene.get_landscape()
landscape.clear_landscape_elements()
landscape.clear_user_defined_optical_properties()

op_leaf = OpticalItem("leaf_op", "0.05,0.45;0.05,0.45;0.02,0.40")
landscape.add_op_item(op_leaf)

# Turbid crown: the OBJ defines the crown volume, scattering is volumetric
obj = SceneObject("TurbidTree")
obj.add_component_from_file(
    r"path/to/crown_ellipsoid.obj",
    "leaf_op",
    is_turbid=True,             # key: enables turbid medium
    leaf_density=1.5,           # leaf area density (m2/m3)
    lad="Spherical",            # leaf angle distribution
    hotspot_factor=0.1          # hotspot correction
)
obj.add_component_from_file(r"path/to/trunk.obj", "birch_branch")
landscape.add_object(obj)

for _ in range(40):
    landscape.place_object("TurbidTree", x=random.uniform(5, 95), y=random.uniform(5, 95))

sensor = SensorOrthographic()
sensor.set_spectral_bands("680:2,550:2")
sensor.set_image_width(256)
sensor.set_image_height(256)
scene.set_sensor(sensor)
scene.set_observation(ObservationOrthographic())

sim.save_sim_project()
sim.start()
```

---

## Example 8: Runtime Modification (Batch with Dynamic Properties)

Modify optical properties between runs without reloading the full scene.

```python
import sys, os
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from OpticalProperty import OpticalItem
from PostProcessing import PostProcessing

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\runtime"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

# Enable runtime modification
sim.enable_runtime_modification_of_properties(True)

scene = sim.get_scene()
landscape = scene.get_landscape()

# Run with different leaf reflectances
for nir_ref in [0.3, 0.4, 0.5, 0.6]:
    op = landscape.get_op_item("leaf_green")
    op.set_op_value(f"0.05,{nir_ref};0.05,{nir_ref};0.02,{nir_ref * 0.8}")

    sim.set_dist_file(os.path.join(sim.get_sim_dir(), "Results", f"nir_{nir_ref}"))
    sim.save_sim_project()
    sim.start()

# After structural changes, reload
sim.reload_runtime_structural_properties()
```

---

## Example 9: DEM Terrain with Atmosphere Model

Simulation over hilly terrain with 6S atmosphere model.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Terrain import TERRAIN_TYPE
from Illumination import Atmosphere6S
from Sensor import SensorOrthographic
from Observation import ObservationOrthographic

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\dem_atm"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()
landscape = scene.get_landscape()

# DEM terrain
terrain = landscape.get_terrain()
terrain.set_extent_width(200)
terrain.set_extent_height(200)
terrain.set_terrain_type(TERRAIN_TYPE.RASTER)
terrain.set_terrain_file(r"D:\data\dem.tif")

# 6S atmosphere
ill = scene.get_illumination()
ill.set_sun_zenith(35)
ill.set_sun_azimuth(150)
ill.set_ats_type("ATMOSPHERE")
ill.set_ats_model("6S")

atm = Atmosphere6S()
atm.ats_profile = "MidlatitudeSummer"
atm.aot_550 = 0.2
atm.aero_profile = "Continental"
atm.target_altitude = 0
atm.month = 7
atm.day = 1
ill.set_ats_model_params(atm)

sensor = SensorOrthographic()
sensor.set_spectral_bands("680:2,550:2,450:2,850:2")
sensor.set_image_width(512)
sensor.set_image_height(512)
scene.set_sensor(sensor)
scene.set_observation(ObservationOrthographic())

sim.save_sim_project()
sim.start()
```

---

## Example 10: TRAC Transect Gap Fraction Measurement

Simulate TRAC-like gap fraction measurements along a transect.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Sensor import SensorTRAC

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\trac"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()

# TRAC sensor: measures gap fraction along a transect line
sensor = SensorTRAC()
sensor.set_spectral_bands("680:2")
sensor.set_startPos("5,50,1")        # start at (5,50) at 1m height
sensor.set_endPos("95,50,1")         # end at (95,50) at 1m height
sensor.set_step(0.05)                # 5cm step size
sensor.set_number_rays(30)           # 30 rays per measurement point
scene.set_sensor(sensor)

sim.save_sim_project()
sim.start()
```

---

## Example 11: LAI and CHM Analysis

Compute scene-level LAI and canopy height model.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\my_scene"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

landscape = sim.get_scene().get_landscape()

# Total scene LAI
lai = landscape.compute_scene_lai()
print(f"Scene LAI: {lai}")

# 3D LAI voxel grid
landscape.compute_lai3d(r"D:\output\lai3d.txt", rows=20, cols=20, layers=30)

# Canopy Height Model (raster)
landscape.compute_chm(r"D:\output\chm.tif", resolution=0.5)

# Crown radius statistics
landscape.compute_crown_radius(r"D:\output\crown_radius.txt",
                                out_mask_img_file=r"D:\output\crown_mask.tif",
                                mask_img_resolution=0.5)
```

---

## Example 12: fPAR and Fluorescence Simulation

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Sensor import SensorPhotonTracing
from Observation import ObservationPhotonTracing

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\fpar_fluor"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()

sensor = SensorPhotonTracing()
sensor.set_spectral_bands("680:2,550:2,760:2")
sensor.set_sun_ray_resolution(0.5)

# Enable fPAR
sensor.enable_fpar_product(True)
sensor.set_fpar_layer("0:2:20")  # layers from 0m to 20m, step 2m

# Enable fluorescence (requires Fluspect optical properties)
sensor.enable_Fluor_product(True)

# Enable up/down radiation
sensor.enable_updown_radiation_product(True)

scene.set_sensor(sensor)
scene.set_observation(ObservationPhotonTracing())

sim.save_sim_project()
sim.start()
```

---

## Example 13: Object Placement with Scaling and Rotation

Place objects with individual scale and rotation.

```python
import sys, random, math
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation

sim_helper = SimulationHelper(r"D:\LESS")
sim = Simulation(r"D:\Simulations\placement", sim_helper)
sim.read_sim_project()

landscape = sim.get_scene().get_landscape()

# Place with rotation (degrees around Y-axis)
landscape.place_object("Tree01", x=30, y=30, rotate=45)

# Place with 3D scale (absolute extents in meters)
landscape.place_object("Tree01", x=60, y=60,
                       scale_extent_x=3.0,   # crown width X
                       scale_extent_y=8.0,    # height
                       scale_extent_z=3.0)    # crown width Z

# Place with custom rotation axes
landscape.place_object("Tree01", x=50, y=50,
                       rotate=30,
                       rotate_axis_x=0, rotate_axis_y=1, rotate_axis_z=0)

# Random forest with varying sizes
for _ in range(100):
    h = random.uniform(5, 20)
    w = random.uniform(2, 6)
    landscape.place_object("Tree01",
                           x=random.uniform(5, 95),
                           y=random.uniform(5, 95),
                           rotate=random.uniform(0, 360),
                           scale_extent_x=w,
                           scale_extent_y=h,
                           scale_extent_z=w)

sim.save_sim_project()
sim.start()
```

---

## Example 14: Multi-Angle Orthographic Images for Per-Pixel BRDF

Simulate co-registered multi-angle orthographic images. Key: enable `is_orthophoto_map` to reproject
oblique views onto the ground plane so all angles are pixel-aligned.

```python
import sys, os
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Sensor import SensorOrthographic
from Observation import ObservationOrthographic
from PostProcessing import PostProcessing

less_dir = r"D:\LESS"
sim_dir = r"D:\Simulations\multiangle_brdf"
sim_helper = SimulationHelper(less_dir)
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()

scene = sim.get_scene()
terrain = scene.get_landscape().get_terrain()
extent_w = terrain.get_extent_width()
extent_h = terrain.get_extent_height()

# Orthographic sensor — sub_region matches scene extent
sensor = SensorOrthographic()
sensor.set_spectral_bands("680:1,550:1,450:1")
sensor.set_image_width(512)
sensor.set_image_height(512)
sensor.set_sub_region_width(extent_w)
sensor.set_sub_region_height(extent_h)
sensor.set_sample_per_pixel(128)
scene.set_sensor(sensor)

# Enable runtime modification for batch efficiency
sim.enable_runtime_modification_of_properties(True)

# Multi-angle loop
view_zeniths = [0, 15, 30, 45, 60]
view_azimuths = [0, 90, 180, 270]

sensor.set_repetitive_scene(100)  # large value to avoid edge effects (flat terrain only)

for zen in view_zeniths:
    for azi in view_azimuths:
        obs = ObservationOrthographic()
        obs.set_obs_zenith(zen)
        obs.set_obs_azimuth(azi)
        obs.is_orthophoto_map = True        # critical: ground-plane reprojection
        obs.orthophoto_relative_height = 0  # reference height
        scene.set_observation(obs)

        sim.set_dist_file(os.path.join(sim.get_sim_dir(), "Results", f"zen{zen}_azi{azi}"))
        sim.save_sim_project()
        sim.start()
        PostProcessing.radiance2brf(sim.get_sim_dir())

# All output images are co-registered: same pixel = same ground location
# Stack them to extract per-pixel BRDF across viewing angles
```

---

## Example 15: PROSPECT-D Leaf Optics and GSV Soil Model

Use physics-based models to generate optical properties.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from Prospect5AndD import prospectD
from GSVSoil import GSVSoil
from OpticalProperty import OpticalItem

# PROSPECT-D: compute leaf reflectance/transmittance at specific wavelengths
wavelengths = [450, 550, 680, 850]
ref, trans = prospectD(wl=wavelengths, N=1.5, Cab=40, Car=8, Cw=0.01, Cm=0.009, Anth=0, BP=0)
print(f"Leaf reflectance: {ref}")
print(f"Leaf transmittance: {trans}")

# Build OpticalItem from PROSPECT-D output
ref_str = ",".join([f"{r:.4f}" for r in ref])
trans_str = ",".join([f"{t:.4f}" for t in trans])
op_leaf = OpticalItem("prospect_leaf", f"{ref_str};{ref_str};{trans_str}")

# GSV Soil: compute soil reflectance
gsv = GSVSoil()
soil_ref = gsv.get_soil_spectra_gsv3(
    wavelength=wavelengths,
    c1=0.5,    # brightness
    c2=0.1,    # shape
    c3=0.05,   # shape
    csm=-0.2   # moisture (-0.6 to 0, 0=dry)
)
print(f"Soil reflectance: {soil_ref}")

soil_ref_str = ",".join([f"{r:.4f}" for r in soil_ref])
op_soil = OpticalItem("gsv_soil", f"{soil_ref_str};{soil_ref_str};0,0,0,0")
```

---

## Example 15: SDKCodeGenerator — Convert GUI Project to Script

Reverse-engineer a LESS GUI simulation into a reproducible Python script.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SDKCodeGenerator import SDKCodeGenerator

# Point to an existing LESS simulation directory (created via GUI)
gen = SDKCodeGenerator(r"D:\Simulations\my_gui_project")

# Generate a complete Python script that recreates the simulation
gen.generate(r"D:\output\generated_script.py")

# The generated script can be modified and rerun programmatically
```

---

## Example 16: CrownGenerator — Custom Tree OBJ Generation

Generate custom tree crown OBJ files from parameters.

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
from SimpleCrownGenerator import CrownGenerator, CrownShape, LAD, LeafShape

gen = CrownGenerator()

# Crown geometry
gen.crown_shape = CrownShape.ELLIPSOID.value
gen.crown_diameter_SN = 4.0    # crown diameter south-north (m)
gen.crown_diameter_EW = 4.0    # crown diameter east-west (m)
gen.crown_height = 6.0         # crown height (m)

# Leaf properties
gen.leaf_volume_density = 1.2  # leaf area density (m2/m3)
gen.leaf_angle_dist = LAD.SPHERICAL.value
gen.leaf_shape = LeafShape.DISK.value
gen.single_leaf_area = 0.001   # individual leaf area (m2)

# Trunk
gen.has_trunk = True
gen.trunk_height = 8.0
gen.dbh = 0.2

# Branches
gen.has_branches = True

# Clumping
gen.clumping_factor = 0.8

# Generate OBJ file
gen.generate_crown(r"D:\output\custom_tree.obj")
```
