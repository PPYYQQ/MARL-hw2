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

## Local Validation

Static checks:

```bash
conda run -n marl_hw2 python -m py_compile experiments/run_baselines.py experiments/run_workflows.py experiments/collect_results.py AFlow/scripts/async_llm.py AFlow/workspace/MATH/workflows/manual_v1/graph.py AFlow/workspace/HumanEval/workflows/manual_v1/graph.py
```

Workflow import check:

```bash
conda run -n marl_hw2 python -c "import os, sys, pathlib; repo=pathlib.Path.cwd(); sys.path.insert(0, str(repo/'AFlow')); os.chdir(repo/'AFlow'); import workspace.MATH.workflows.manual_v1.graph as math_graph; import workspace.HumanEval.workflows.manual_v1.graph as code_graph; print(math_graph.Workflow.__name__, code_graph.Workflow.__name__)"
```

Observed result:

```text
Workflow Workflow
```
