# pyLessSDK FAQ — Common Domain Questions

When users ask physics or methodology questions related to LESS simulations, refer to these answers.

---

## Q1: Can I compute transmittance from reflectance using T = 1 - R?

**No.** The correct energy conservation is **R + T + A = 1** (reflectance + transmittance + absorptance). Leaf absorption varies dramatically by wavelength:

- **Visible (400-700nm)**: chlorophyll/carotenoid absorption is very high (A ~ 80-90%), so R+T << 1
- **NIR (700-1300nm)**: absorption is very low (A ~ 0), so R+T ≈ 1
- **SWIR (1300-2500nm)**: water absorption bands cause high A again

Using T = 1-R will grossly overestimate transmittance in visible bands.

**Correct approach**: Use PROSPECT-D model inversion. Fit the known reflectance spectrum by adjusting leaf biochemical parameters (N, Cab, Car, Cw, Cm), then the model outputs physically consistent R and T together:

```python
from Prospect5AndD import prospectD
ref, trans = prospectD(wl=wavelengths, N=1.5, Cab=40, Car=8, Cw=0.01, Cm=0.009, Anth=0, BP=0)
```

---

## Q2: What is the difference between BRF and reflectance?

**BRF (Bidirectional Reflectance Factor)** is the ratio of reflected radiance from a surface to that from an ideal Lambertian surface under the same illumination. It is dimensionless and can exceed 1 (e.g., in the hotspot direction). LESS orthographic sensor outputs radiance images; `PostProcessing.radiance2brf()` converts them to BRF by dividing by the incoming irradiance.

**Reflectance** (hemispherical) integrates over all viewing directions. BRF is directional — it depends on both sun and view angles. For remote sensing validation, BRF is typically what satellite sensors measure.

---

## Q3: When should I use turbid medium vs. explicit triangle mesh for tree crowns?

| | Turbid Medium | Triangle Mesh |
|---|---|---|
| **Speed** | Faster (volumetric scattering, no leaf geometry) | Slower (millions of leaf triangles) |
| **Accuracy** | Good for canopy-level statistics (LAI, BRF) | Better for detailed within-crown radiation |
| **Memory** | Low | High (large OBJ files) |
| **Use case** | Large scenes, parameter studies, PROSAIL-like simulations | Detailed single-tree studies, LiDAR simulation |
| **Hotspot** | Needs `hotspot_factor` parameter | Naturally captured by geometry |

Rule of thumb: use turbid for scene-level simulations (>50 trees), triangle mesh for detailed studies or when crown internal structure matters.

---

## Q4: What does sample_per_pixel (spp) control and how do I choose a value?

`sample_per_pixel` controls how many rays are traced per pixel. More rays = less noise but longer runtime.

- **Preview/debugging**: 16-32 spp
- **Production**: 64-256 spp
- **For orthographic sensor**: also check spatial density — aim for >= 64 samples per m². If pixels are large (low resolution image over big scene), increase spp accordingly.

Noise appears as random per-pixel variation. If the result image looks grainy, increase spp. Double spp = half the variance (but double the time).

---

## Q5: How does the atmosphere model affect simulation results?

LESS supports two atmosphere modes:

- **SKY_TO_TOTAL** (default): Simple ratio of diffuse sky radiation to total. Set per-band via `ill.set_ats_percentage()`. Value of 0 = direct sun only, 0.5 = half diffuse.
- **ATMOSPHERE (6S)**: Full atmospheric radiative transfer using 6SV model. Computes atmospheric path radiance, transmittance, and sky radiance based on aerosol type, optical thickness, and atmospheric profile.

For most research, SKY_TO_TOTAL with a reasonable ratio (0.1-0.2 for clear sky) is sufficient. Use 6S when you need physically accurate TOA radiance or when simulating specific atmospheric conditions.

---

## Q6: Why is my simulation result all black or all white?

Common causes:

- **All black**: sun zenith >= 90 (no illumination), wrong optical properties (all zeros), or sensor pointing in wrong direction
- **All white / saturated**: sample_per_pixel too low causing extreme noise, or optical property values > 1
- **Partially black edges**: scene too small for viewing angle — use `set_repetitive_scene()` for flat terrain
- **Uniform gray**: forgot to set optical properties, using defaults

Check: illumination angles, optical property values (should be 0-1), sensor/observation configuration, and scene extent.

---

## Q7: What is the difference between forward (photon tracing) and backward (orthographic/perspective) ray tracing?

- **Backward tracing** (SensorOrthographic, SensorPerspective, SensorFisheye): traces rays from sensor into scene. Efficient for generating images. Each pixel gets a radiance value.
- **Forward tracing** (SensorPhotonTracing): traces rays from the sun into the scene, records where photons go. Needed for:
  - Multi-angle BRF (many directions simultaneously)
  - fPAR (fraction of absorbed PAR)
  - Fluorescence emission
  - Up/down radiation profiles
  - Photosynthesis products

Use backward tracing for images, forward tracing for radiation budget and multi-angle products.

---

## Q8: How do I simulate a specific satellite sensor (e.g., Landsat, Sentinel-2)?

Do NOT set the sensor bands to match the satellite's broad bandpass directly. Instead:

