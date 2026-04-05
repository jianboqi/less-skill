# pyLessSDK API Reference

## ForestSceneBuilder

Generate 3D forest scenes from statistical parameters (LAI, FCC, forest type). Located in `Utility/Python_script/pyLessSDK/ForestSceneBuilder.py`.

```python
ForestSceneBuilder(less_root_dir, dist_dir, sim_name, scene_x_size=30, scene_y_size=30)
```

### Forest Types

```python
class ForestType(Enum):
    CONIFEROUS_NATURAL       # Cone crown, Poisson disc, CV=0.25
    CONIFEROUS_PLANTATION    # Cone crown, regular grid, CV=0.08
    BROADLEAF_NATURAL        # Ellipsoid crown, Poisson disc, CV=0.30
    BROADLEAF_PLANTATION     # Ellipsoid crown, regular grid, CV=0.05
    MIXED_NATURAL            # Mixed shapes, Poisson disc, CV=0.35
    SAVANNA                  # Wide flat crowns, sparse, CV=0.40
    SHRUBLAND                # Low shrubs, no trunk, CV=0.30
```

### Properties (set before calling `build()`)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `lai` | float | 3.0 | Leaf area index |
| `fcc` | float | 0.5 | Fractional crown cover |
| `lad` | LAD/None | None | Leaf angle distribution (None = use preset) |
| `forest_type` | ForestType | BROADLEAF_NATURAL | Forest type preset |
| `leaf_as_turbid` | bool | True | True=turbid medium, False=triangle mesh |
| `crown_diameter_mean` | float/None | None | Override auto-derived crown diameter (m) |
| `crown_height` | float/None | None | Override crown height (m) |
| `tree_height` | float/None | None | Override total tree height (m) |
| `trunk_height` | float/None | None | Override trunk height (m) |
| `crown_shape` | CrownShape/None | None | Override preset crown shape |
| `dbh` | float/None | None | Override DBH (m) |
| `num_templates` | int/None | None | Number of template trees (None=auto: 7 natural, 1 plantation) |
| `has_understory` | bool/None | None | Enable understory grass (None = use preset) |
| `understory_lai` | float | 0.5 | Understory LAI |
| `understory_height` | float | 0.3 | Understory height (m) |
| `understory_lad` | LAD | ERECTOPHILE | Understory leaf angle distribution |
| `species_mix` | dict/None | None | Mixed forest ratio, e.g. `{"broadleaf": 0.6, "coniferous": 0.4}` |
| `spectral_bands` | list | [450,550,650,850] | Wavelengths in nm |
| `op_leaf` | OpticalRefTrans/None | None | Leaf optics (None=auto from PROSPECT-D) |
| `op_leaf_db_name` | str/None | None | Use database spectral name instead |
| `op_soil` | OpticalRefTrans/None | None | Soil optics (None=auto) |
| `op_trunk` | OpticalRefTrans/None | None | Trunk optics (None=auto) |
| `op_understory` | OpticalRefTrans/None | None | Understory optics (None=auto) |
| `solar_zenith` | float | 30 | Sun zenith angle (degrees) |
| `solar_azimuth` | float | 180 | Sun azimuth angle (degrees) |
| `view_zen_azi_angles` | list | [(0,0)] | View angles for photon tracing |
| `hotspot` | float | 0.1 | Hotspot factor |
| `random_seed` | int | 42 | Random seed for reproducibility |

### Methods

| Method | Description |
|--------|-------------|
| `set_canopy_params(lai, fcc, lad)` | Set canopy statistical parameters |
| `set_forest_type(forest_type)` | Set forest type and load preset |
| `set_optical_from_prospect(N, Cab, Car, Cw, Cm, Anth=0, BP=0)` | Derive leaf optics from PROSPECT-D |
| `build()` | Auto-derive all parameters and generate complete LESS project |
| `run()` | Run the LESS simulation |
| `get_simulation()` | Return underlying `Simulation` object for further customization |

