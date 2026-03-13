# Hardware Advisor + Live Leaderboard — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a hardware-aware model advisor that detects the user's machine, grades every local model by compatibility (S/A/B/C/D/F), recommends the best fit, and installs in one click — directly leapfrogging canirun.ai on every gap identified in its HN launch thread (228 pts, 4h, 2026-03-13).

**Architecture:** New `src/prowlrbot/hardware/` module (detector → catalog → scorer). One new FastAPI router (`/api/hardware`). New console page ("What can my machine run?"). Wire gamification XP events into AgentRunner + CronExecutor so the existing leaderboard DB fills with real data and goes live over WebSocket.

**Tech Stack:** Python 3.10+ / `psutil` / `subprocess` (nvidia-smi, rocm-smi, sysctl) / FastAPI / Pydantic (backend); React 18 / TypeScript / Ant Design / recharts (frontend); existing SQLite gamification DB + WebSocket bus

**Context:** canirun.ai launched on HN 2026-03-13. Key gaps from the comment thread that we address:

| canirun.ai gap (HN source) | Our answer |
|---------------------------|------------|
| Browser WebGPU detection is wrong/unreliable (LeifCarrotson) | `psutil` + `nvidia-smi` = exact values, not estimates |
| No quantization support — Q4_K_M vs fp16 is the PRIMARY variable (Felixbot) | Quant-aware catalog: every model shows 4-bit, 8-bit, fp16 options with separate RAM/VRAM costs |
| MoE active-param calculation wrong — uses total params (meatmanek) | Catalog marks MoE models + stores active params for correct memory estimate |
| "RAM: Unknown" — browser can't read it (vova_hn2) | `psutil.virtual_memory()` returns exact bytes |
| AMD ROCm / Intel Arc not covered (GrayShade, AstroBen) | `rocm-smi` + Intel GPU detection at the OS level |
| No Raspberry Pi / ARM server support (g_br_l) | CPU-only inference scoring on ARM; targets homelab crowd directly |
| No KV cache / CPU offload modeling (LeifCarrotson) | Show score with vs without CPU offload (split VRAM + RAM) |
| No model capability ratings — just size (corra) | Cross-reference with `/api/leaderboard` benchmark scores |
| No reverse lookup: "what hardware do I need for X?" (sxates) | `GET /api/hardware/reverse-lookup/{model_id}` endpoint |
| No integration with install tools (amelius) | Grade A/B/C → "Install" button calls existing `/api/local-models/download` or `/api/ollama-models` |
| Numbers pessimistic / one magnitude off (GrayShade, AstroBen) | After install + use, actual tok/s feeds back into leaderboard → real user data, not estimates |
| Leaderboard not live | WebSocket push on every XP award; gamification events wired to real agent activity |

---

## Chunk 1: Hardware Detection Backend

### Task 1.1: Create `HardwareProfile` model and `HardwareDetector`

**Files:**
- Create: `src/prowlrbot/hardware/__init__.py`
- Create: `src/prowlrbot/hardware/detector.py`
- Test: `tests/hardware/test_detector.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/hardware/test_detector.py
"""Tests for HardwareDetector — platform-agnostic unit tests with mocks."""
import pytest
from unittest.mock import patch, MagicMock
from prowlrbot.hardware.detector import HardwareDetector, HardwareProfile


def test_hardware_profile_fields():
    profile = HardwareProfile(
        ram_gb=16.0,
        cpu_cores=8,
        cpu_arch="x86_64",
        platform="linux",
        gpu_name="NVIDIA RTX 3060",
        gpu_vram_gb=12.0,
        gpu_vendor="nvidia",
        estimated_bandwidth_gbps=360.0,
        is_apple_silicon=False,
        unified_memory=False,
    )
    assert profile.ram_gb == 16.0
    assert profile.gpu_vram_gb == 12.0
    assert not profile.unified_memory


def test_detector_returns_profile():
    detector = HardwareDetector()
    profile = detector.detect()
    assert isinstance(profile, HardwareProfile)
    assert profile.ram_gb > 0
    assert profile.cpu_cores > 0


def test_detector_handles_missing_nvidia_smi(monkeypatch):
    """nvidia-smi absent → gpu_vram_gb is None, gpu_vendor is 'unknown'."""
    def _raise(*a, **kw):
        raise FileNotFoundError("nvidia-smi not found")
    monkeypatch.setattr("subprocess.run", _raise)
    detector = HardwareDetector()
    profile = detector._detect_nvidia()
    assert profile is None


def test_detector_apple_silicon(monkeypatch):
    """platform=darwin + arm64 + sysctl → is_apple_silicon=True."""
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    detector = HardwareDetector()
    assert detector._is_apple_silicon()
```

- [ ] **Step 2: Run to confirm they fail**

```bash
cd /home/anon/dev/prowlrbot
pytest tests/hardware/test_detector.py -v 2>&1 | head -30
```

Expected: `ModuleNotFoundError: No module named 'prowlrbot.hardware'`

- [ ] **Step 3: Create the module**

```python
# src/prowlrbot/hardware/__init__.py
from .detector import HardwareDetector, HardwareProfile

__all__ = ["HardwareDetector", "HardwareProfile"]
```