1. Simulate narrowband hyperspectral (1nm resolution) covering the satellite band range
2. Apply the satellite's spectral response function (SRF) in post-processing to compute broadband values

This avoids errors from assuming uniform sensitivity across the bandpass. The SRF can be obtained from the satellite operator's documentation.

---

## Q9: What coordinate system does LESS use?

- Origin `(0, 0)` is at one corner of the scene
- X and Y are horizontal, Z is vertical (up)
- Scene extent: `(0, 0)` to `(extent_width, extent_height)` in meters
- Sun azimuth: 0 = North, 90 = East, 180 = South, 270 = West
- View azimuth follows the same convention
- Zenith: 0 = straight down (nadir) for view, straight up for sun

---

## Q10: Is the Python SDK faster than the GUI?

**No.** Simulation speed is identical — both call the same C++ rendering core. The bottleneck is rays per pixel and scene complexity, not the frontend.

**Tips for speeding up large scene simulations** (e.g., 500m x 500m at 0.5m resolution):

1. **Reduce `sample_per_pixel`** — this is the main speed lever. Try 32-64 first; increase only if results are too noisy.
2. **Enable "only first order" for four-component products** — if you only need sunlit/shaded soil/vegetation fraction images (`has_four_components_product = True`), set `sensor.record_only_direct = True`. This skips multiple scattering and is much faster.
3. **Use runtime modification for multi-angle batch** — avoids reloading the scene for each angle.

---

## Q11: Why does changing the observation height (obs_R) in orthographic mode not change the image?

Orthographic is **parallel projection** — all rays are parallel, so the projection distance has no effect on the image. The image only depends on the viewing angle and the sub_region (ground coverage). If you need images from different heights (with perspective effects like foreshortening), use **SensorPerspective** instead.

---

## Q12: How do I simulate leaf-level total fluorescence (not just canopy-level)?

Use **SensorPhotonTracing** with both fPAR and fluorescence enabled. This mode traces photons from the sun through the canopy and records absorption and fluorescence emission at every leaf interaction:

```python
sensor = SensorPhotonTracing()
sensor.enable_fpar_product(True)
sensor.enable_Fluor_product(True)
sensor.set_sun_ray_resolution(0.003)
```

The fPAR product gives absorbed radiation per layer; combined with fluorescence yield, this provides leaf-level total fluorescence. See the fluorescence user manual for details on multi-layer fluorescence simulation.

---

## Q13: How do I simulate mixed pixels (vegetation + water + bare soil) for spectral index construction?

**Do NOT** just assign different spectra to a flat land cover map — that is equivalent to linear spectral mixing and ignores 3D vegetation structure and multiple scattering between vegetation and background.

**Correct approach**:
1. Create the background (water, bare soil) as a **land cover albedo map** for the terrain (`terrain.set_terr_brdf_type(TERRAIN_BRDF_TYPE.LAND_COVER_MAP)`)
2. Place 3D vegetation OBJ objects **on top** of the background
3. Use **SensorOrthographic** to get per-pixel reflectance images (not PhotonTracing, which gives scene-average spectra)
4. Use **four-component product** (`sensor.has_four_components_product = True`) to get per-pixel vegetation/soil fractions
5. Aggregate fine-resolution images to coarser pixels to get mixed spectra with known component fractions

For vegetation optical properties, use **PROSPECT model** to generate component-level (leaf, stem) spectra — do NOT extract from satellite imagery, as those are pixel-level mixed spectra, not component spectra.

---

## Q14: How do I compute effective LAI (LAI_eff) from LESS simulations?

LESS's `compute_scene_lai()` returns **true LAI** (actual leaf area / ground area). Effective LAI accounts for clumping and is derived from gap fraction:

**LAI_eff = -ln(T) * cos(theta) / G**

Where:
- `T` = gap fraction (from four-component product: fraction of pixels seeing soil at a given angle)
- `theta` = view zenith angle
- `G` = leaf projection function (0.5 for spherical LAD)

Steps:
1. Simulate four-component image at desired zenith angle with `sensor.has_four_components_product = True`
2. Compute gap fraction T from the sunlit/shaded soil fraction
3. Apply Beer-Lambert formula above

**Note**: clumping index = LAI_eff / LAI_true. It is NOT a geometric property — it varies with viewing direction and is defined as the ratio between effective and true LAI.

---

## Q15: When should I use orthographic (per-pixel image) vs photon tracing (scene-average spectrum)?

| Need | Sensor |
|------|--------|
| Per-pixel reflectance/BRF image | SensorOrthographic |
| Scene-average BRF at multiple angles | SensorPhotonTracing |
| Per-pixel vegetation/soil fraction | SensorOrthographic + `has_four_components_product` |
| fPAR, fluorescence, radiation budget | SensorPhotonTracing |
| Simulate satellite image | SensorOrthographic |
| BRDF characterization (many angles) | SensorPhotonTracing with virtual directions, or SensorOrthographic + `is_orthophoto_map` |

---

## Q16: Can LESS simulate thermal infrared?

Yes. Set `sensor.thermal_radiation = True` on the sensor. Temperature is assigned per object component (e.g., `temperature="T300"` for 300K) and per terrain. LESS computes emitted thermal radiance based on Planck's law. Use `PostProcessing.bt_single_img_processing()` to convert radiance to brightness temperature.