### Parameter Auto-Derivation

When `build()` is called, it automatically derives tree-level parameters:
1. **Crown diameter** from FCC and scene size (if not specified)
2. **Crown height** = diameter x `crown_aspect_ratio` (from preset)
3. **Tree height** = diameter x `height_diameter_ratio` (from preset)
4. **Trunk height** = tree_height - crown_height
5. **DBH** = diameter x `dbh_diameter_ratio` (from preset)
6. **Number of trees** = FCC x scene_area / crown_projected_area
7. **Leaf volume density** = LAI x scene_area / (N_trees x crown_volume)
8. **Optical properties** auto-generated from PROSPECT-D if not specified

### Template Tree Strategy

For natural forests (crown_diameter_cv > 0.1):
- Generates `num_templates` (default 7) template trees with different crown diameters
- Each template is a separate SceneObject, placed via instances at multiple positions
- Crown diameters sampled from Normal(mean, mean x CV) distribution
- More efficient than per-tree unique OBJ while maintaining visual/physical diversity

---

## SimulationHelper

```python
SimulationHelper(less_install_root_path="")
```

| Method | Description |
|--------|-------------|
| `create_new_sim(sim_path)` | Create new simulation directory with default structure |
| `get_less_py_dir()` | Get lesspy script directory |
| `get_py_interpreter_path()` | Get bundled Python interpreter path |
| `get_script_less_py_path()` | Get main less.py script path |
| `get_default_config_file()` | Get default.conf path |

---

## Simulation

```python
Simulation(sim_dir, simulation_helper)
```

| Method | Description |
|--------|-------------|
| `read_sim_project()` | Load existing project from input.conf |
| `save_sim_project()` | Save config to input.conf |
| `save_as_sim_project(path)` | Save as new project at given path |
| `start()` | Execute the simulation |
| `get_scene()` / `set_scene(scene)` | Get/set Scene object |
| `get_sim_dir()` | Returns simulation directory path |
| `get_parameters_dir()` | Returns Parameters/ directory |
| `get_dist_file()` / `set_dist_file(path)` | Output file path |
| `is_sim_valid()` | Check if directory has `.less/` marker |
| `enable_runtime_modification_of_properties(bool)` | Batch mode: modify properties between runs |
| `reload_runtime_structural_properties()` | Reset scene for structural changes in batch mode |
| `get_runtime_scene()` | Get RuntimeScene (for ray intersection queries) |
| `get_scene_helper()` | Returns the SimulationHelper object |
| `load_input_conf()` | Loads input.conf JSON and returns config dict |
| `log_level` | Attribute: `LogLevel.trace/debug/info/warn/error` |

---

## Scene

```python
scene = sim.get_scene()
```

| Method | Description |
|--------|-------------|
| `get_landscape()` / `set_landscape(l)` | Landscape object |
| `get_sensor()` / `set_sensor(s)` | Sensor (triggers atmosphere/band sync) |
| `get_illumination()` / `set_illumination(i)` | Illumination object |
| `get_observation()` / `set_observation(o)` | Observation geometry |
| `get_advanced_params()` / `set_advanced_params(p)` | Advanced parameters |
| `with_lidar_sensor()` | Check if current sensor is LiDAR |
| `write_scene(json_file_path)` | Write scene configuration to a JSON file |

---

## Landscape

```python
landscape = scene.get_landscape()
```

### Object / Instance Management

| Method | Description |
|--------|-------------|
| `add_object(scene_object, override_file=True, translate_to_origin="no")` | Add a SceneObject. `translate_to_origin`: `"no"`, `"xy"`, or `"xyz"` |
| `place_object(name, x=50, y=50, z=0, rotate=0, rotate_axis_x=None, rotate_axis_y=None, rotate_axis_z=None, scale_extent_x=None, scale_extent_y=None, scale_extent_z=None)` | Place object instance at position |
| `get_objects()` | Dict of all SceneObjects |
| `get_object(name)` | Get single SceneObject by name |
| `get_instances()` | Dict of instance positions |
| `get_object_bounds()` | Bounding boxes per object |
| `clear_landscape_elements()` | Remove all objects AND instances |
| `clear_objects()` | Remove objects only |
| `clear_instances()` | Remove instances only |

