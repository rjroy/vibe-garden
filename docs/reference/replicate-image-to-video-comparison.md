# Replicate's image-to-video models: A complete pricing and capabilities guide

**The image-to-video landscape on Replicate now offers 30+ models** spanning open-source options at **$0.002/second** to premium proprietary models reaching **$0.28/second**. Your choice depends on three key tradeoffs: photorealistic vs stylized content, strict keyframe control vs creative freedom, and budget vs generation quality.

Replicate's official image-to-video collection includes models from Kuaishou (Kling), MiniMax (Hailuo), Luma (Ray/Dream Machine), Alibaba (Wan), ByteDance (Seedance), PixVerse, Runway, and others. All support commercial use, with pricing updated as of July 2025.

## Pricing breakdown by cost per second of output video

The most cost-effective option is **Wan 2.2-i2v-fast at $0.002-0.004/second**, generating 5-second 720p clips for just $0.01-0.02. Premium models like **Kling v2.1-master reach $0.28/second** but deliver superior quality and dynamics.

| Model | Resolution | Duration | Price/Video | Cost/Second |
|-------|-----------|----------|-------------|-------------|
| **Wan 2.2-i2v-fast** | 480-720p | 5s | $0.01-0.02 | **$0.002-0.004** |
| WaveSpeed Wan 2.1 | 480-720p | 5s | $0.05-0.11 | $0.01-0.02 |
| Hailuo 02-fast | 512p | 6-10s | $0.10-0.17 | $0.017 |
| Luma Ray Flash 2 | 540-720p | 5-9s | $0.14-0.44 | $0.028-0.049 |
| Hailuo 02 Standard | 768p | 6-10s | $0.27-0.45 | **$0.045** |
| Runway Gen-4 Turbo | 720p | 5-10s | $0.25-0.50 | $0.05 |
| Kling v2.5 Turbo Pro | 1080p | 5-10s | $0.35-0.70 | **$0.07** |
| Hailuo 02 Pro | 1080p | 6s | $0.48 | $0.08 |
| MiniMax video-01 | 720p | 6s | $0.50 | $0.083 |
| Seedance Pro | 1080p | 5-10s | $0.62-1.50 | $0.12-0.15 |
| Luma Ray 2 | 720p | 5-9s | $0.71-1.27 | **$0.14** |
| Kling v2.1-master | 1080p | 5-10s | $1.40-2.80 | $0.28 |

For **720p ~5-second clips**, expect costs between **$0.05 (Wan accelerated) and $0.71 (Luma Ray 2)**, with sweet spots around **$0.25-0.50** for Kling v2.5 Turbo Pro and Runway Gen-4 Turbo.

## Animation and stylized content excels with specific models

Three models stand out for **animation, cartoon, and Live2D content**:

**MiniMax video-01-live ($0.50/video, $0.10/sec)** is the only model explicitly trained for Live2D animation. It maintains frame-to-frame consistency for anime/manga characters, supports seamless expression transitions, and preserves 2D illustration styles while adding natural motion. Best for VTuber-style content, digital portraits, and general illustration animation.

**ToonCrafter ($0.086/run)** specializes in cartoon interpolation—upload two keyframes and the AI generates smooth in-between animation preserving your art style. Runs at 768×512 resolution, 16 frames output. Ideal for traditional animation workflows and frame-by-frame cartoon creation.

**PixVerse v4 ($0.30-0.80/video)** handles stylized content well with built-in support for anime, 3D animation, comic, cyberpunk, and claymation styles. Its **start AND end frame** specification makes it excellent for morphing and style transitions.

For **photorealistic/live-action content**, prioritize:
- **Kling v2.1/v2.5**: Outstanding physics, human motion, facial expressions, and cinematic camera movements
- **Hailuo 02**: Ranks #2 globally on Artificial Analysis benchmarks, excels at "real world physics" including fluid dynamics, gravity, and complex character motion
- **Runway Gen-4**: Superior character consistency and world-building coherence

## Prompt adherence varies significantly across model families

**Top performers for prompt faithfulness:**

**Seedance-1 Pro** currently leads prompt adherence benchmarks, ranking #1 on Artificial Analysis ELO scores. It accurately parses complex natural language and handles multi-shot narrative coherence.

**Kling v2.5 Turbo Pro** is specifically marketed for "remarkable prompt adherence" and responds well to cinematographic language. The CFG scale parameter (0-1, default 0.5) lets you trade creative freedom against strict prompt following. Prompts up to **2,500 characters** are supported with negative prompts available.

**MiniMax/Hailuo models** deliver strong prompt adherence but work best with "director-style" prompts—concrete shot grammar (framing, lens, motion verbs) rather than emotional descriptions. The `prompt_optimizer=false` setting reduces unwanted alterations.

**Luma Ray** handles mood and atmosphere well but struggles when combining multiple camera movements in a single prompt. Users report erratic behavior unless the "enhanced prompt" option is disabled.