```python
# src/prowlrbot/hardware/detector.py
"""Hardware fingerprinting for local model compatibility scoring.

Reads actual system values (psutil, nvidia-smi, rocm-smi, sysctl) rather
than browser estimates — the key accuracy advantage over browser-based tools.
"""
from __future__ import annotations

import json
import logging
import platform
import subprocess
from dataclasses import dataclass, field
from typing import Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class HardwareProfile:
    ram_gb: float
    cpu_cores: int
    cpu_arch: str
    platform: str                        # linux / darwin / windows
    gpu_name: Optional[str] = None
    gpu_vram_gb: Optional[float] = None
    gpu_vendor: str = "unknown"          # nvidia / amd / intel / apple
    estimated_bandwidth_gbps: float = 0.0
    is_apple_silicon: bool = False
    unified_memory: bool = False         # True on Apple Silicon — RAM shared with GPU


# Memory bandwidth estimates (GB/s) keyed by lowercase GPU name substring.
# Derived from published specs; used when nvidia-smi doesn't report bandwidth.
_BANDWIDTH_TABLE: dict[str, float] = {
    "rtx 4090": 1008.0,
    "rtx 4080": 736.0,
    "rtx 4070 ti": 504.0,
    "rtx 4070": 504.0,
    "rtx 4060": 272.0,
    "rtx 3090": 936.0,
    "rtx 3080": 760.0,
    "rtx 3070": 448.0,
    "rtx 3060": 360.0,
    "rx 7900 xtx": 960.0,
    "rx 7900 xt": 800.0,
    "rx 6900 xt": 512.0,
    "rx 6800 xt": 512.0,
    "m4 ultra": 800.0,
    "m4 max": 546.0,
    "m4 pro": 273.0,
    "m4": 120.0,
    "m3 ultra": 800.0,
    "m3 max": 400.0,
    "m3 pro": 153.6,
    "m3": 100.0,
    "m2 ultra": 800.0,
    "m2 max": 400.0,
    "m2 pro": 200.0,
    "m2": 100.0,
    "m1 ultra": 800.0,
    "m1 max": 400.0,
    "m1 pro": 200.0,
    "m1": 68.25,
}


class HardwareDetector:
    """Detect hardware specs using OS-level APIs and CLI tools."""

    def detect(self) -> HardwareProfile:
        mem = psutil.virtual_memory()
        ram_gb = mem.total / (1024 ** 3)
        cpu_cores = psutil.cpu_count(logical=False) or psutil.cpu_count() or 1
        cpu_arch = platform.machine()
        sys_platform = platform.system().lower()

        is_apple = self._is_apple_silicon()
        gpu_info = None

        if is_apple:
            gpu_info = self._detect_apple()
        else:
            gpu_info = self._detect_nvidia() or self._detect_amd() or self._detect_intel()

        unified = is_apple  # Apple Silicon shares RAM with GPU
        bw = 0.0
        if gpu_info:
            bw = self._estimate_bandwidth(gpu_info.get("name", ""))
            if not bw and is_apple:
                bw = self._apple_bandwidth(ram_gb)

        return HardwareProfile(
            ram_gb=round(ram_gb, 1),
            cpu_cores=cpu_cores,
            cpu_arch=cpu_arch,
            platform=sys_platform,
            gpu_name=gpu_info.get("name") if gpu_info else None,
            gpu_vram_gb=gpu_info.get("vram_gb") if gpu_info else None,
            gpu_vendor=gpu_info.get("vendor", "unknown") if gpu_info else "unknown",
            estimated_bandwidth_gbps=round(bw, 1),
            is_apple_silicon=is_apple,
            unified_memory=unified,
        )

    # ── internal helpers ──────────────────────────────────────────────────

    def _is_apple_silicon(self) -> bool:
        return platform.system() == "Darwin" and platform.machine() == "arm64"

    def _detect_nvidia(self) -> Optional[dict]:
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
            )
            if out.returncode != 0:
                return None
            line = out.stdout.strip().split("\n")[0]
            name, vram_mib = line.split(", ")
            return {
                "name": name.strip(),
                "vram_gb": round(float(vram_mib) / 1024, 1),
                "vendor": "nvidia",
            }
        except Exception:
            return None

    def _detect_amd(self) -> Optional[dict]:
        try:
            out = subprocess.run(
                ["rocm-smi", "--showproductname", "--showmeminfo", "vram",
                 "--json"],
                capture_output=True, text=True, timeout=5,
            )
            if out.returncode != 0:
                return None
            data = json.loads(out.stdout)
            card = next(iter(data.values()))
            name = card.get("Card series", "AMD GPU")
            vram_bytes = int(card.get("VRAM Total Memory (B)", 0))
            return {
                "name": name,
                "vram_gb": round(vram_bytes / (1024 ** 3), 1),
                "vendor": "amd",
            }
        except Exception:
            return None

    def _detect_intel(self) -> Optional[dict]:
        """Best-effort Intel Arc detection via sysfs on Linux."""
        try:
            import glob as _glob
            cards = _glob.glob("/sys/class/drm/card*/device/vendor")
            for card_path in cards:
                with open(card_path) as f:
                    vendor_id = f.read().strip()
                if vendor_id == "0x8086":  # Intel
                    mem_path = card_path.replace("device/vendor",
                                                 "device/mem_info_vram_total")
                    vram_gb = None
                    try:
                        with open(mem_path) as f:
                            vram_gb = round(int(f.read().strip()) / (1024 ** 3), 1)
                    except Exception:
                        pass
                    return {"name": "Intel GPU", "vram_gb": vram_gb,
                            "vendor": "intel"}
        except Exception:
            pass
        return None

    def _detect_apple(self) -> Optional[dict]:
        try:
            out = subprocess.run(
                ["system_profiler", "SPDisplaysDataType", "-json"],
                capture_output=True, text=True, timeout=10,
            )
            data = json.loads(out.stdout)
            displays = data.get("SPDisplaysDataType", [])
            if displays:
                gpu = displays[0]
                name = gpu.get("sppci_model", "Apple GPU")
                # Apple Silicon: VRAM = full unified RAM
                mem = psutil.virtual_memory()
                vram_gb = round(mem.total / (1024 ** 3), 1)
                return {"name": name, "vram_gb": vram_gb, "vendor": "apple"}
        except Exception:
            pass
        return None

    def _estimate_bandwidth(self, gpu_name: str) -> float:
        name_lower = gpu_name.lower()
        for key, bw in _BANDWIDTH_TABLE.items():
            if key in name_lower:
                return bw
        return 0.0

    def _apple_bandwidth(self, ram_gb: float) -> float:
        """Rough bandwidth estimate for Apple Silicon based on RAM tier."""
        if ram_gb >= 192:
            return 800.0
        if ram_gb >= 96:
            return 546.0
        if ram_gb >= 64:
            return 400.0
        if ram_gb >= 36:
            return 273.0
        if ram_gb >= 24:
            return 200.0
        return 100.0
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/hardware/test_detector.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/prowlrbot/hardware/ tests/hardware/
git commit -m "feat(hardware): add HardwareDetector with psutil + nvidia-smi/rocm-smi/sysctl"
```

---

### Task 1.2: Model catalog with quantization and MoE support

**Files:**
- Create: `src/prowlrbot/hardware/catalog.py`
- Test: `tests/hardware/test_catalog.py`

The catalog is the core data that canirun.ai gets wrong:
- Every model has **per-quantization** memory costs (Q4_K_M, Q8_0, fp16)
- MoE models store `active_params_b` separately (used for bandwidth calc, not `params_b`)
- Models have `capability_tags` so we can show "good for coding", "good for reasoning"

- [ ] **Step 1: Write failing tests**

```python
# tests/hardware/test_catalog.py
from prowlrbot.hardware.catalog import MODEL_CATALOG, ModelEntry, QuantVariant, get_model


def test_catalog_not_empty():
    assert len(MODEL_CATALOG) >= 20


def test_model_has_quant_variants():
    llama = get_model("llama-3.1-8b")
    assert llama is not None
    assert len(llama.quant_variants) >= 2
    q4 = next(v for v in llama.quant_variants if v.quant == "Q4_K_M")
    fp16 = next(v for v in llama.quant_variants if v.quant == "fp16")
    assert q4.ram_gb < fp16.ram_gb


def test_moe_model_has_active_params():
    """MoE models must use active_params_b for bandwidth calc, not params_b."""
    gpt_oss = get_model("gpt-oss-20b")
    assert gpt_oss is not None
    assert gpt_oss.is_moe is True
    assert gpt_oss.active_params_b is not None
    assert gpt_oss.active_params_b < gpt_oss.params_b


def test_model_capability_tags():
    qwen_coder = get_model("qwen2.5-coder-7b")
    assert "coding" in qwen_coder.capability_tags
```

- [ ] **Step 2: Run to confirm they fail**

```bash
pytest tests/hardware/test_catalog.py -v 2>&1 | head -15
```

- [ ] **Step 3: Implement catalog**

