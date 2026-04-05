---
name: less-sdk
description: "Guide for using the LESS radiative transfer model via pyLessSDK. Use when the user asks to create, configure, or run LESS simulations, set up scenes with vegetation/terrain, configure sensors (orthographic, perspective, fisheye, LiDAR, TRAC, photon tracing), define optical properties, or post-process simulation results."
argument-hint: "[task description]"
---

# LESS Radiative Transfer Model — pyLessSDK Guide

You are helping a user write Python code to drive the LESS (LargE-Scale remote sensing data and image simulation framework) 3D radiative transfer model using **pyLessSDK**.

The user's task: **$ARGUMENTS**

## LESS Installation Path Discovery

Before generating any code, you MUST determine where LESS is installed. Follow this priority order:

1. **Check user's CLAUDE.md** for a line like `LESS installation directory: <path>` or `LESS_ROOT: <path>`
2. **Check environment variable** `LESS_ROOT`
3. **Check common locations**: `D:\LESS`, `C:\LESS`, `~/LESS`, or a path containing `lessrt`
4. **Ask the user** if none of the above yields a valid path

Once found, use the path consistently for both `SimulationHelper(less_dir)` and the `sys.path.insert` import.

Similarly, determine the **pyLessSDK path**:
- If LESS is an installed distribution: `<LESS_ROOT>/app/Python_script/pyLessSDK`
- If working from the source repo: `<repo_root>/Utility/Python_script/pyLessSDK`

### Bundled Python Interpreter

LESS ships with a bundled Python interpreter — users do NOT need to install Python separately:
- **Windows**: `<LESS_ROOT>/app/bin/python/python.exe`
- **Linux**: `<LESS_ROOT>/app/bin/py312_linux/bin/python`

When running simulation scripts, prefer using this bundled interpreter as it includes all required dependencies (NumPy, etc.). For example:
```bash
# Windows
D:\LESS\app\bin\python\python.exe my_simulation.py

# Linux
/opt/LESS/app/bin/py312_linux/bin/python my_simulation.py
```

**Tip for users**: Add this line to your project's `CLAUDE.md` to avoid being asked every time:
```
LESS installation directory: D:\LESS
```

## Architecture Overview

LESS simulates spectral remote sensing images over heterogeneous 3D scenes. The Python SDK (`Utility/Python_script/pyLessSDK/`) orchestrates simulations by:

1. Configuring a **Scene** (landscape + terrain + illumination + sensor + observation)
2. Writing a JSON config (`Parameters/input.conf`) and Mitsuba XML scene files
3. Invoking the C++ radiative transfer core (`lessrt.exe`) via Mitsuba bindings
4. Post-processing outputs (radiance -> BRF, brightness temperature, LAS point clouds, etc.)

```
SimulationHelper -> Simulation -> Scene
                                  |-- Landscape (objects, instances, optical properties)
                                  |     +-- Terrain (DEM, BRDF)
                                  |-- Sensor (orthographic, perspective, fisheye, photon tracing, LiDAR, TRAC)
                                  |-- Observation (viewing geometry)
                                  |-- Illumination (sun position, atmosphere)
                                  +-- AdvancedParams (cores, iterations)
```

## Import Pattern

pyLessSDK is NOT installed as a package. Add its parent directory to `sys.path`:

```python
import sys
sys.path.insert(0, r"<LESS_ROOT>/Utility/Python_script/pyLessSDK")
# For installed LESS distribution, use:
# sys.path.insert(0, r"<LESS_ROOT>/app/Python_script/pyLessSDK")

from SimulationHelper import SimulationHelper
from Simulation import Simulation
from SceneObjects import SceneObject
from OpticalProperty import OpticalItem, OpticalItemType
from Sensor import SensorOrthographic, SensorPerspective, SensorFisheye, SensorPhotonTracing, SensorLiDAR, SensorTRAC
from Observation import ObservationOrthographic, ObservationPerspective, ObservationFisheye
from Illumination import Illumination, Atmosphere6S, SunPositionCalculator
from Terrain import TERRAIN_TYPE, TERRAIN_BRDF_TYPE
from PostProcessing import PostProcessing
from LiDAR import ALSLiDAR, TLSLiDAR, LiDARSimMode
from SimpleCrownGenerator import LAD, CrownShape, LeafShape, CrownGenerator
from Prospect5AndD import prospectD
from GSVSoil import GSVSoil
from SDKCodeGenerator import SDKCodeGenerator
```

