# **B**ikkie's **I**nteractive **Sh**ader Tool

`BISh` is reverse engineering tool for Titanfall 2's Shaders
Designed to be used in a REPL, like [`bsp_tool`](https://github.com/snake-biscuits/bsp_tool)


## Shader Spec

Titanfall 2's shaders are a pain to replicate.
It's **very** picky about which version of `fxc.exe` you use.

**Don't expect this tool to support anything outside this spec.**

> TODO: link to `fxc.exe` found by 4volts in Northstar Discord

| | |
| :--- | :--- |
| Compiler | `Microsoft (R) HLSL Shader Compiler 10.0.10011.16384` |
| DirectX | `11` |
| File Extension | `*.fxc` |
| Intermediate Language | `DXBC` |
| Program Chunk | `SHEX` |
| Shader Model | `5` |


## Usage

Extract `shdr` resource(s) w/ [rsx](https://github.com/r-ex/rsx)

```python
>>> import bish
>>> fxc = bish.DXBC.from_file("rsx/exported_files/shader/filename.fxc")
>>> assert "SHEX" in fxc.chunks
>>> len(fxc.SHEX.instructions)
# a surprisingly small number
```