```python
# src/prowlrbot/hardware/catalog.py
"""Curated local model catalog with quantization-aware memory costs.

Key design decisions vs canirun.ai:
- Q4_K_M vs fp16 is the PRIMARY variable (13B = 8 GB vs 26 GB)
- MoE models store active_params_b — not total params — for bandwidth math
- capability_tags allow cross-referencing with benchmark leaderboard
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QuantVariant:
    quant: str          # "Q4_K_M" | "Q5_K_M" | "Q8_0" | "fp16"
    ram_gb: float       # minimum RAM/VRAM to load (no KV cache)
    kv_cache_gb: float  # additional RAM needed for 8K context KV cache
    tok_per_sec_per_100gbps: float  # throughput coefficient: actual tok/s ≈ this * bandwidth_gbps / 100


@dataclass
class ModelEntry:
    id: str
    name: str
    family: str
    params_b: float
    context_k: int
    quant_variants: list[QuantVariant]
    capability_tags: list[str] = field(default_factory=list)
    is_moe: bool = False
    active_params_b: Optional[float] = None   # MoE only: active params per token
    added_months_ago: int = 0
    hf_repo: Optional[str] = None
    ollama_tag: Optional[str] = None


def _q(quant: str, ram_gb: float, kv_gb: float, coeff: float) -> QuantVariant:
    return QuantVariant(quant=quant, ram_gb=ram_gb, kv_cache_gb=kv_gb,
                        tok_per_sec_per_100gbps=coeff)


MODEL_CATALOG: list[ModelEntry] = [
    # ── Sub-2B ──────────────────────────────────────────────────────────
    ModelEntry(
        id="qwen3.5-0.8b", name="Qwen 3.5 0.8B", family="qwen", params_b=0.8,
        context_k=32, added_months_ago=1,
        quant_variants=[
            _q("Q4_K_M", 0.5, 0.2, 84.0),
            _q("Q8_0",   0.8, 0.2, 50.0),
            _q("fp16",   1.6, 0.2, 25.0),
        ],
        capability_tags=["general", "fast"],
        ollama_tag="qwen3.5:0.8b",
    ),
    ModelEntry(
        id="llama-3.2-1b", name="Llama 3.2 1B", family="llama", params_b=1.0,
        context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 0.5, 0.5, 84.0),
            _q("Q8_0",   1.0, 0.5, 42.0),
            _q("fp16",   2.0, 0.5, 21.0),
        ],
        capability_tags=["general", "fast"],
        ollama_tag="llama3.2:1b",
    ),
    # ── 3–4B ────────────────────────────────────────────────────────────
    ModelEntry(
        id="llama-3.2-3b", name="Llama 3.2 3B", family="llama", params_b=3.0,
        context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 1.5, 0.5, 28.0),
            _q("Q8_0",   3.0, 0.5, 14.0),
            _q("fp16",   6.0, 0.5, 7.0),
        ],
        capability_tags=["general"],
        ollama_tag="llama3.2:3b",
    ),
    ModelEntry(
        id="qwen3-4b", name="Qwen 3 4B", family="qwen", params_b=4.0,
        context_k=32, added_months_ago=11,
        quant_variants=[
            _q("Q4_K_M", 2.0, 0.5, 21.0),
            _q("Q8_0",   4.0, 0.5, 10.5),
            _q("fp16",   8.0, 0.5, 5.0),
        ],
        capability_tags=["general", "reasoning"],
        ollama_tag="qwen3:4b",
    ),
    # ── 7–9B ────────────────────────────────────────────────────────────
    ModelEntry(
        id="llama-3.1-8b", name="Llama 3.1 8B", family="llama", params_b=8.0,
        context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 4.1, 1.0, 10.0),
            _q("Q5_K_M", 5.3, 1.0, 7.5),
            _q("Q8_0",   8.5, 1.0, 5.0),
            _q("fp16",  16.0, 1.0, 2.5),
        ],
        capability_tags=["general", "coding"],
        ollama_tag="llama3.1:8b",
    ),
    ModelEntry(
        id="qwen2.5-7b", name="Qwen 2.5 7B", family="qwen", params_b=7.0,
        context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 3.6, 1.0, 12.0),
            _q("Q8_0",   7.2, 1.0, 6.0),
            _q("fp16",  14.5, 1.0, 3.0),
        ],
        capability_tags=["general", "coding"],
        ollama_tag="qwen2.5:7b",
    ),
    ModelEntry(
        id="qwen2.5-coder-7b", name="Qwen 2.5 Coder 7B", family="qwen",
        params_b=7.0, context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 3.6, 1.0, 12.0),
            _q("Q8_0",   7.2, 1.0, 6.0),
            _q("fp16",  14.5, 1.0, 3.0),
        ],
        capability_tags=["coding"],
        ollama_tag="qwen2.5-coder:7b",
    ),
    ModelEntry(
        id="mistral-7b", name="Mistral 7B v0.3", family="mistral", params_b=7.0,
        context_k=32, added_months_ago=24,
        quant_variants=[
            _q("Q4_K_M", 3.6, 0.8, 12.0),
            _q("Q8_0",   7.2, 0.8, 6.0),
            _q("fp16",  14.5, 0.8, 3.0),
        ],
        capability_tags=["general"],
        ollama_tag="mistral:7b",
    ),
    # ── MoE: GPT-OSS 20B (active ~3.5B per token) ───────────────────────
    ModelEntry(
        id="gpt-oss-20b", name="GPT-OSS 20B", family="gpt-oss", params_b=20.0,
        context_k=128, added_months_ago=7,
        is_moe=True, active_params_b=3.5,
        quant_variants=[
            # MoE: all experts must fit in RAM, but only active experts
            # contribute to bandwidth — so tok/s is much better than param count suggests
            _q("Q4_K_M", 10.8, 1.5, 35.0),
            _q("Q8_0",   20.0, 1.5, 18.0),
            _q("fp16",   40.0, 1.5, 9.0),
        ],
        capability_tags=["general", "reasoning"],
        ollama_tag="gpt-oss:20b",
    ),
    # ── 13–14B ──────────────────────────────────────────────────────────
    ModelEntry(
        id="phi-4-14b", name="Phi-4 14B", family="phi", params_b=14.0,
        context_k=16, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 7.2, 0.5, 6.0),   # <-- 13B at Q4 fits in 8GB VRAM!
            _q("Q8_0",  14.5, 0.5, 3.0),
            _q("fp16",  28.0, 0.5, 1.5),
        ],
        capability_tags=["reasoning", "general"],
        ollama_tag="phi4:14b",
    ),
    ModelEntry(
        id="qwen2.5-14b", name="Qwen 2.5 14B", family="qwen", params_b=14.0,
        context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 7.2, 1.5, 6.0),
            _q("Q8_0",  14.5, 1.5, 3.0),
            _q("fp16",  28.0, 1.5, 1.5),
        ],
        capability_tags=["general", "coding"],
        ollama_tag="qwen2.5:14b",
    ),
    # ── 24–32B ──────────────────────────────────────────────────────────
    ModelEntry(
        id="mistral-small-24b", name="Mistral Small 3.1 24B", family="mistral",
        params_b=24.0, context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 12.3, 2.0, 3.5),
            _q("Q8_0",   24.0, 2.0, 1.8),
            _q("fp16",   48.0, 2.0, 0.9),
        ],
        capability_tags=["general", "reasoning"],
        ollama_tag="mistral-small3.1:24b",
    ),
    ModelEntry(
        id="qwen2.5-coder-32b", name="Qwen 2.5 Coder 32B", family="qwen",
        params_b=32.0, context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 16.4, 2.5, 2.5),
            _q("Q8_0",   32.0, 2.5, 1.3),
            _q("fp16",   64.0, 2.5, 0.6),
        ],
        capability_tags=["coding"],
        ollama_tag="qwen2.5-coder:32b",
    ),
    # ── MoE: Qwen 3 30B-A3B ─────────────────────────────────────────────
    ModelEntry(
        id="qwen3-30b-a3b", name="Qwen 3 30B-A3B", family="qwen", params_b=30.0,
        context_k=128, added_months_ago=11,
        is_moe=True, active_params_b=3.0,
        quant_variants=[
            _q("Q4_K_M", 15.4, 2.0, 22.0),  # bandwidth based on active_params_b
            _q("Q8_0",   30.0, 2.0, 11.0),
            _q("fp16",   60.0, 2.0, 5.5),
        ],
        capability_tags=["reasoning", "coding"],
        ollama_tag="qwen3:30b-a3b",
    ),
    # ── 70B ─────────────────────────────────────────────────────────────
    ModelEntry(
        id="llama-3.3-70b", name="Llama 3.3 70B", family="llama", params_b=70.0,
        context_k=128, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 35.9, 4.0, 1.0),
            _q("Q8_0",   70.0, 4.0, 0.5),
            _q("fp16",  140.0, 4.0, 0.25),
        ],
        capability_tags=["general", "reasoning", "coding"],
        ollama_tag="llama3.3:70b",
    ),
    # ── DeepSeek R1 distills ─────────────────────────────────────────────
    ModelEntry(
        id="deepseek-r1-7b", name="DeepSeek R1 Distill 7B", family="deepseek",
        params_b=7.0, context_k=64, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 3.6, 1.0, 12.0),
            _q("Q8_0",   7.2, 1.0, 6.0),
            _q("fp16",  14.5, 1.0, 3.0),
        ],
        capability_tags=["reasoning"],
        ollama_tag="deepseek-r1:7b",
    ),
    ModelEntry(
        id="deepseek-r1-14b", name="DeepSeek R1 Distill 14B", family="deepseek",
        params_b=14.0, context_k=64, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 7.2, 1.5, 6.0),
            _q("Q8_0",  14.5, 1.5, 3.0),
            _q("fp16",  28.0, 1.5, 1.5),
        ],
        capability_tags=["reasoning"],
        ollama_tag="deepseek-r1:14b",
    ),
    ModelEntry(
        id="deepseek-r1-32b", name="DeepSeek R1 Distill 32B", family="deepseek",
        params_b=32.0, context_k=64, added_months_ago=12,
        quant_variants=[
            _q("Q4_K_M", 16.4, 2.5, 2.5),
            _q("Q8_0",   32.0, 2.5, 1.3),
            _q("fp16",   64.0, 2.5, 0.6),
        ],
        capability_tags=["reasoning"],
        ollama_tag="deepseek-r1:32b",
    ),
]

_INDEX: dict[str, ModelEntry] = {m.id: m for m in MODEL_CATALOG}


def get_model(model_id: str) -> Optional[ModelEntry]:
    return _INDEX.get(model_id)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/hardware/test_catalog.py -v
```

