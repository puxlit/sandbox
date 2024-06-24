# [rev] awassmbely

<table><tbody>
<tr><th>Value</th><td>771 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>lisp_beamer</td></tr>
<tr><th>Files</th><td><a href="./files/code.s">code.s</a></td></tr>
</tbody></table>

My AWA 5.0 code got jumbled up with my Assembly code help! What's in register eax?

Put the answer in the decimal number base for example if your answer is 0x11 the flag would be 
jellyCTF{17}

---

raw notes:

  - (`awa` is 0, `wa` is 1)
  - annotated:
    ```
    <+0>:     endbr64
    <+4>:     push   rbp
    <+5>:     mov    rbp,rsp
    <+8>:     mov    DWORD PTR [rbp-4],wawawa  ; immediate is 0b111
    <+15>:    mov    DWORD PTR [rbp-8],wawaawa ; immediate is 0b110
    <+22>:    mov    eax,DWORD PTR [rbp-4]     ;                     eax is 0b00000111 (  7 base 10)
    <+25>:    add    eax,DWORD PTR [rbp-8]     ;                     eax is 0b00001101 ( 13 base 10)
    <+28>:    shl    eax,waawaawa              ; immediate is 0b100, eax is 0b11010000 (208 base 10)
    <+31>:    pop    rbp
    <+32>:    ret
    ```
  - flag is `jellyCTF{208}`
  - meta: the `jellyCTF{}` flag wrapper seems kinda pointless here
