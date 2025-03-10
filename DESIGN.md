# Design
## Do Want
 * data flow mapped out clearly
 * simplified mathematical operations (LATEX?)
   - divisions (magic constants)
   - exponents
   - modulo (magic constants)
   - multiplication (lea)
 * decompiler compatability
   - ghidra
   - radare2
 * helpful variable names
   - hidden metadata (source register-swizzle)
 * pattern recognition
   - `X * rcp(Y)` -> `X / Y`
 * refactoring tools
   - reorder lines
   - maintain determinism
   - equivalent equations (x * 0.5 <-> x / 2)

## Do Not Want
 * recompiling w/ edits
   - readability > optimisation
   - understanding > machine translation


## General HLSL notes

> TODO: copy notes from `~/drives/ssd1/Mod/_tools/HLSL`
> -- cite your sources!


## Scope
track each time a register-swizzle appears


## Operations Reducer
 * BOMDAS / BODMAS / PEMDAS / GEMS / whatever combiner and reduced
 * slide blocks of equation around to find a nice representation
 * automated reducer w/ list of stragies (e.g. minimal brackets)
 * standardised order for common variables
   - identified by usage / index (Normal, Position, Light, Ambient, Albedo etc.)

## Multi-line Representaion
```c++
out = base
    + r1.xxx * r2.xyz
    + r1.yyy * r2.xyz
    + r1.zzz * r2.xyz;
```

align repeating similar operations to make the variations clearer
```
r1.x = dot(r2.xxx, r3.xyz) * int2(-1,  1)
r1.y = dot(r2.yyy, r3.xyz) * int2( 1, -1)
r1.z = dot(r2.zzz, r3.xyz) * int2( 0,  1)
```

group and sort swizzle


## Limiting Scope
Shaders are frequently a single long function
We need to localise the scope of variables to small blocks
Enough that all the info a reader needs is in the one view (30 lines max)
(what's the linux style guide limit on functions again? something like that)

sometimes part of a calcuation is kept as an optimisation
for readability it's more helpful to duplicate the work
expecially if you can represent a variable as LATEX


### Register Life Cycle
 * Declaration (of variable)
 * 1st Assignment
 * Nth Assignment
 * Post-Assignment Reads

reading between assignments is essentially re-birth
we should be reducing the assignment to a single block
branches can complicate things w/ re-assignments

if a register has reached it's final assignment, we can try to inline it

the overall lifespan of a variable can tell us a lot too
e.g. early assignment & multiple reads => common static variable (like `dot(N, L)`)

re-assignment marks an end of scope (on the last read before that assignment)
... i forgor ...

### Identifying Variables
 * Clear relationship to source data
 * Low-ish cognitive complexity
   - `1 - dot(N, L)`
 * Dense block assembling a single register
 * That register is only reads from then on


## Paralellism
Some lines will only work in series
Others could be paralellised
e.g. assembling 2 full 4-swizzle registers at once

We could try representing these in paralell
Then allow the user to identify, simplify & name from this grouped context


## Pattern Recognition
inversion:
`r1 = -r1 + 1` -> `r1 = 1 - r1`

`dot(self, self)` is magnitude squared
cancel out the exponents in `sqrt(x^2)`
`r1.w = dot(r0.xyz, r0.xyz); r1.w = rsqrt(r1.w)` -> `r1.w = 1 / length(r0.xyz);`

> NOTE: `rsqrt` is **reciprocal** square root (`1 / sqrt(x)`)

```c++
r1.w = dot(r0.xyz, r0.xyz);
r1.w = rsqrt(r1.w);
r0.xyz = r0.xyz * r1.www;
/* -> */
r0.normalise();
```