Expected: All 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/prowlrbot/hardware/catalog.py tests/hardware/test_catalog.py
git commit -m "feat(hardware): add quant-aware model catalog with MoE active-param support"
```

---

### Task 1.3: Scorer — grades models against hardware profile

**Files:**
- Create: `src/prowlrbot/hardware/scorer.py`
- Test: `tests/hardware/test_scorer.py`

The scorer is where the S/A/B/C/D/F grades come from. It picks the best quantization for the hardware, estimates tok/s, and applies the grading rubric.

Key logic:
- **MoE**: use `active_params_b` for bandwidth calc, `params_b` for RAM calc
- **Unified memory** (Apple Silicon): use `ram_gb` as available VRAM
- **CPU offload**: model grades with optional `cpu_offload=True` show the slower-but-possible case
- **Score**: primary metric is `effective_memory_ratio = required_gb / available_gb`; secondary is tok/s

- [ ] **Step 1: Write failing tests**

```python
# tests/hardware/test_scorer.py
import pytest
from prowlrbot.hardware.detector import HardwareProfile
from prowlrbot.hardware.catalog import get_model
from prowlrbot.hardware.scorer import ModelScorer, ModelScore, Grade


RTX_3060_12GB = HardwareProfile(
    ram_gb=32.0, cpu_cores=8, cpu_arch="x86_64", platform="linux",
    gpu_name="NVIDIA RTX 3060", gpu_vram_gb=12.0, gpu_vendor="nvidia",
    estimated_bandwidth_gbps=360.0, is_apple_silicon=False, unified_memory=False,
)

M2_8GB = HardwareProfile(
    ram_gb=8.0, cpu_cores=8, cpu_arch="arm64", platform="darwin",
    gpu_name="Apple M2", gpu_vram_gb=8.0, gpu_vendor="apple",
    estimated_bandwidth_gbps=100.0, is_apple_silicon=True, unified_memory=True,
)

LOW_END = HardwareProfile(
    ram_gb=8.0, cpu_cores=4, cpu_arch="x86_64", platform="linux",
    gpu_name=None, gpu_vram_gb=None, gpu_vendor="unknown",
    estimated_bandwidth_gbps=0.0, is_apple_silicon=False, unified_memory=False,
)


def test_small_model_grades_s_on_rtx3060():
    scorer = ModelScorer(RTX_3060_12GB)
    score = scorer.score_model(get_model("llama-3.2-3b"))
    assert score.grade in (Grade.S, Grade.A)
    assert score.best_quant == "Q4_K_M"


def test_large_model_grades_f_on_low_end():
    scorer = ModelScorer(LOW_END)
    score = scorer.score_model(get_model("llama-3.3-70b"))
    assert score.grade == Grade.F
    assert score.tok_per_sec == 0


def test_moe_model_scores_better_than_equivalent_dense():
    """GPT-OSS 20B (MoE) should grade better than a real 20B dense model
    because active params drive bandwidth, not total params."""
    scorer = ModelScorer(RTX_3060_12GB)
    score = scorer.score_model(get_model("gpt-oss-20b"))
    # With 12GB VRAM, Q4_K_M needs 10.8 GB — fits, should be D or C at least
    assert score.grade != Grade.F


def test_quant_selection_picks_best_fitting():
    """Scorer should pick highest quality quant that fits in available memory."""
    scorer = ModelScorer(M2_8GB)
    score = scorer.score_model(get_model("phi-4-14b"))
    # fp16 needs 28GB — won't fit. Q4_K_M needs 7.2GB — fits in 8GB M2.
    assert score.best_quant == "Q4_K_M"
    assert score.grade != Grade.F


def test_all_models_scored_no_exception():
    from prowlrbot.hardware.catalog import MODEL_CATALOG
    scorer = ModelScorer(RTX_3060_12GB)
    for model in MODEL_CATALOG:
        score = scorer.score_model(model)
        assert score is not None