## Minimal Complete Workflow

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

# 1. Setup
less_dir = r"D:\LESS"                    # LESS installation root
sim_dir = r"D:\Simulations\my_sim"       # simulation workspace
sim_helper = SimulationHelper(less_dir)
sim_helper.create_new_sim(sim_dir)       # creates directory + default config

# 2. Load project
sim = Simulation(sim_dir, sim_helper)
sim.read_sim_project()
scene = sim.get_scene()
landscape = scene.get_landscape()

# 3. Clear defaults and add custom optical properties
landscape.clear_landscape_elements()
landscape.clear_user_defined_optical_properties()
op_leaf = OpticalItem("leaf_green", "0.05,0.45;0.05,0.45;0.02,0.40")
#                      name          front_ref;back_ref;transmittance  (per band, comma-sep)
landscape.add_op_item(op_leaf)

# 4. Add 3D object and place instances
obj = SceneObject("Birch")
obj.add_component_from_file(r"path/to/birch_crown.obj", "leaf_green")
obj.add_component_from_file(r"path/to/birch_trunk.obj", "birch_branch")  # built-in op
landscape.add_object(obj)
for _ in range(50):
    landscape.place_object("Birch", x=random.uniform(5, 95), y=random.uniform(5, 95))

# 5. Terrain
terrain = landscape.get_terrain()
terrain.set_extent_width(100)
terrain.set_extent_height(100)
terrain.set_optical("dark_soil_mollisol")  # built-in soil

# 6. Sensor + Observation
sensor = SensorOrthographic()
sensor.set_spectral_bands("680:2,550:2,450:2")  # R, G, B bands (center:fwhm)
sensor.set_image_width(512)
sensor.set_image_height(512)
sensor.set_sample_per_pixel(128)
scene.set_sensor(sensor)
scene.set_observation(ObservationOrthographic())

# 7. Illumination
ill = scene.get_illumination()
ill.set_sun_zenith(30)
ill.set_sun_azimuth(180)

# 8. Run
sim.save_sim_project()
sim.start()

# 9. Post-process
PostProcessing.radiance2brf(sim.get_sim_dir())
```

## ForestSceneBuilder — Quick Forest Scene from Statistical Parameters

For users who want to generate forest scenes from high-level parameters (like PROSAIL) instead of manually specifying individual tree parameters:

```python
from ForestSceneBuilder import ForestSceneBuilder, ForestType
from SimpleCrownGenerator import LAD