### Optical Properties

| Method | Description |
|--------|-------------|
| `add_op_item(OpticalItem)` | Add optical property |
| `get_op_item(name)` | Get OpticalItem by name |
| `get_all_op_items()` | List all optical items |
| `clear_user_defined_optical_properties()` | Remove custom ops, keep built-ins |
| `clear_all_optical_properties()` | Remove ALL optical properties |

### Analysis Methods

| Method | Description |
|--------|-------------|
| `compute_scene_lai(exclude_object_outside=False, ignore_list=None)` | Total scene LAI |
| `compute_lai3d(out_path, rows, cols, layers, compute_width=-1, compute_height=-1, ignore_list=None)` | 3D LAI voxel grid |
| `compute_chm(out_path, resolution=2, ignore_list=None)` | Canopy Height Model raster |
| `compute_crown_radius(out_file, out_mask_img_file=None, mask_img_resolution=0.5)` | Crown radius per instance |
| `compute_crown_boundary(out_file, out_mask_img_file=None, mask_img_resolution=0.5)` | Crown boundary polygons |

### Other

| Method | Description |
|--------|-------------|
| `convert_obj_to_binary(bool)` | Enable binary OBJ conversion for faster load |
| `set_obj_cache(bool)` | Cache OBJ meshes in memory |
| `get_terrain()` | Returns Terrain object |
| `set_terrain_op(op_name)` | Shortcut to set terrain optical property |

---

## SceneObject

```python
obj = SceneObject(name, components=None)
```

| Method | Description |
|--------|-------------|
| `get_scene_obj_name()` / `set_scene_obj_name(name)` | Object name |
| `add_component_from_file(obj_path, op_name, temperature="-", color="0x006400ff", is_turbid=False, leaf_density=-999.0, lad="-", hotspot_factor=-999.0)` | Add OBJ mesh component |
| `set_component_op(comp_name, op_name)` | Change optical property of existing component |

**Component parameters for turbid media:**
- `is_turbid=True` — treat as participating medium (volumetric scattering)
- `leaf_density` — leaf area density (m2/m3)
- `lad` — leaf angle distribution: `"Spherical"`, `"Uniform"`, `"Planophile"`, `"Erectophile"`, `"Plagiophile"`, `"Extremophile"`
- `hotspot_factor` — hotspot correction factor

---

## OpticalItem

```python
OpticalItem(op_name="", op_value="", op_type=1, op_model_params=None)
```

**Value format:** `"front_r1,front_r2;back_r1,back_r2;trans_r1,trans_r2"` — semicolon separates front reflectance, back reflectance, and transmittance. Commas separate per-band values.

| Method | Description |
|--------|-------------|
| `get_op_name()` / `set_op_name(name)` | Property name |
| `get_op_value()` / `set_op_value(value)` | Raw value string |
| `get_op_type()` / `set_op_type(type)` | OpticalItemType enum value |
| `get_op_model_params()` / `set_op_model_params(dict)` | Model-specific parameters |
| `get_op_front_reflectance()` | Parsed front reflectance as float list |
| `get_op_back_reflectance()` | Parsed back reflectance as float list |
| `get_op_transmittance()` | Parsed transmittance as float list |

**OpticalItemType values:**