**Wan models** show inconsistent camera control—direction specification (left/right) is "basically random chance" in v2.1, though v2.2 significantly improves with dolly movements working reliably. CFG scale 5-7 recommended for prompt adherence.

## Input image handling differs by model architecture

Models treat input images in fundamentally different ways:

**Strict starting frame (first frame conditioning)**—the input becomes the literal first frame:
- Kling (all versions)
- MiniMax/Hailuo standard I2V
- Wan (all versions)
- Runway Gen-4
- Seedance
- Leonardo Motion

**Start AND end frame specification (keyframe interpolation)**—define both beginning and destination:
- **Luma Ray 2**: Full `frame0` and `frame1` keyframe support via API
- **PixVerse v4**: Dedicated "Transition (First-last frame)" feature
- **Kling v1.6-pro/v2.1 (pro mode)**: End frame available in pro configurations
- **Seedance-1**: Both lite and pro support start/end frame control
- **Hailuo 02**: End frame supported at 768p (6s, 10s) and 1080p (6s only)

**Subject reference mode (maintain character identity across dynamic scenes)**:
- **MiniMax video-01 (S2V-01)**: Extracts and preserves facial features from reference image
- **Kling v1.6/v2.1 with subject reference**: Available on specific model variants

**Image influence/strength parameters:**

| Model | Strength Control | Parameter |
|-------|-----------------|-----------|
| Kling | Yes | `cfg_scale` (0-1, default 0.5) |
| Wan | Yes | `strength/denoise` (0.35-0.65), `guide_scale`, `steps` |
| Luma Modify Video | Yes | 3-level slider: Adhere/Flex/Reimagine |
| MiniMax | No explicit control | Image acts as definitive first frame |
| PixVerse | No | Direct keyframe specification |

## Output specifications comparison across all major models

| Model | Max Resolution | Durations | Frame Rate | Aspect Ratios |
|-------|---------------|-----------|------------|---------------|
| **Kling v2.5 Turbo Pro** | 1080p | 5s, 10s | 30fps | 16:9, 9:16, 1:1 |
| **Kling v2.1-master** | 1080p | 5s, 10s | 30fps | 16:9, 9:16, 1:1 |
| **Kling v1.6-pro** | 1080p | 5s, 10s | 24fps | Multiple |
| **Hailuo 02 Pro** | 1080p | 6s (10s at 768p) | 24fps | Standard |
| **Hailuo 02 Standard** | 768p | 6s, 10s | 24fps | Standard |
| **MiniMax video-01** | 720p | 6s | 25fps | Standard |
| **Luma Ray 2** | 720p (4K via upscale) | 5s, 9s | 24fps | 7 ratios |
| **Luma Ray Flash 2** | 720p | 5s, 9s | 24fps | 7 ratios |
| **Seedance Pro** | 1080p | 5s, 10s | 24fps | Multiple |
| **Seedance Lite** | 720p | 5s, 10s | 24fps | Multiple |
| **PixVerse v4** | 1080p | 5s, 8s | 30fps | 16:9, 9:16, 1:1, 4:3 |
| **Runway Gen-4 Turbo** | 720p | 5s, 10s | Standard | Multiple |
| **Wan 2.5** | 1080p | up to 10s | 16fps | 6 options |
| **Wan 2.1/2.2** | 720p | 5s | 16fps | Auto, 16:9, 9:16, 1:1 |

**Key limitations to note:**
- Wan models run at **16fps** (vs 24-30fps for others)—more cinematic but less smooth
- Hailuo 02 Pro only supports **6 seconds maximum** at 1080p
- Most models cap at **10 seconds**; Luma extends to ~30s with quality degradation

## Recommendations by use case

**Budget prototyping**: Wan 2.2-i2v-fast ($0.01-0.02/video) provides the fastest iteration at lowest cost

**Animation/stylized content**: MiniMax video-01-live for Live2D, ToonCrafter for cartoon interpolation, PixVerse v4 for style variety

**Photorealistic production**: Kling v2.5 Turbo Pro offers best value ($0.07/sec, 1080p, strong physics), or Hailuo 02 for #2-ranked benchmark quality

**Precise storyboarding**: PixVerse v4 or Luma Ray 2 with start+end frame specification for controlled transitions

**Maximum quality**: Kling v2.1-master ($0.28/sec) or Google Veo 3 ($6/video) for premium cinematic output

## Conclusion

The Replicate image-to-video ecosystem has matured significantly, with clear segmentation emerging. **Kling v2.5 Turbo Pro** represents the current sweet spot—62% cheaper than v2.1 Master while maintaining 1080p quality and strong prompt adherence at $0.07/second. For animation, **video-01-live** is the only purpose-built Live2D model. Budget-conscious developers should leverage **Wan's open-source variants** at under $0.02/video, accepting the 16fps tradeoff. The end-frame specification feature in Luma and PixVerse enables transition effects impossible with single-keyframe models—a capability worth the premium for morphing and scene-transition use cases.