builder = ForestSceneBuilder(less_dir, output_dir, "my_sim", scene_x_size=40, scene_y_size=40)
builder.set_canopy_params(lai=3.0, fcc=0.6)           # FCC = fractional crown cover
builder.set_forest_type(ForestType.BROADLEAF_NATURAL)  # preset: crown shape, allometry, spacing
builder.build()    # generates a complete LESS simulation project
builder.run()      # runs the simulation
```

**7 forest types**: `CONIFEROUS_NATURAL`, `CONIFEROUS_PLANTATION`, `BROADLEAF_NATURAL`, `BROADLEAF_PLANTATION`, `MIXED_NATURAL`, `SAVANNA`, `SHRUBLAND`

**Key features**:
- Automatic derivation of tree dimensions from allometric relationships (crown diameter -> height, trunk, DBH)
- Template tree approach: generates K template OBJs with different sizes, instances each multiple times
- Natural forests: crown size variance via Normal distribution + Poisson disc spacing
- Plantations: uniform trees + regular grid spacing with jitter
- Mixed forests: `builder.species_mix = {"broadleaf": 0.6, "coniferous": 0.4}`
- Understory grass layer: `builder.has_understory = True`
- PROSPECT-D leaf optics: `builder.set_optical_from_prospect(N=1.5, Cab=40, Car=8, Cw=0.01, Cm=0.009)`
- Triangle mesh or turbid: `builder.leaf_as_turbid = True/False`
- Access underlying Simulation: `sim = builder.get_simulation()` for further customization

For full ForestSceneBuilder API and examples, see `api-reference.md` and `examples.md`.

## Key Concepts

### Spectral Bands Format
Bands are comma-separated `wavelength:fwhm` pairs in nanometers:
- `"680:2,550:2,450:2"` — three bands centered at 680, 550, 450 nm, each 2 nm wide
- `"680,550,450"` — same centers, default width

### Optical Property Value Format
Semicolon-separated groups for front reflectance, back reflectance, and transmittance. Each group has comma-separated values per band:
```
"front_r1,front_r2;back_r1,back_r2;trans_r1,trans_r2"
```

### Coordinate System
- Scene is a rectangle: `(0,0)` to `(width, height)` in meters
- Z is up (vertical)
- `place_object(name, x, y, z=0, rotate=0)` — positions in scene coordinates

### Built-in Optical Properties (always available)
- `"birch_leaf_green"` — green leaf
- `"birch_branch"` — bark/branch
- `"dark_soil_mollisol"` — dark soil

### Leaf Angle Distribution (LAD) Enum
Used when setting turbid medium components or ForestSceneBuilder:
- `LAD.UNIFORM` — Uniform distribution
- `LAD.SPHERICAL` — Spherical distribution
- `LAD.ERECTOPHILE` — Erectophile (vertical leaves)
- `LAD.EXTREMOPHILE` — Extremophile
- `LAD.PLANOPHILE` — Planophile (horizontal leaves)
- `LAD.PLAGIOPHILE` — Plagiophile

### Crown Shape Enum
- `CrownShape.CUBE`, `CrownShape.ELLIPSOID`, `CrownShape.CYLINDER`, `CrownShape.CONE`, `CrownShape.ASYMMETRIC_GAUSSIAN`

### Leaf Shape Enum
- `LeafShape.SQUARE`, `LeafShape.DISK`

## Optical Property Models

### PROSPECT-D (Leaf Optics)
```python
from Prospect5AndD import prospectD
reflectances, transmittances = prospectD(wl=[550, 680, 850], N=1.5, Cab=40, Car=8, Cw=0.01, Cm=0.009, Anth=0, BP=0)
```

### GSV Soil Model
```python
from GSVSoil import GSVSoil
gsv = GSVSoil()
soil_ref = gsv.get_soil_spectra_gsv3(wavelength=[550, 680, 850], c1=0.5, c2=0.1, c3=0.05, csm=-0.2)
# csm: moisture coefficient, recommended [-0.6, 0], 0 = dry
```

### Fluspect (Leaf Fluorescence)
Used internally when `OpticalItemType.FLUSPECT` is set. The `fluspect()` function computes leaf reflectance/transmittance with fluorescence matrices.

### FvCB Photosynthesis Model
```python
from FvCB_from_SCOPE import PhotosynthesisModel
model = PhotosynthesisModel(plant_type="C3", P=101325, O2=209000, Q=1000,
                             Cs_ppm=400, es=1.0, leaf_tmp_k=298.15,
                             Vcmx25=60, RdPerVcmax25=0.015,
                             BallBerrySlope=8, BallBerry0=0.01)