| Type | Value | Description |
|------|-------|-------------|
| `DB_LAMBERTIAN` | 0 | Database Lambertian (built-in) |
| `MANUAL` | 1 | Manually specified (default) |
| `PROSPECT` | 2 | PROSPECT leaf model |
| `GSV` | 3 | GSV soil model |
| `FLUSPECT` | 4 | Fluspect leaf fluorescence model |
| `RPV` | 5 | Rahman-Pinty-Verstraete BRDF |
| `ART` | 6 | ART model |
| `SOILSPECT` | 7 | SoilSpect model |
| `ARTF` | 8 | ART with fluorescence |
| `HAPKE_MARMIR2` | 9 | Hapke Marmit2 model |

---

## Terrain

```python
terrain = landscape.get_terrain()
```

| Method | Description |
|--------|-------------|
| `set_extent_width(w)` / `get_extent_width()` | Scene width in meters (default 100) |
| `set_extent_height(h)` / `get_extent_height()` | Scene height in meters (default 100) |
| `set_terrain_type(type)` | `TERRAIN_TYPE.PLANE`, `.RASTER`, `.MESH` |
| `set_terrain_file(path)` | DEM raster or OBJ mesh file (copies to Parameters/) |
| `set_terr_brdf_type(type)` | `TERRAIN_BRDF_TYPE.SPATIALLY_UNIFORM`, `.LAND_ALBEDO_MAP`, `.LAND_COVER_MAP` |
| `set_optical(name)` | Set terrain optical property (SPATIALLY_UNIFORM only) |
| `get_optical()` | Get terrain optical property name |
| `set_landalbedo_file(path)` | Set albedo map file (LAND_ALBEDO_MAP only) |

**Attributes:** `temperature` (default `"T300"`), `CacheDEMFile` (default True), `CacheLandAlbedoMapFile` (default True), `optical_scale` (default 1)

---

## Sensors

### SensorOrthographic (Nadir Image)

```python
sensor = SensorOrthographic()
```

| Method | Description |
|--------|-------------|
| `set_spectral_bands(bands)` | e.g., `"680:2,550:2,450:2"` |
| `get_spectral_bands()` | Get band string |
| `get_number_of_bands()` | Band count |
| `set_image_width(w)` / `set_image_height(h)` | Image dimensions (pixels) |
| `set_sample_per_pixel(n)` | Samples per pixel (default 128) |
| `set_sub_region_width(w)` / `set_sub_region_height(h)` | Sub-region rendering |
| `set_film_type(type)` | `"rgb"` or `"spectrum"` |
| `set_repetitive_scene(n)` | Repeat scene tiling |
| `enable_virtual_plane(enabled, center, size)` | Virtual measurement plane |
| `has_four_components_product` | Boolean: output sunlit/shaded soil/vegetation fractions |
| `has_Fluor_Product` | Boolean: enable fluorescence output |
| `thermal_radiation` | Boolean: enable thermal mode |

### SensorPerspective (Perspective Camera)

```python
sensor = SensorPerspective()
```

Inherits all SensorOrthographic methods plus:

| Method | Description |
|--------|-------------|
| `set_fov_x(deg)` / `get_fov_x()` | Field of view X |
| `set_fov_y(deg)` / `get_fov_y()` | Field of view Y |

### SensorFisheye (Hemispherical)

```python
sensor = SensorFisheye()
```

Additional methods:

| Method | Description |
|--------|-------------|
| `set_angular_fov(deg)` | Angular FOV (default 165) |
| `set_projection_type(type)` | `"equisolid"` (default) |

### SensorPhotonTracing (Forward Tracing — BRF, fPAR, Fluorescence)

```python
sensor = SensorPhotonTracing()
```

| Method | Description |
|--------|-------------|
| `set_sun_ray_resolution(res)` | Sun ray spacing (default 0.02 m) |
| `enable_brf_product(bool)` | Enable BRF output |
| `enable_fpar_product(bool)` | Enable fPAR output |
| `set_fpar_layer(layer_def)` | fPAR layer definition, e.g., `"0:2:20"` (start:step:end) |
| `enable_updown_radiation_product(bool)` | Enable up/down radiation |
| `enable_Fluor_product(bool)` | Enable fluorescence |
| `set_virtual_directions(dirs)` | Virtual observation directions: `"zen1:azi1;zen2:azi2"` |
| `set_virtual_director_directions(dirs)` | Virtual detector directions |
| `set_number_of_directions(n)` | Photon directions (default 150) |
| `set_Photosynthesis(model)` | `"No"` or model name |
| `has_four_components_product` | 4-component output |

