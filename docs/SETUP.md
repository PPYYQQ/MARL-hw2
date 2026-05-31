# Setup Notes

These notes record the environment setup used for the assignment experiments.

## Conda Environment

Created a dedicated Python 3.9 environment:

```bash
conda create -n marl_hw2 python=3.9 -y
```

The default `pip` resolved by conda was too new for Python 3.9 in this environment and failed with:

```text
TypeError: dataclass() got an unexpected keyword argument 'slots'
```

Fixed by installing a Python 3.9-compatible pip build:

```bash
conda install -n marl_hw2 pip=24.2 -y
```

Installed AFlow dependencies:

```bash
conda run -n marl_hw2 python -m pip install -r AFlow/requirements.txt
```

The upstream data downloader imports `requests`, which was missing from the imported requirements snapshot. Added `requests==2.32.3` to `AFlow/requirements.txt` and installed it with the same command above.

The local shell uses a SOCKS proxy. `httpx` requires `socksio` for that proxy mode, so `socksio==1.0.0` was also added to `AFlow/requirements.txt`.

MATH scoring uses SymPy's LaTeX parser. A smoke test produced the correct answer but scored zero because `antlr4` was missing, so `antlr4-python3-runtime==4.11.0` was added.

Report compilation uses Tectonic in the same conda environment:

```bash
conda install -n marl_hw2 -c conda-forge tectonic -y
```

## Kimi Configuration

Created the local config from the safe example:

```bash
cp AFlow/config/config2.kimi.example.yaml AFlow/config/config2.yaml
```

The local config is ignored by Git. It reads the API key from:

```bash
KIMI_API_KEY
```

Validation command:

```bash
conda run -n marl_hw2 python -c "import os, sys, pathlib; repo=pathlib.Path.cwd(); sys.path.insert(0, str(repo/'AFlow')); os.chdir(repo/'AFlow'); from scripts.async_llm import LLMsConfig; cfg=LLMsConfig.default().get('kimi-k2.5'); print(cfg.model, cfg.base_url, bool(cfg.key))"
```

Observed result:

```text
kimi-k2.5 https://api.moonshot.cn/v1 True
```

The first API smoke tests showed that this Kimi endpoint requires `top_p: 0.95` and, when thinking is disabled, `temperature: 0.6` for `kimi-k2.5`. A one-sample request with default thinking stayed open for more than two minutes, so the default `kimi-k2.5` alias disables thinking through `extra_body` and sets an explicit request timeout. A separate `kimi-k2.5-thinking` alias is kept for experiments that intentionally use model-side thinking.

## Local Validation

The current no-API validation entry points are maintained in the root `Makefile`:

```bash
make final-check
make handoff-check
```

For a narrower syntax-only check, use:

```bash
make py-compile
```

Expected result:

```text
The commands should pass locally without making API calls. `make final-check` may warn about missing final student metadata and the quota-blocked full MATH `manual_v1` test table until those external inputs are resolved.
```
