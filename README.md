# less-skill

AI coding assistant skill/rule for the [LESS](http://lessrt.org/) 3D radiative transfer model. It enables AI assistants (Claude Code, Cursor, Windsurf, etc.) to generate correct pyLessSDK simulation code with domain knowledge built in.

## What's included

| File | Description |
|------|-------------|
| `SKILL.md` | Core guide: architecture, workflow, key concepts, rules & restrictions |
| `api-reference.md` | Complete API reference for all pyLessSDK classes |
| `examples.md` | 16 working examples covering all simulation types |
| `faq.md` | 16 common domain Q&A (leaf optics, BRF, turbid vs mesh, etc.) |
| `helpers.py` | Validation utilities (band consistency, spp check, etc.) |

## Installation

### Claude Code

```bash
# Clone into your project's .claude/skills directory
git clone https://github.com/jianboqi/less-skill .claude/skills/less-sdk

# Or clone into global skills (available to all projects)
git clone https://github.com/jianboqi/less-skill ~/.claude/skills/less-sdk
```

Also add the LESS installation path to your project's `CLAUDE.md`:

```
LESS installation directory: D:\LESS
```

Then use the skill via:

```
/less-sdk create a broadleaf forest scene with LAI=3
```

### Cursor

Copy the content of `SKILL.md` into `.cursor/rules/less-sdk.md` in your project:

```bash
mkdir -p .cursor/rules
cp less-skill/SKILL.md .cursor/rules/less-sdk.md
```

### Windsurf

Copy into `.windsurf/rules/`:

```bash
mkdir -p .windsurf/rules
cp less-skill/SKILL.md .windsurf/rules/less-sdk.md
```

### Other AI Coding Tools

Most AI coding assistants support project-level instruction files. Copy `SKILL.md` (and optionally the other reference files) into the tool's designated rules/instructions directory.

## What can it do?

Once installed, your AI assistant can:

- Generate complete LESS simulation scripts from natural language descriptions
- Configure sensors (orthographic, perspective, fisheye, LiDAR, photon tracing, TRAC)
- Set up optical properties using PROSPECT-D, GSV soil, Fluspect models
- Build forest scenes from statistical parameters (LAI, FCC) via ForestSceneBuilder
- Handle batch simulations with runtime modification
- Avoid common pitfalls (20+ built-in rules and 14 hard restrictions)
- Answer domain questions about radiative transfer, BRF, LAI, fluorescence, etc.

## Requirements

- [LESS](http://lessrt.org/) installed on your system
- Python with NumPy

## License

MIT

## Citation

If LESS is used in your work, please cite:

> Qi, J., Xie, D., Yin, T., Yan, G., Gastellu-Etchegorry, J.-P., Li, L., Zhang, W., Mu, X., Norford, L.K., 2019. LESS: LargE-Scale remote sensing data and image simulation framework over heterogeneous 3D scenes. Remote Sensing of Environment 221, 695-706.