### SensorLiDAR

```python
sensor = SensorLiDAR()
sensor.set_scanning_device(ALSLiDAR())  # or TLSLiDAR()
```

### SensorTRAC (Transect Gap Fraction)

Simulates TRAC-like measurements along a transect line for gap fraction analysis.

```python
sensor = SensorTRAC()
```

| Method | Description |
|--------|-------------|
| `set_startPos(pos)` | Start position as `"X,Y,Z"` string (default `"5,5,1"`) |
| `get_startPos()` | Get start position |
| `set_endPos(pos)` | End position as `"X,Y,Z"` string (default `"90,90,1"`) |
| `get_endPos()` | Get end position |
| `set_step(step)` | Step size along transect (default 0.05 m) |
| `get_step()` | Get step size |
| `set_number_rays(num)` | Number of rays per measurement point (default 30) |
| `get_number_rays()` | Get number of rays |

**Attributes:**
- `cover_whole_scene` (bool, default False) — measure across entire scene
- `sample_per_pixel` (int, default 128) — samples per pixel
- `sub_region_width` / `sub_region_height` (int, default 100)

Inherits from SensorBasic: `set_spectral_bands()`, `set_image_width()`, `set_image_height()`, etc.

---

## LiDAR Devices

### ALSLiDAR (Airborne)

```python
als = ALSLiDAR()
als.platform.altitude = 800        # flight altitude (m)
als.platform.startX = 5            # flight line start X
als.platform.startY = 50           # flight line start Y
als.platform.endX = 95             # flight line end X
als.platform.endY = 50             # flight line end Y
als.platform.swathWidth = 90       # swath width (m)
als.platform.rangeResolution = 0.5 # range resolution (m)
als.platform.yawResolution = 0.5   # yaw resolution (deg)
als.platform.minRange = 770        # min range
als.platform.maxRange = 805        # max range
als.beam.axialDivision = 30        # beam subdivisions
als.beam.maxOrder = 2              # max bounce order
als.device.footprintHalfAngle = 0.0012
als.device.pulseEnergy = 1
als.set_lidar_sim_mode(LiDARSimMode.MultiRayPointCloud)
```

### TLSLiDAR (Terrestrial)

```python
tls = TLSLiDAR()
tls.platform.x = 20               # scanner X position
tls.platform.y = 20               # scanner Y position
tls.platform.z = 10               # scanner height
tls.platform.centerAzimuth = 45
tls.platform.resolutionAzimuth = 1
tls.platform.deltaAzimuth = 10
tls.platform.centerZenith = 90
tls.platform.resolutionZenith = 1
tls.platform.deltaZenith = 10
tls.platform.minRange = 10
tls.platform.maxRange = 100
```

### MonoPulseLiDAR

```python
mono = MonoPulseLiDAR()
# Uses MonoPulsePlatform instead of ALSPlatform
# Otherwise same interface as ALSLiDAR (beam, device, sim_mode)
```

### LiDARSimMode

| Mode | Description |
|------|-------------|
| `SingleRayPointCloud` | Single ray per pulse |
| `MultiRayPointCloud` | Multiple rays per pulse |
| `MultiRayPointCloudIncident` | With incident angle information |
| `MultiRayWaveform` | Full waveform simulation |

---

## Observation Types

### ObservationOrthographic

```python
obs = ObservationOrthographic()
obs.set_obs_zenith(0)     # 0 = nadir
obs.set_obs_azimuth(180)  # view azimuth
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_orthophoto_map` | bool | False | Reproject oblique view onto ground plane for co-registered multi-angle images |
| `orthophoto_relative_height` | float | 0 | Reference height for orthophoto reprojection |