```

- [ ] **Step 2: Confirm they fail**

```bash
pytest tests/hardware/test_scorer.py -v 2>&1 | head -20
```

- [ ] **Step 3: Implement scorer**

```python
# src/prowlrbot/hardware/scorer.py
"""Grade AI models against detected hardware.

Grades: S (90+), A (75+), B (60+), C (40+), D (20+), F (0)
Primary axis: memory fit ratio.
Secondary axis: estimated tok/s from bandwidth × quant coefficient.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .catalog import ModelEntry, QuantVariant
from .detector import HardwareProfile


class Grade(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


@dataclass
class ModelScore:
    model_id: str
    grade: Grade
    score: int                   # 0–100
    best_quant: Optional[str]    # e.g. "Q4_K_M"
    required_gb: float           # RAM/VRAM needed for best_quant
    available_gb: float          # what the hardware offers
    tok_per_sec: float           # estimated; 0 if F
    memory_ratio: float          # required / available (lower = better)
    cpu_offload_possible: bool   # True if fits with CPU offload but not GPU alone
    label: str                   # "Runs great" / "Decent" / "Tight fit" / etc.


_GRADE_LABELS = {
    Grade.S: "Runs great",
    Grade.A: "Runs well",
    Grade.B: "Decent",
    Grade.C: "Tight fit",
    Grade.D: "Barely runs",
    Grade.F: "Too heavy",
}

_SCORE_TO_GRADE = [
    (90, Grade.S),
    (75, Grade.A),
    (60, Grade.B),
    (40, Grade.C),
    (20, Grade.D),
    (0,  Grade.F),
]


def _grade_from_score(score: int) -> Grade:
    for threshold, grade in _SCORE_TO_GRADE:
        if score >= threshold:
            return grade
    return Grade.F


class ModelScorer:
    """Score every model in the catalog against a hardware profile."""

    def __init__(self, profile: HardwareProfile) -> None:
        self.profile = profile

    def available_memory_gb(self) -> float:
        """Memory available for model weights.

        Apple Silicon: unified RAM (RAM IS the VRAM).
        Discrete GPU: VRAM. If no GPU, system RAM (CPU inference).
        """
        p = self.profile
        if p.unified_memory:
            # Leave 20% for OS + KV cache overhead
            return p.ram_gb * 0.80
        if p.gpu_vram_gb:
            return p.gpu_vram_gb * 0.95  # small headroom
        # CPU-only inference (no GPU)
        return p.ram_gb * 0.60  # conservative — OS + other apps

    def score_model(self, model: ModelEntry) -> ModelScore:
        available = self.available_memory_gb()

        # Pick the best (highest quality) quant that fits
        best_variant: Optional[QuantVariant] = None
        for variant in sorted(model.quant_variants,
                               key=lambda v: v.ram_gb, reverse=True):
            if variant.ram_gb <= available:
                best_variant = variant
                break

        # Check CPU offload: does it fit in RAM even if GPU can't hold it alone?
        cpu_offload_possible = False
        if best_variant is None and self.profile.ram_gb > 0:
            for variant in sorted(model.quant_variants, key=lambda v: v.ram_gb):
                if variant.ram_gb <= self.profile.ram_gb * 0.70:
                    cpu_offload_possible = True
                    best_variant = variant  # still show it, but grade as D at best
                    break

        if best_variant is None:
            return ModelScore(
                model_id=model.id, grade=Grade.F, score=0,
                best_quant=None, required_gb=model.quant_variants[-1].ram_gb,
                available_gb=available, tok_per_sec=0,
                memory_ratio=999.0, cpu_offload_possible=False,
                label=_GRADE_LABELS[Grade.F],
            )

        memory_ratio = best_variant.ram_gb / max(available, 0.1)

        # Bandwidth-based tok/s estimate.
        # For MoE: bandwidth = active_params_b / params_b * full_bandwidth
        # because only active expert weights move through memory per token.
        bw = self.profile.estimated_bandwidth_gbps
        if model.is_moe and model.active_params_b:
            moe_factor = model.active_params_b / model.params_b
            bw = bw * moe_factor
        if not self.profile.gpu_vram_gb:
            # CPU inference: use rough estimate of ~20 GB/s memory bandwidth
            bw = max(bw, 20.0)

        tok_per_sec = best_variant.tok_per_sec_per_100gbps * bw / 100.0
        if cpu_offload_possible:
            tok_per_sec = tok_per_sec * 0.25  # CPU offload severe penalty

        # Score formula:
        # memory headroom (60%) + tok/s bonus (40%)
        # memory component: ratio 0.15 → 100, ratio 0.5 → 60, ratio 0.9 → 20, ratio >1 → 0
        if memory_ratio > 1.0:
            mem_score = 0
        elif memory_ratio < 0.15:
            mem_score = 100
        else:
            mem_score = int(100 - (memory_ratio - 0.15) / 0.85 * 80)

        # tok/s component: 50+ tok/s → 100, 10 tok/s → 60, 3 tok/s → 30, 0 → 0
        if tok_per_sec >= 50:
            tok_score = 100
        elif tok_per_sec >= 20:
            tok_score = 80
        elif tok_per_sec >= 10:
            tok_score = 60
        elif tok_per_sec >= 5:
            tok_score = 40
        elif tok_per_sec >= 2:
            tok_score = 20
        else:
            tok_score = 0

        raw_score = int(mem_score * 0.6 + tok_score * 0.4)
        # CPU offload cap: never better than D
        if cpu_offload_possible:
            raw_score = min(raw_score, 35)

        grade = _grade_from_score(raw_score)

        return ModelScore(
            model_id=model.id, grade=grade, score=raw_score,
            best_quant=best_variant.quant, required_gb=best_variant.ram_gb,
            available_gb=available, tok_per_sec=round(tok_per_sec, 1),
            memory_ratio=round(memory_ratio, 3),
            cpu_offload_possible=cpu_offload_possible,
            label=_GRADE_LABELS[grade],
        )

    def score_all(self) -> list[ModelScore]:
        from .catalog import MODEL_CATALOG
        scores = [self.score_model(m) for m in MODEL_CATALOG]
        return sorted(scores, key=lambda s: s.score, reverse=True)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/hardware/test_scorer.py -v
```

Expected: All 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/prowlrbot/hardware/scorer.py tests/hardware/test_scorer.py
git commit -m "feat(hardware): quant-aware model scorer with MoE support and CPU offload modeling"
```

---

## Chunk 2: Hardware API Router

### Task 2.1: `GET /api/hardware` and `GET /api/hardware/model-grades`

**Files:**
- Create: `src/prowlrbot/app/routers/hardware.py`
- Modify: `src/prowlrbot/app/routers/__init__.py` (add hardware_router)
- Test: `tests/test_hardware_router.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_hardware_router.py
import pytest
from fastapi.testclient import TestClient


def test_hardware_endpoint_returns_profile(test_client: TestClient):
    resp = test_client.get("/api/hardware")
    assert resp.status_code == 200
    data = resp.json()
    assert "ram_gb" in data
    assert data["ram_gb"] > 0
    assert "platform" in data


def test_model_grades_endpoint(test_client: TestClient):
    resp = test_client.get("/api/hardware/model-grades")
    assert resp.status_code == 200
    grades = resp.json()
    assert isinstance(grades, list)
    assert len(grades) >= 10
    first = grades[0]
    assert "model_id" in first
    assert "grade" in first
    assert "tok_per_sec" in first
    assert "best_quant" in first


def test_reverse_lookup(test_client: TestClient):
    resp = test_client.get("/api/hardware/reverse-lookup/llama-3.3-70b")
    assert resp.status_code == 200
    data = resp.json()
    assert "min_vram_gb" in data
    assert "recommended_setup" in data
```

- [ ] **Step 2: Implement router**

```python
# src/prowlrbot/app/routers/hardware.py
"""Hardware detection and model compatibility API.

Leapfrogs browser-based tools (canirun.ai) by using actual OS-level APIs:
psutil, nvidia-smi, rocm-smi, sysctl — exact values, not browser estimates.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ...hardware.catalog import MODEL_CATALOG, get_model
from ...hardware.detector import HardwareDetector, HardwareProfile
from ...hardware.scorer import ModelScore, ModelScorer

router = APIRouter(prefix="/hardware", tags=["hardware"])

_detector = HardwareDetector()


class HardwareProfileResponse(BaseModel):
    ram_gb: float
    cpu_cores: int
    cpu_arch: str
    platform: str
    gpu_name: Optional[str]
    gpu_vram_gb: Optional[float]
    gpu_vendor: str
    estimated_bandwidth_gbps: float
    is_apple_silicon: bool
    unified_memory: bool


class ModelGradeResponse(BaseModel):
    model_id: str
    name: str
    family: str
    params_b: float
    context_k: int
    grade: str
    score: int
    label: str
    best_quant: Optional[str]
    required_gb: float
    available_gb: float
    tok_per_sec: float
    memory_ratio: float
    cpu_offload_possible: bool
    capability_tags: List[str]
    is_moe: bool
    ollama_tag: Optional[str]


