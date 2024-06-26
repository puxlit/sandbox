# [crypto] cherry

<table><tbody>
<tr><th>Value</th><td>957 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>Meow Mix</td></tr>
<tr><th>Connection info</th><td><a href="https://cherry.jellyc.tf/">https://cherry.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/cherry_dist.zip">cherry_dist.zip</a></td></tr>
</tbody></table>

A Starknight hacked an old slot machine and turned it into something strange?!
I heard that you win a secret message if you manage to get triple cherries, but...

---

raw notes:

  - reading the provided source code…
      - "change" button cycles between three starting configurations of reels (i.e. three ciphertexts)
      - "play 0/1/2 coin" + "spin" increment separate counters (which I'll call a/b/c) + advance the reels by differing amounts
      - there are 32,768 values on the reels, and the cherry is at position 0
      - when the reels read cherry, a/b/c should decode to some plaintext
  - basically, we're solving a system of linear congruences (in three variables)
    ```
    # first ciphertext
    10992 + a*19 + b*32 + c*347 ≡ 0 (mod 32768)
    30978 + a*22 + b*27 + c*349 ≡ 0 (mod 32768)
    12520 + a*19 + b*29 + c*353 ≡ 0 (mod 32768)
    --
    - guess a =  4194 (because we expect awascii32 to be "jel")
    - guess b = 29860 (because we expect awascii32 to be "lyC")
    - guess c = 25598 (because we expect awascii32 to be "TF{")
    - solution works!
    
    # second ciphertext
    30983 + a*19 + b*32 + c*347 ≡ 0 (mod 32768)
     7390 + a*22 + b*27 + c*349 ≡ 0 (mod 32768)
      481 + a*19 + b*29 + c*353 ≡ 0 (mod 32768)
    --
    - deferring to Wolfram Alpha: "solve the diophantine equations 30983 + 19a + 32b + 347c = 32768u, 7390 + 22a + 27b + 349c = 32768v, 481 + 19a + 29b + 353c = 32768w"
    - got a = 10469 => "you" in awascii32
    - got b =  7226 => "_wo" in awascii32
    - got c = 14158 => "n_c" in awascii32
    
    # third ciphertext
    25974 + a*19 + b*32 + c*347 ≡ 0 (mod 32768)
    26744 + a*22 + b*27 + c*349 ≡ 0 (mod 32768)
     9122 + a*19 + b*29 + c*353 ≡ 0 (mod 32768)
    ---
    - deferring to Wolfram Alpha: "solve the diophantine equations 25974 + 19a + 32b + 347c = 32768u, 26744 + 22a + 27b + 349c = 32768v, 9122 + 19a + 29b + 353c = 32768w"
    - got a = 20582 => "her" in awascii32
    - got b =  3380 => "rie" in awascii32
    - got c = 26344 => "s!}" in awascii32
    ```

addendum:
  - the [official solution](https://github.com/jellyctf/challenges/blob/662f1eb8d032f967076fb630b549ccbcf1996c9f/crypto/cherry/solve/solve.py) uses SymPy. since I skipped the number crunching by using Wolfram Alpha, now would be a good time to refresh some linear algebra (with the first ciphertext)
  - we can rewrite our system of linear congruences in the form $A \vec x \equiv \vec v \pmod m$:
```math
\begin{align}
\begin{bmatrix} 19 & 32 & 347 \\ 22 & 27 & 349 \\ 19 & 29 & 353 \end{bmatrix} \begin{bmatrix} a \\ b \\ c \end{bmatrix} & \equiv - \begin{bmatrix} 10992 \\ 30978 \\ 12520 \end{bmatrix} & \pmod{32768} \\
& \equiv \begin{bmatrix} 21776 \\ 1790 \\ 20248 \end{bmatrix} & \pmod{32768}
\end{align}
```
  - (note that the official solution has $\vec v$ equal to the starting configurations, and subtracts $\vec x$ from $32768$ when decoding)
  - to solve for $\vec x$, we want to find $A^{-1}$ so that:
```math
\begin{align}
A^{-1} A \vec x & \equiv A^{-1} \vec v & \pmod m \\
I \vec x & \equiv A^{-1} \vec v & \pmod m \\
\vec x & \equiv A^{-1} \vec v & \pmod m
\end{align}
```
  - $A$ is invertible if it has full rank (i.e. $\det A \neq 0$). then, $A^{-1} = (\det A)^{-1} C^T$, where $C^T$ is the transpose of the cofactor matrix (a.k.a. the adjugate of $A$). to calculate the determinant (via Laplace expansion) and the cofactor matrix, we first want to calculate the matrix of minors
      - geometric interpretation of the determinant with respect to inverting a matrix: <https://www.youtube.com/watch?v=uQhTuRlWMxw>
      - inverting a 3×3 matrix: <https://www.youtube.com/watch?v=S4n-tQZnU6o>
      - note that since we need to calculate the modular multiplicative inverse of the determinant, we also want to test that it's coprime with the modulus (i.e. $\gcd (\det A, 32768) = 1$)
```math
\begin{align}
M & = \begin{bmatrix} \begin{vmatrix} 27 & 349 \\ 29 & 353 \end{vmatrix} & \begin{vmatrix} 22 & 349 \\ 19 & 353 \end{vmatrix} & \begin{vmatrix} 22 & 27 \\ 19 & 29 \end{vmatrix} \\ \begin{vmatrix} 32 & 347 \\ 29 & 353 \end{vmatrix} & \begin{vmatrix} 19 & 347 \\ 19 & 353 \end{vmatrix} & \begin{vmatrix} 19 & 32 \\ 19 & 29 \end{vmatrix} \\ \begin{vmatrix} 32 & 347 \\ 27 & 349 \end{vmatrix} & \begin{vmatrix} 19 & 347 \\ 22 & 349 \end{vmatrix} & \begin{vmatrix} 19 & 32 \\ 22 & 27 \end{vmatrix} \end{bmatrix} \\
& = \begin{bmatrix} (27 \cdot 353) - (349 \cdot 29) & (22 \cdot 353) - (349 \cdot 19) & (22 \cdot 29) - (27 \cdot 19) \\ (32 \cdot 353) - (347 \cdot 29) & (19 \cdot 353) - (347 \cdot 19) & (19 \cdot 29) - (32 \cdot 19) \\ (32 \cdot 349) - (347 \cdot 27) & (19 \cdot 349) - (347 \cdot 22) & (19 \cdot 27) - (32 \cdot 22) \end{bmatrix} \\
& = \begin{bmatrix} -590 & 1135 & 125 \\ 1233 & 114 & -57 \\ 1799 & -1003 & -191 \end{bmatrix} \\
C & = M \odot \begin{bmatrix} +1 & -1 & +1 \\ -1 & +1 & -1 \\ +1 & -1 & +1 \end{bmatrix} \\
& = \begin{bmatrix} -590 & -1135 & 125 \\ -1233 & 114 & 57 \\ 1799 & 1003 & -191 \end{bmatrix} \\
\det A & = A_{11} C_{11} + A_{12} C_{12} + A_{13} C_{13} \\
& = 19 \cdot (-590) + 32 \cdot (-1135) + 347 \cdot 125 \\
& = -4155 \\
& \equiv 28613 & \pmod{32768} \\
C^T & = \begin{bmatrix} -590 & -1233 & 1799 \\ -1135 & 114 & 1003 \\ 125 & 57 & -191 \end{bmatrix} \\
A^{-1} & \equiv (\det A)^{-1} C^T & \pmod{32768} \\
& \equiv 28613^{-1} C^T & \pmod{32768} \\
& \equiv 14093 C^T & \pmod{32768} \\
& \equiv \begin{bmatrix} 8202 & 23139 & 23643 \\ 27997 & 970 & 12271 \\ 24921 & 16869 & 27981 \end{bmatrix} & \pmod{32768} \\
\vec x & \equiv A^{-1} \vec v & \pmod{32768} \\
& \equiv \begin{bmatrix} 8202 & 23139 & 23643 \\ 27997 & 970 & 12271 \\ 24921 & 16869 & 27981 \end{bmatrix} \begin{bmatrix} 21776 \\ 1790 \\ 20248 \end{bmatrix} & \pmod{32768} \\
& \equiv \begin{bmatrix} 4194 \\ 29860 \\ 25598 \end{bmatrix} & \pmod{32768}
\end{align}
```