### ObservationPerspective

```python
obs = ObservationPerspective()
obs.set_origin((50, 50, 80))   # camera position (x, y, z)
obs.set_target((50, 50, 0))    # look-at point
obs.enable_relative_height(True)  # z relative to terrain
```

### ObservationFisheye

Same interface as ObservationPerspective.

### ObservationPhotonTracing

Same interface as ObservationOrthographic. Used with SensorPhotonTracing.

---

## Illumination

```python
ill = scene.get_illumination()
```

### Basic Solar Geometry

| Method | Description |
|--------|-------------|
| `set_sun_zenith(deg)` | Solar zenith (0-89.99) |
| `set_sun_azimuth(deg)` | Solar azimuth |

### Atmosphere Mode

| Method | Description |
|--------|-------------|
| `set_ats_type(type)` | `"SKY_TO_TOTAL"` (default) or `"ATMOSPHERE"` |
| `set_ats_percentage(pct)` | Sky-to-total ratio per band, e.g., `"0.1,0.2,0.15"` |
| `set_sun_spectrum(spec)` | Manual sun spectrum values |
| `set_sky_spectrum(spec)` | Manual sky spectrum values |

### Atmosphere 6S Model

```python
ill.set_ats_type("ATMOSPHERE")
ill.set_ats_model("6S")
atm = Atmosphere6S()
atm.ats_profile = "MidlatitudeSummer"  # or "Tropical", "SubarcticSummer", etc.
atm.aot_550 = 0.375                    # aerosol optical thickness at 550nm
atm.aero_profile = "Continental"        # or "Maritime", "Urban", etc.
atm.target_altitude = 0                 # target altitude in meters
atm.month = 7
atm.day = 14
ill.set_ats_model_params(atm)
```

### Sun Position Calculator

```python
from Illumination import SunPositionCalculator
calc = SunPositionCalculator()
calc.timezone = 8
calc.year, calc.month, calc.day = 2024, 6, 19
calc.hour, calc.minute, calc.second = 19, 23, 37
calc.latitude = 39.96
calc.longitude = 116.37
calc.altitude = 50
ill.set_sun_position_calculator(True)
ill.set_sun_position_calculator_params(calc)
```

### Environmental Parameters

| Method | Description |
|--------|-------------|
| `set_ats_temperature(name)` | Temperature profile, default `"T300"` |
| `set_ats_CO2(ppm)` | CO2 concentration (default 400) |
| `set_ats_O2(ppm)` | O2 concentration (default 209000) |
| `set_ats_pressure(hPa)` | Air pressure (default 970) |
| `set_ats_Tyear(K)` | Annual mean temperature (default 288.15) |

---

## AdvancedParams

```python
params = scene.get_advanced_params()
params.set_number_of_cores(8)     # CPU cores to use
params.minimum_iteration = 100    # minimum iterations
params.network_sim = False        # network simulation
```

---

## PostProcessing

```python
from PostProcessing import PostProcessing
```

| Method | Description |
|--------|-------------|
| `PostProcessing.radiance2brf(sim_dir, input_file="", output_file="")` | Convert radiance to BRF |
| `PostProcessing.bt_single_img_processing(radiance_path, wavelengths)` | Brightness temperature |
| `PostProcessing.fourcomponents2fvc(input_file, output_file)` | 4-component -> vegetation fraction |
| `PostProcessing.multiray_pointcloud_txt2las(pt_dir, sceneY)` | Point cloud TXT -> LAS |
| `PostProcessing.readIrr(irr_file_path)` | Read irradiance file |

---

## Optical Property Models

### PROSPECT-D (Leaf Reflectance/Transmittance)

```python
from Prospect5AndD import prospectD
reflectances, transmittances = prospectD(wl, N, Car, BP, Cm, Cab, Anth, Cw)
```