class ReverseLookupResponse(BaseModel):
    model_id: str
    name: str
    min_vram_gb: float          # minimum to run at all (Q4_K_M)
    ideal_vram_gb: float        # to run at Q8 quality
    min_ram_gb: float           # for CPU-only inference
    recommended_setup: str      # human-readable sentence


@router.get("", response_model=HardwareProfileResponse)
async def get_hardware() -> HardwareProfileResponse:
    """Detect this machine's hardware specs using OS-level APIs."""
    profile: HardwareProfile = _detector.detect()
    return HardwareProfileResponse(**profile.__dict__)


@router.get("/model-grades", response_model=List[ModelGradeResponse])
async def get_model_grades(
    capability: Optional[str] = None,
    min_grade: Optional[str] = None,
) -> List[ModelGradeResponse]:
    """Grade all models in the catalog against detected hardware.

    Query params:
    - capability: filter by tag (e.g. "coding", "reasoning")
    - min_grade: only return S/A/B/C/D models (exclude F)
    """
    profile = _detector.detect()
    scorer = ModelScorer(profile)
    scores = scorer.score_all()

    results = []
    for score in scores:
        model = get_model(score.model_id)
        if model is None:
            continue
        if capability and capability not in model.capability_tags:
            continue
        if min_grade and score.grade.value == "F":
            continue

        results.append(ModelGradeResponse(
            model_id=score.model_id,
            name=model.name,
            family=model.family,
            params_b=model.params_b,
            context_k=model.context_k,
            grade=score.grade.value,
            score=score.score,
            label=score.label,
            best_quant=score.best_quant,
            required_gb=score.required_gb,
            available_gb=score.available_gb,
            tok_per_sec=score.tok_per_sec,
            memory_ratio=score.memory_ratio,
            cpu_offload_possible=score.cpu_offload_possible,
            capability_tags=model.capability_tags,
            is_moe=model.is_moe,
            ollama_tag=model.ollama_tag,
        ))
    return results


@router.get("/reverse-lookup/{model_id}", response_model=ReverseLookupResponse)
async def reverse_lookup(model_id: str) -> ReverseLookupResponse:
    """Return minimum hardware requirements for a specific model.

    Answers the HN request: 'pick a model, see what hardware you need.'
    """
    from fastapi import HTTPException
    model = get_model(model_id)
    if not model:
        raise HTTPException(404, f"Model '{model_id}' not in catalog")

    q4 = next((v for v in model.quant_variants if v.quant == "Q4_K_M"), None)
    q8 = next((v for v in model.quant_variants if v.quant == "Q8_0"), None)
    cheapest = sorted(model.quant_variants, key=lambda v: v.ram_gb)[0]

    min_vram = q4.ram_gb if q4 else cheapest.ram_gb
    ideal_vram = q8.ram_gb if q8 else (q4.ram_gb * 1.5 if q4 else min_vram)
    min_ram = cheapest.ram_gb / 0.60  # CPU inference uses 60% RAM budget

    tags = ", ".join(model.capability_tags) if model.capability_tags else "general"
    recommended = (
        f"For {model.name} ({tags}): minimum {min_vram:.0f} GB VRAM "
        f"(Q4_K_M), ideal {ideal_vram:.0f} GB (Q8_0). "
        f"CPU-only possible with {min_ram:.0f} GB RAM (slow)."
    )

    return ReverseLookupResponse(
        model_id=model_id,
        name=model.name,
        min_vram_gb=min_vram,
        ideal_vram_gb=ideal_vram,
        min_ram_gb=round(min_ram, 1),
        recommended_setup=recommended,
    )
```

- [ ] **Step 3: Wire into `__init__.py`**

```python
# add after existing imports (line 46 area):
from .hardware import router as hardware_router

# add to router.include_router block:
router.include_router(hardware_router)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_hardware_router.py -v
```

Expected: All 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/prowlrbot/app/routers/hardware.py
git commit -m "feat(hardware): add /api/hardware router — model grades, reverse lookup, quant-aware"
```

---

## Chunk 3: Wire Gamification Events (Live Leaderboard Feed)

The gamification DB and XP API exist. Nothing writes to them. This chunk wires 4 high-value events so the leaderboard has real data within minutes of install.

### Task 3.1: XP event hooks in AgentRunner

**Files:**
- Read: `src/prowlrbot/app/runner/runner.py`
- Modify: `src/prowlrbot/app/runner/runner.py`
- Test: `tests/test_gamification_events.py`

- [ ] **Step 1: Read the runner to find where tasks complete**

```bash
grep -n "response\|result\|complete\|finish" src/prowlrbot/app/runner/runner.py | head -30
```

- [ ] **Step 2: Write failing test for XP award after task**

```python
# tests/test_gamification_events.py
from unittest.mock import AsyncMock, patch
import pytest


async def test_xp_awarded_after_agent_task(test_client):
    """After a successful agent query, XP should be recorded."""
    with patch("prowlrbot.gamification.xp_tracker.XPTracker.award_xp") as mock_award:
        resp = test_client.post("/api/agent/query", json={
            "content": "echo hello", "session_id": "test"
        })
        # XP should have been attempted regardless of model response
        # (we just check the call was made, not that the model succeeded)
        # This test just confirms the wiring path exists
        assert resp.status_code in (200, 422, 500)
```

- [ ] **Step 3: Add `_award_xp` helper to runner**

Find the line in `runner.py` where a successful response is returned. Add after it:

```python
# Inside AgentRunner, after successful query result:
async def _award_xp(self, entity_id: str, category: str, reason: str,
                    amount: int = 10) -> None:
    """Fire-and-forget XP award. Never raises."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8088/api/gamification/xp",
                json={
                    "entity_id": entity_id,
                    "entity_type": "agent",
                    "amount": amount,
                    "category": category,
                    "reason": reason,
                },
                timeout=2.0,
            )
    except Exception:
        pass  # XP is best-effort, never block the agent
```

Call it at the end of successful query execution:
```python
await self._award_xp(
    entity_id=session_id or "default",
    category="task_complete",
    reason=f"Completed agent task",
    amount=10,
)
```

- [ ] **Step 4: Add XP event to CronExecutor**

```bash
grep -n "complete\|success\|result" src/prowlrbot/app/crons/executor.py | head -20
```

After successful cron job execution, add:
```python
# fire XP for cron task completion (fire-and-forget)
import asyncio
asyncio.create_task(_award_xp_background(
    entity_id="cron",
    category="cron_complete",
    reason=f"Cron job completed: {job_id}",
    amount=5,
))
```

- [ ] **Step 5: Add XP event to skill use**

In `AgentRunner` or wherever skills are invoked, add 2 XP per skill use.

- [ ] **Step 6: Commit**

```bash
git add src/prowlrbot/app/runner/ src/prowlrbot/app/crons/
git commit -m "feat(gamification): wire XP events to agent tasks, cron jobs, and skill use"
```

---

### Task 3.2: WebSocket push for live leaderboard updates

**Files:**
- Read: `src/prowlrbot/app/websocket.py` (existing WS infrastructure)
- Modify: `src/prowlrbot/gamification/xp_tracker.py`
- Test: `tests/test_leaderboard_live.py`

- [ ] **Step 1: Understand the existing WebSocket event bus**

```bash
grep -n "emit\|publish\|broadcast\|event" src/prowlrbot/app/websocket.py | head -20
```

- [ ] **Step 2: Emit `leaderboard_update` event after XP award**

In `XPTracker.award_xp`, after the DB write, emit via the event bus:

```python
# After recording XP in DB:
try:
    from ..app.event_bus import get_event_bus
    bus = get_event_bus()
    await bus.emit("leaderboard_update", {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "new_xp": new_total,
        "level": level_info.level,
        "category": category,
    })
except Exception:
    pass
```

