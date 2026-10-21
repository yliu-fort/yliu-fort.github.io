---
title: "Example post: equations, figures and code"
description: "A reference draft that exercises every writing feature of this site, using the second-order Stokes wave as the example."
tags: [example, waves]
toc: true
---

This draft is never published; it exists so that the writing features can be checked in the
local preview (`scripts/serve.sh`). The physics is the textbook second-order Stokes wave in deep
water.

## Setting

Consider a periodic wave train with wavenumber $k$, frequency $\omega$ and amplitude $a$, so that
the steepness is $ka$ and the phase is $\theta = kx - \omega t$. In deep water the linear
dispersion relation is $\omega^2 = g k$, the deep-water limit of $\omega^2 = g k \tanh(kh)$.
A set written with braces needs the double-dollar form inline, as in $$\{\theta : \cos\theta > 0\}$$.

## The second-order profile

Expanding in powers of the steepness, the free surface to second order is

$$
\begin{equation}
\eta(x, t) = a\cos\theta + \tfrac12 k a^2 \cos 2\theta . \label{eq:stokes}
\end{equation}
$$

The correction in \eqref{eq:stokes} raises the crests and lifts the troughs by the same amount:

$$
\begin{aligned}
\eta_{\text{crest}} &= a + \tfrac12 k a^2, \\
\eta_{\text{trough}} &= -a + \tfrac12 k a^2 .
\end{aligned}
$$

Crests therefore become sharper and troughs flatter as $ka$ grows, which is the first visible
sign of nonlinearity.[^speed]

{% include figure.html
   src="/assets/posts/example-post/stokes-profile.svg"
   alt="Linear and second-order Stokes wave profiles over two wavelengths"
   caption="Linear (dashed) and second-order (solid) surface profiles from equation (1) for $ka = 0.25$. The second-order crests are higher and narrower."
   width="100%" %}

| Steepness $ka$ | Linear crest $/a$ | Second-order crest $/a$ |
| --- | --- | --- |
| 0.1 | 1.00 | 1.05 |
| 0.2 | 1.00 | 1.10 |
| 0.3 | 1.00 | 1.15 |

## Computing it

```python
import numpy as np

def stokes2(theta, a, k):
    """Second-order Stokes free surface, equation (1)."""
    return a * np.cos(theta) + 0.5 * k * a**2 * np.cos(2 * theta)

theta = np.linspace(-np.pi, 3 * np.pi, 401)
eta = stokes2(theta, a=0.25, k=1.0)
```

> Blockquotes are useful for definitions or quoted text.

## Syntax notes

- Inline math: `$ka$`; with braces or norms: `$$\{x\}$$`, `$$\|u\|$$`.
- Display math: `$$` on its own lines, with a blank line before and after.
- A literal dollar sign in running text is written `\\$`.

## References

- Stokes, G. G. (1847). On the theory of oscillatory waves. *Transactions of the Cambridge
  Philosophical Society*, 8, 441–455.

[^speed]: The amplitude dependence of the phase speed, $c = \sqrt{g/k}\,\bigl(1 + \tfrac12 (ka)^2\bigr)$, only appears at third order.