| Parameter | Description |
|-----------|-------------|
| `wl` | Wavelength(s) — float, int, or list (nm) |
| `N` | Leaf structure parameter (mesophyll layers) |
| `Cab` | Chlorophyll a+b content (ug/cm2) |
| `Car` | Carotenoid content (ug/cm2) |
| `Anth` | Anthocyanin content (ug/cm2) |
| `Cw` | Water content (cm) |
| `Cm` | Dry matter content (g/cm2) |
| `BP` | Brown pigment content |

Returns: `(reflectances_list, transmittances_list)`

### GSV Soil Model

```python
from GSVSoil import GSVSoil
gsv = GSVSoil()
# 3-parameter model (more accurate)
soil_ref = gsv.get_soil_spectra_gsv3(wavelength, c1, c2, c3, csm)
# 1-parameter model (simpler)
soil_ref = gsv.get_soil_spectra_gsv1(wavelength, c1, csm)
```

| Parameter | Description |
|-----------|-------------|
| `wavelength` | Array/list of wavelengths (400-2500 nm) |
| `c1` | Brightness coefficient for dry soil spectrum |
| `c2` | Shape coefficient (GSV3 only) |
| `c3` | Shape coefficient (GSV3 only) |
| `csm` | Moisture coefficient (recommended [-0.6, 0]; 0 = dry) |

### Fluspect (Leaf Fluorescence)

```python
from Fluspect import fluspect
ref_str, trans_str = fluspect(wl, isFluspectPro, isFluor, opName,
                               Cab=30, Cca=10, V2Z=0, Can=0,
                               Cw=0.015, Cdm=0.009, Cs=0, N=1.5,
                               eta=0.025, Cbc=0.009, Cp=0.001,
                               eta_1=0.002, eta_2=0.01)
```

| Parameter | Description |
|-----------|-------------|
| `wl` | Comma-separated wavelength string (e.g., "502,621,640") |
| `isFluspectPro` | bool — use PROSPECT-PRO model (True) or P6D (False) |
| `isFluor` | bool — compute fluorescence matrices |
| `opName` | Output file name prefix |
| `Cab` | Chlorophyll (ug/cm2), default 30 |
| `Cca` | Carotenoid (ug/cm2), default 10 |
| `V2Z` | Violaxanthin-Zeaxanthin deepoxidation [0-1], default 0; -999 to disable |
| `Can` | Anthocyanin (ug/cm2), default 0 |
| `Cw` | Water column (cm), default 0.015 |
| `Cdm` | Dry matter (g/cm2), default 0.009; if 0, uses Cbc+Cp |
| `Cs` | Senescent matter fraction [0-1], default 0 |
| `N` | Mesophyll structure [1.0-3.5], default 1.5 |
| `eta` | Combined PSI+PSII fluorescence quantum yield (PRO only), default 0.025 |
| `Cbc` | Carbon-based dry matter (g/cm2, PRO only), default 0.009 |
| `Cp` | Protein content (g/cm2, PRO only), default 0.001 |
| `eta_1` | PSI fluorescence quantum yield (P6D only), default 0.002 |
| `eta_2` | PSII fluorescence quantum yield (P6D only), default 0.01 |

Returns: `(reflectances_string, transmittances_string)` as comma-separated strings.

### FvCB Photosynthesis Model (from SCOPE)

```python
from FvCB_from_SCOPE import PhotosynthesisModel
model = PhotosynthesisModel(plant_type, P, O2, Q, Cs_ppm, es, leaf_tmp_k,
                             Vcmx25, RdPerVcmax25, BallBerrySlope, BallBerry0)
Ci_ppm, gs, A, Ag, Vc, Vs, Ve, CO2_per_electron = model.run()
```