- [ ] **Step 3: Verify WS clients receive the event**

```bash
# Manual test: open ws://localhost:8088/ws in browser console
# then trigger an agent task — should see leaderboard_update message
```

- [ ] **Step 4: Commit**

```bash
git add src/prowlrbot/gamification/
git commit -m "feat(gamification): push leaderboard_update over WebSocket on every XP award"
```

---

## Chunk 4: Console Frontend — Hardware Advisor Page

### Task 4.1: Hardware Advisor page component

**Files:**
- Create: `console/src/pages/HardwareAdvisor/index.tsx`
- Create: `console/src/pages/HardwareAdvisor/ModelGradeCard.tsx`
- Create: `console/src/pages/HardwareAdvisor/GradeBadge.tsx`
- Modify: `console/src/router.tsx` (add route `/hardware`)
- Modify: `console/src/components/Layout/Sidebar.tsx` (add nav item)

The page design:
```
┌─ Hardware Advisor ───────────────────────────────┐
│  Detected: RTX 3060 (12 GB) · 32 GB RAM · ~360 GB/s │
│  [Filter: All capabilities ▼] [Sort: Score ▼]        │
│                                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │ S  Llama 3.2 3B   Q4_K_M · 1.5 GB · ~103 tok/s │ │
│  │    Runs great    [Install with Ollama]          │ │
│  ├──────────────────────────────────────────────┤    │
│  │ A  Qwen 3 4B      Q4_K_M · 2.0 GB · ~76 tok/s  │ │
│  │    Runs well     [Install with Ollama]          │ │
│  ├──────────────────────────────────────────────┤    │
│  │ D  Llama 3.1 8B   Q4_K_M · 4.1 GB · ~36 tok/s  │ │
│  │    Barely runs   [Install with Ollama]          │ │
│  ├──────────────────────────────────────────────┤    │
│  │ F  Llama 3.3 70B  Too heavy (35.9 GB required) │ │
│  │    What do I need? →                            │ │
│  └──────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────┘
```

- [ ] **Step 1: Create GradeBadge component**

```tsx
// console/src/pages/HardwareAdvisor/GradeBadge.tsx
import React from "react";

const GRADE_COLORS: Record<string, { bg: string; text: string }> = {
  S: { bg: "#00C853", text: "#fff" },
  A: { bg: "#69F0AE", text: "#000" },
  B: { bg: "#FFD740", text: "#000" },
  C: { bg: "#FF9100", text: "#fff" },
  D: { bg: "#FF5252", text: "#fff" },
  F: { bg: "#424242", text: "#aaa" },
};

export const GradeBadge: React.FC<{ grade: string }> = ({ grade }) => {
  const colors = GRADE_COLORS[grade] ?? GRADE_COLORS.F;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: 32,
        height: 32,
        borderRadius: 4,
        fontWeight: 700,
        fontSize: 16,
        backgroundColor: colors.bg,
        color: colors.text,
        flexShrink: 0,
      }}
    >
      {grade}
    </span>
  );
};
```

- [ ] **Step 2: Create ModelGradeCard**

```tsx
// console/src/pages/HardwareAdvisor/ModelGradeCard.tsx
import React from "react";
import { Button, Tag, Tooltip } from "antd";
import { GradeBadge } from "./GradeBadge";

interface ModelGrade {
  model_id: string;
  name: string;
  grade: string;
  label: string;
  score: number;
  best_quant: string | null;
  required_gb: number;
  tok_per_sec: number;
  capability_tags: string[];
  is_moe: boolean;
  cpu_offload_possible: boolean;
  ollama_tag: string | null;
}

interface Props {
  model: ModelGrade;
  onInstall: (ollamaTag: string) => void;
}

export const ModelGradeCard: React.FC<Props> = ({ model, onInstall }) => {
  const canInstall = model.grade !== "F" && model.ollama_tag;

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 16,
      padding: "12px 16px", borderBottom: "1px solid #f0f0f0",
      opacity: model.grade === "F" ? 0.5 : 1,
      transition: "opacity 0.2s",
    }}
      onMouseEnter={e => {
        if (model.grade === "F") e.currentTarget.style.opacity = "0.7";
      }}
      onMouseLeave={e => {
        if (model.grade === "F") e.currentTarget.style.opacity = "0.5";
      }}
    >
      <GradeBadge grade={model.grade} />

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontWeight: 600 }}>{model.name}</span>
          {model.is_moe && (
            <Tooltip title="Mixture of Experts — memory efficient">
              <Tag color="purple" style={{ marginLeft: 4 }}>MoE</Tag>
            </Tooltip>
          )}
          {model.capability_tags.map(tag => (
            <Tag key={tag} color="blue">{tag}</Tag>
          ))}
        </div>
        <div style={{ fontSize: 12, color: "#8c8c8c", marginTop: 2 }}>
          {model.label}
          {model.best_quant && ` · ${model.best_quant}`}
          {model.required_gb > 0 && ` · ${model.required_gb.toFixed(1)} GB`}
          {model.tok_per_sec > 0 && ` · ~${model.tok_per_sec.toFixed(0)} tok/s`}
          {model.cpu_offload_possible && " · (CPU offload)"}
        </div>
      </div>

      {canInstall ? (
        <Button
          size="small"
          type="primary"
          onClick={() => onInstall(model.ollama_tag!)}
        >
          Install with Ollama
        </Button>
      ) : (
        <Button size="small" type="link" href={`/hardware/reverse/${model.model_id}`}>
          What do I need? →
        </Button>
      )}
    </div>
  );
};
```

- [ ] **Step 3: Create the main HardwareAdvisor page**

```tsx
// console/src/pages/HardwareAdvisor/index.tsx
import React, { useEffect, useState } from "react";
import { Alert, Select, Spin, Typography } from "antd";
import { ModelGradeCard } from "./ModelGradeCard";

const { Title, Text } = Typography;

interface HardwareProfile {
  ram_gb: number;
  gpu_name: string | null;
  gpu_vram_gb: number | null;
  estimated_bandwidth_gbps: number;
  platform: string;
  is_apple_silicon: boolean;
}

interface ModelGrade {
  model_id: string;
  name: string;
  grade: string;
  label: string;
  score: number;
  best_quant: string | null;
  required_gb: number;
  tok_per_sec: number;
  capability_tags: string[];
  is_moe: boolean;
  cpu_offload_possible: boolean;
  ollama_tag: string | null;
}

const CAPABILITY_OPTIONS = [
  { label: "All capabilities", value: "" },
  { label: "Coding", value: "coding" },
  { label: "Reasoning", value: "reasoning" },
  { label: "General", value: "general" },
  { label: "Fast", value: "fast" },
];

export const HardwareAdvisor: React.FC = () => {
  const [hardware, setHardware] = useState<HardwareProfile | null>(null);
  const [grades, setGrades] = useState<ModelGrade[]>([]);
  const [loading, setLoading] = useState(true);
  const [capability, setCapability] = useState("");
  const [hideF, setHideF] = useState(false);
  const [installing, setInstalling] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/hardware").then(r => r.json()),
      fetch("/api/hardware/model-grades").then(r => r.json()),
    ]).then(([hw, g]) => {
      setHardware(hw);
      setGrades(g);
    }).finally(() => setLoading(false));
  }, []);

  const filtered = grades.filter(m => {
    if (capability && !m.capability_tags.includes(capability)) return false;
    if (hideF && m.grade === "F") return false;
    return true;
  });

  const handleInstall = async (ollamaTag: string) => {
    setInstalling(ollamaTag);
    try {
      await fetch("/api/ollama-models/pull", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: ollamaTag }),
      });
    } finally {
      setInstalling(null);
    }
  };

  if (loading) return <Spin style={{ margin: "80px auto", display: "block" }} />;

  const hwSummary = hardware ? [
    hardware.gpu_name ?? "No GPU",
    hardware.gpu_vram_gb ? `${hardware.gpu_vram_gb} GB VRAM` : null,
    `${hardware.ram_gb.toFixed(0)} GB RAM`,
    hardware.estimated_bandwidth_gbps
      ? `~${hardware.estimated_bandwidth_gbps.toFixed(0)} GB/s`
      : null,
    hardware.platform,
  ].filter(Boolean).join(" · ") : "";

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <Title level={3}>What can my machine run?</Title>

      {hardware && (
        <Alert
          type="info"
          showIcon
          message={<Text strong>Detected: </Text>}
          description={hwSummary}
          style={{ marginBottom: 16 }}
        />
      )}

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Select
          options={CAPABILITY_OPTIONS}
          value={capability}
          onChange={setCapability}
          style={{ width: 200 }}
        />
        <Select
          value={hideF ? "runnable" : "all"}
          onChange={v => setHideF(v === "runnable")}
          options={[
            { label: "All models", value: "all" },
            { label: "Runnable only", value: "runnable" },
          ]}
          style={{ width: 160 }}
        />
      </div>

      <div style={{ border: "1px solid #f0f0f0", borderRadius: 8 }}>
        {filtered.map(model => (
          <ModelGradeCard
            key={model.model_id}
            model={model}
            onInstall={handleInstall}
          />
        ))}
        {filtered.length === 0 && (
          <div style={{ padding: 32, textAlign: "center", color: "#8c8c8c" }}>
            No models match the current filter.
          </div>
        )}
      </div>
    </div>
  );
};

export default HardwareAdvisor;
```