Ci_ppm, gs, A, Ag, Vc, Vs, Ve, CO2_per_electron = model.run()
```

## SDKCodeGenerator — Reverse-Engineer GUI Projects

Generate Python SDK code from an existing LESS GUI simulation project:

```python
from SDKCodeGenerator import SDKCodeGenerator
gen = SDKCodeGenerator(r"D:\Simulations\my_gui_project")
gen.generate(r"D:\output\generated_script.py")
```

This is useful for converting GUI-created simulations into reproducible Python scripts.

For the full API reference with all classes, methods, parameters, and advanced examples, read the supporting files in this skill directory:
- `api-reference.md` — complete API for every class
- `examples.md` — working code for every simulation type (LiDAR, BRF, fisheye, batch, forest scenes, etc.)
- `helpers.py` — validation utilities (band consistency check, orthographic spp check, turbid boundary check, LAI computation). You can inline these functions into generated code when validation is needed.
- `faq.md` — common domain questions (leaf optics, BRF vs reflectance, turbid vs mesh, atmosphere, thermal, etc.). Consult when users ask physics or methodology questions.

## PROHIBITED — Do NOT Use

These are hard restrictions. Violating them will produce incorrect simulation results.

1. **NEVER use `cover_whole_scene = True`** on SensorTRAC or SensorOrthographic — this option is forbidden for these sensor types
2. **NEVER use `set_repetitive_scene()`** when terrain is non-planar (RASTER or MESH) — repetitive scene must be 0 (disabled) for DEM/mesh terrain
3. **NEVER use `enable_virtual_plane()`** on SensorOrthographic or SensorPhotonTracing — virtual plane is forbidden for these sensor types (PhotonTracing has a known bug)
4. **NEVER use `compute_scene_lai()` when scene contains turbid medium objects** — `landscape.compute_scene_lai()` only works for triangle mesh scenes. For turbid medium scenes, manually compute LAI as: `LAI = crown_volume * leaf_area_density * num_trees / scene_area`

## Important Defaults & Rules

1. **Orthographic sensor view region must match scene extent** — when the user does not explicitly specify `sub_region_width` / `sub_region_height` for SensorOrthographic, always set them equal to the terrain extent (`terrain.get_extent_width()` / `terrain.get_extent_height()`). Do NOT leave them at arbitrary defaults or guess values.
2. **Orthographic simulation must post-process radiance to BRF** — after `sim.start()` with SensorOrthographic, always call `PostProcessing.radiance2brf(sim.get_sim_dir())`. Use BRF results for all subsequent analysis unless the user explicitly asks for radiance.
3. **Spectral band FWHM defaults to 1** — when setting `set_spectral_bands()`, use `"680:1,550:1,450:1"` format. Only use a different FWHM if the user explicitly specifies it.
   - **RGB film type (`set_film_type("rgb")`)**: When using RGB film type to produce PNG images, set **30 uniform bands from 360 to 830 nm** (approximately 16.2 nm spacing). Generate the bands string as: `bands = ",".join(f"{int(wl)}:1" for wl in np.linspace(360, 830, 30))`. All optical properties (leaf, soil, trunk, understory, etc.) and `ill.set_ats_percentage()` must also have exactly 30 values to match. When using `ForestSceneBuilder`, set `builder.spectral_bands = [int(wl) for wl in np.linspace(360, 830, 30)]` BEFORE calling `build()`.
   - **Broadband reflectance**: To simulate broadband sensor reflectance (e.g., Landsat, Sentinel-2 bands), do NOT set a large FWHM directly. Instead, simulate narrowband hyperspectral data (1 nm resolution across the band range), then post-process by applying the spectral response function (SRF) or numerical integration to compute broadband values. This applies to reflectance, BRF, and up/down radiation products. Only skip this if the user explicitly requests direct broadband simulation.
4. **All band counts must be consistent** — sensor spectral bands, `ill.set_ats_percentage()` (sky-to-total ratio), and `OpticalItem` values (each semicolon-separated group) must all have the same number of bands. When band count changes, update all of them. Fill unknown values with `0` for sky-to-total ratio.
5. **Sensor type must match observation type** — `SensorOrthographic` with `ObservationOrthographic`, `SensorPerspective` with `ObservationPerspective`, `SensorFisheye` with `ObservationFisheye`, `SensorPhotonTracing` with `ObservationPhotonTracing`. Mismatched pairs will cause errors.
6. **Sun zenith angle range is 0~89.99** — never set to 90 or above, it will cause simulation errors.
7. **Turbid medium objects must be entirely within scene boundary** — when placing turbid medium objects, ensure the entire OBJ bounding box (position + crown extent) stays within `(0, 0)` to `(extent_width, extent_height)`. Objects protruding outside the boundary will produce incorrect results.
8. **Sample per pixel guidance** — preview/testing: 16~32; production: 64~256. For SensorOrthographic, also check spatial sampling density: `spp_needed = 64 * (sub_region_width * sub_region_height) / (image_width * image_height)`. Ensure at least 64 samples per square meter. Adjust `sample_per_pixel` or `image_width`/`image_height` accordingly.
9. **PhotonTracing illumination resolution for fluorescence/fPAR** — when using `SensorPhotonTracing` with fluorescence (`enable_Fluor_product(True)`) or fPAR (`enable_fpar_product(True)`), set `sensor.set_sun_ray_resolution(0.003)` instead of the default 0.01. If the user reports slow runtime, suggest increasing this value (e.g., 0.005 or 0.01) as a speed/accuracy tradeoff.
10. **Multi-angle orthographic images must enable orthophoto map** — when simulating multiple viewing angles with SensorOrthographic for per-pixel BRDF extraction, always set `obs.is_orthophoto_map = True` on ObservationOrthographic. This reprojects each oblique view onto the ground plane so that all angles produce co-registered images (same pixel = same ground location and size). Without this, different angles cover different ground extents and pixel sizes, making per-pixel comparison impossible. Also use `set_repetitive_scene(100)` (flat terrain only) to avoid edge effects at oblique angles.
11. **Batch simulations should use runtime modification by default** — when looping over spectral properties, sun angles, view angles, or optical properties, always enable `sim.enable_runtime_modification_of_properties(True)` to avoid reloading the full scene each iteration. This significantly speeds up batch runs. Inform the user that you are using this mode. If structural changes (geometry/instances) are needed between runs, call `sim.reload_runtime_structural_properties()`.
11. **CPU cores default to total cores minus 2** — when setting `params.set_number_of_cores()`, use `os.cpu_count() - 2` (minimum 1) to leave headroom for the OS. Always `import os` and compute dynamically rather than hardcoding.
12. **Always call `sim.read_sim_project()` before modifying the scene** — it loads defaults from input.conf.
13. **Always call `sim.save_sim_project()` before `sim.start()`** — writes the JSON config.
14. **`clear_landscape_elements()` removes ALL objects/instances** — call before re-adding.
15. **`clear_user_defined_optical_properties()`** keeps built-in properties — use instead of `clear_all_optical_properties()`.
16. **Turbid media components** require extra params: `is_turbid=True, leaf_density=X, lad="Spherical"`.
17. **LiDAR sensor** needs a scanning device set via `sensor.set_scanning_device(ALSLiDAR())` or `TLSLiDAR()`.
18. **SensorTRAC** is for TRAC-like gap fraction measurements along a transect line.
19. **Call `landscape.prepare_for_ui()` before opening in GUI** — if a scene is created via SDK and the user wants to visualize it in the LESS GUI, call `landscape.prepare_for_ui()` after `sim.save_sim_project()`. This computes bounding boxes and other metadata needed by the GUI to display the scene correctly.
20. **Disable OBJ cache when geometry changes between runs** — if an OBJ file is replaced with different geometry but keeps the same filename, LESS will use the cached version and produce identical results. Call `landscape.set_obj_cache(False)` to force reloading. Re-enable after the geometry stabilizes for better performance.
21. **ForestSceneBuilder spectral bands must match sensor** — when customizing the sensor's spectral bands after `builder.build()`, the builder's default bands (550, 680, 800, 850 nm) may differ from the desired sensor bands. Always set `builder.spectral_bands = [680, 550, 450]` (or the desired wavelengths) BEFORE calling `builder.build()` and `builder.set_optical_from_prospect(...)`, so that all generated optical properties (leaf, soil, trunk, understory) have the correct number of bands matching the sensor. Mismatched band counts will cause a runtime error: `"Invalid spectrum value specified (length does not match the current spectral discretization)"`.
22. **Ask user about crown representation mode (facet vs turbid)** — when using `ForestSceneBuilder` or `SimpleCrownGenerator` to create tree crowns, always ask the user whether they prefer **facet mode** (triangle mesh leaves, `builder.leaf_as_turbid = False`) or **turbid mode** (homogeneous turbid medium, `builder.leaf_as_turbid = True`) before generating the scene. Facet mode is more realistic but slower; turbid mode is faster and suitable for large-scale scenes. Do NOT assume a default without asking.