| Parameter | Description |
|-----------|-------------|
| `plant_type` | `"C3"` or `"C4"` |
| `P` | Atmospheric pressure (Pa) |
| `O2` | Oxygen concentration (ppm) |
| `Q` | Photosynthetic photon flux (umol/m2/s) |
| `Cs_ppm` | Leaf surface CO2 (ppm) |
| `es` | Saturated vapor pressure (kPa) |
| `leaf_tmp_k` | Leaf temperature (Kelvin) |
| `Vcmx25` | Max RuBisCO carboxylation rate at 25C (umol/m2/s) |
| `RdPerVcmax25` | Respiration rate ratio |
| `BallBerrySlope` | Ball-Berry slope parameter |
| `BallBerry0` | Ball-Berry intercept parameter |

**Returns:** `(Ci_ppm, gs, A, Ag, Vc, Vs, Ve, CO2_per_electron)`
- `Ci_ppm`: Intercellular CO2 (ppm)
- `gs`: Stomatal conductance
- `A`: Net photosynthetic rate
- `Ag`: Gross photosynthetic rate
- `Vc`, `Vs`, `Ve`: Carboxylation-limited, RuBP-limited, TPU-limited rates
- `CO2_per_electron`: CO2 fixed per electron

---

## SimpleCrownGenerator

### Enums

```python
from SimpleCrownGenerator import LAD, CrownShape, LeafShape
```

**LAD (Leaf Angle Distribution):**
`UNIFORM`, `SPHERICAL`, `ERECTOPHILE`, `EXTREMOPHILE`, `PLANOPHILE`, `PLAGIOPHILE`

**CrownShape:**
`CUBE`, `ELLIPSOID`, `CYLINDER`, `CONE`, `ASYMMETRIC_GAUSSIAN`

**LeafShape:**
`SQUARE`, `DISK`

### CrownGenerator Class

```python
from SimpleCrownGenerator import CrownGenerator
gen = CrownGenerator()
```

| Property | Type | Description |
|----------|------|-------------|
| `leaf_angle_dist` | str | Leaf angle distribution type |
| `leaf_volume_density` | float | Leaf area per unit volume (m2/m3) |
| `crown_diameter_SN` | float | Crown diameter south-north (m) |
| `crown_diameter_EW` | float | Crown diameter east-west (m) |
| `crown_height` | float | Crown height (m) |
| `crown_shape` | str | Shape from CrownShape enum |
| `leaf_shape` | str | Shape from LeafShape enum |
| `single_leaf_area` | float | Area of individual leaf (m2) |
| `has_trunk` | bool | Generate trunk |
| `trunk_height` | float | Trunk height (m) |
| `dbh` | float | Diameter at breast height (m) |
| `has_branches` | bool | Generate branches |
| `clumping_factor` | float | Clumping [0,1] |

| Method | Description |
|--------|-------------|
| `get_crown_volume()` | Compute crown volume based on shape |
| `get_trunk_radius_at_height(h)` | Trunk radius at height h |
| `get_trunk_surface_area()` | Trunk surface area |
| `get_trunk_volume()` | Trunk volume |
| `generate_crown(dist_obj_path)` | Generate OBJ file with crown geometry |

---

## SDKCodeGenerator

Reverse-engineer a LESS GUI simulation project into a Python SDK script.

```python
from SDKCodeGenerator import SDKCodeGenerator
gen = SDKCodeGenerator(sim_dir)
gen.generate(out_script_path)
```

| Parameter | Description |
|-----------|-------------|
| `sim_dir` | Path to existing LESS simulation directory |
| `out_script_path` | Output Python script path |

The generated script includes: terrain, optical properties, objects, instances, sensor, illumination, observation, and simulation execution code.

---

## RuntimeScene (Advanced — Ray Intersection)

```python
sim.enable_runtime_modification_of_properties(True)
sim.save_sim_project()
sim.start()
rt_scene = sim.get_runtime_scene()
rt_scene.load_scene()

# Ray intersection query
result = rt_scene.ray_intersect(origin=(50, 50, 100), direction=(0, 0, -1))
# Returns: ((x, y, z), shape_name) or None
```