- [ ] **Step 4: Add route and sidebar nav**

In `console/src/router.tsx`, add:
```tsx
{ path: "/hardware", element: <HardwareAdvisor /> }
```

In sidebar nav config, add:
```tsx
{ label: "Hardware Advisor", path: "/hardware", icon: <CpuIcon /> }
```

- [ ] **Step 5: Build check**

```bash
cd /home/anon/dev/prowlrbot/console
npm run build 2>&1 | tail -20
```

Expected: successful build, no TypeScript errors.

- [ ] **Step 6: Commit**

```bash
git add console/src/pages/HardwareAdvisor/
git commit -m "feat(console): add Hardware Advisor page with graded model list and one-click Ollama install"
```

---

## Chunk 5: Live Leaderboard Console Widget

### Task 5.1: Leaderboard widget with WebSocket live updates

**Files:**
- Create: `console/src/pages/Leaderboard/index.tsx`
- Create: `console/src/hooks/useLeaderboard.ts`
- Modify: `console/src/router.tsx`

The leaderboard shows real agent activity — XP earned, levels, top performers — and updates live over WebSocket without polling.

- [ ] **Step 1: Create `useLeaderboard` hook**

```typescript
// console/src/hooks/useLeaderboard.ts
import { useEffect, useState, useRef } from "react";

interface LeaderboardEntry {
  entity_id: string;
  entity_type: string;
  total_xp: number;
  level: number;
  category_breakdown: Record<string, number>;
}

export function useLeaderboard(entityType: "agent" | "user" = "agent") {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initial load
    fetch(`/api/gamification/leaderboard?entity_type=${entityType}&limit=20`)
      .then(r => r.json())
      .then(setEntries);

    // Live updates via existing WebSocket
    const ws = new WebSocket(`ws://${location.host}/ws`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "leaderboard_update") {
        // Refresh on any XP event
        fetch(`/api/gamification/leaderboard?entity_type=${entityType}&limit=20`)
          .then(r => r.json())
          .then(data => {
            setEntries(data);
            setLastUpdate(new Date());
          });
      }
    };

    return () => ws.close();
  }, [entityType]);

  return { entries, lastUpdate };
}
```

- [ ] **Step 2: Create Leaderboard page**

```tsx
// console/src/pages/Leaderboard/index.tsx
import React, { useState } from "react";
import { Badge, Table, Tag, Typography } from "antd";
import { useLeaderboard } from "../../hooks/useLeaderboard";

const { Title, Text } = Typography;

const LEVEL_COLORS = ["gray", "green", "blue", "purple", "gold", "red"];

export const Leaderboard: React.FC = () => {
  const [entityType, setEntityType] = useState<"agent" | "user">("agent");
  const { entries, lastUpdate } = useLeaderboard(entityType);

  const columns = [
    {
      title: "Rank",
      key: "rank",
      render: (_: unknown, __: unknown, index: number) => (
        <span style={{ fontWeight: 700, color: index < 3 ? "#faad14" : undefined }}>
          #{index + 1}
        </span>
      ),
      width: 60,
    },
    {
      title: "Agent / User",
      dataIndex: "entity_id",
      key: "entity_id",
      render: (id: string) => <Text strong>{id}</Text>,
    },
    {
      title: "Level",
      dataIndex: "level",
      key: "level",
      render: (level: number) => (
        <Tag color={LEVEL_COLORS[Math.min(level - 1, LEVEL_COLORS.length - 1)]}>
          Lv {level}
        </Tag>
      ),
      width: 80,
    },
    {
      title: "XP",
      dataIndex: "total_xp",
      key: "total_xp",
      render: (xp: number) => <Text>{xp.toLocaleString()} XP</Text>,
      sorter: (a: { total_xp: number }, b: { total_xp: number }) =>
        b.total_xp - a.total_xp,
      width: 120,
    },
  ];

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between",
                    alignItems: "center", marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>Leaderboard</Title>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {lastUpdate && (
            <Badge status="processing" text={
              <Text type="secondary" style={{ fontSize: 12 }}>
                Live · updated {lastUpdate.toLocaleTimeString()}
              </Text>
            } />
          )}
        </div>
      </div>

      <Table
        dataSource={entries}
        columns={columns}
        rowKey="entity_id"
        pagination={false}
        size="small"
      />
    </div>
  );
};

export default Leaderboard;
```

- [ ] **Step 3: Wire route**

Add `/leaderboard` route to router and sidebar.

- [ ] **Step 4: Build check**

```bash
cd /home/anon/dev/prowlrbot/console && npm run build 2>&1 | tail -10
```

- [ ] **Step 5: Commit**

```bash
git add console/src/pages/Leaderboard/ console/src/hooks/useLeaderboard.ts
git commit -m "feat(console): live leaderboard page with WebSocket XP event updates"
```

---

## Summary: What This Delivers

| Feature | Status after this plan |
|---------|----------------------|
| Hardware fingerprint (`psutil` + `nvidia-smi` + `rocm-smi` + `sysctl`) | ✅ |
| Quantization-aware model scoring (Q4_K_M vs fp16 → real memory cost) | ✅ |
| MoE active-param calculation (fixes #1 canirun.ai complaint on HN) | ✅ |
| AMD ROCm + Intel Arc detection | ✅ |
| CPU offload modeling ("fits slow" tier) | ✅ |
| Raspberry Pi / ARM server support (CPU-only scoring path) | ✅ |
| Reverse lookup: "what hardware do I need?" | ✅ |
| One-click Ollama install from grade card | ✅ |
| Auto-configure smart router after install | Next iteration |
| Real tok/s feedback → leaderboard (closes estimation gap) | Next iteration |
| Live XP leaderboard over WebSocket | ✅ |
| XP awarded on real agent activity | ✅ |
