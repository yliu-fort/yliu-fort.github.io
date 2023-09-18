---
title: "Post: Latex"
excerpt_separator: "<!--more-->"
categories:
  - Blog
tags:
  - Post Formats
  - readability
  - latex
mathjax: true
---

When $$ a \ne 0 $$, there are two solutions to $$ ax^2 + bx + c = 0 $$ and they are

$$ x = {-b \pm \sqrt{b^2-4ac} \over 2a}. $$

<!--more-->
```yaml
excerpt_separator: "<!--more-->"
```

At first, we sample $$f(x)$$ in the $$N$$ ($$N$$ is odd) equidistant points around $$x^*$$:

$$
   f_k = f(x_k),\: x_k = x^*+kh,\: k=-\frac{N-1}{2},\dots,\frac{N-1}{2}
$$

where $$h$$ is some step.

Then we interpolate points $$\{(x_k,f_k)\}$$ by polynomial

\begin{equation} \label{eq:poly}
   P_{N-1}(x)=\sum_{j=0}^{N-1}{a_jx^j}.
\end{equation}

Its coefficients $$\{a_j\}$$ are found as a solution of system of linear equations:

\begin{equation} \label{eq:sys}
   \{ P_{N-1}(x_k) = f_k \},\quad k=-\frac{N-1}{2},\dots,\frac{N-1}{2}.
\end{equation}

Here are references to existing equations: \eqref{eq:poly}, \eqref{eq:sys}.

Here is reference to non-existing equation \eqref{eq:unknown}.


