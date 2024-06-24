# [rev] rev1

<table><tbody>
<tr><th>Value</th><td>784 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Files</th><td><a href="./files/rev1">rev1</a></td></tr>
</tbody></table>

you'll want some kind of disassembler e.g. ghidra, ida, binary ninja, radare2

---

raw notes:

  - using Hex-Rays v8.4.0.240320 via <https://dogbolt.org/>:
    ```c
    //-------------------------------------------------------------------------
    // Data declarations
    
    /* ... */
    char aCEerMTzxIaKxMx[38] = "c^eer<M?tZX<*Ia,kX?*MX_)kX:Xik*g<,..v"; // weak
    /* ... */
    ```
    ```c
    //----- (0000000000401176) ----------------------------------------------------
    int __cdecl get_key()
    {
      return 7;
    }
    ```
    ```c
    //----- (0000000000401180) ----------------------------------------------------
    int __fastcall main(int argc, const char **argv, const char **envp)
    {
      int key; // ebx
      int i; // eax
      char v6[72]; // [rsp+0h] [rbp-48h] BYREF
    
      /* ... */
        key = get_key();
        /* ... */
          for ( i = 0; i <= 36; ++i )
            v6[i] = aCEerMTzxIaKxMx[i] + key;
          key = strcmp(v6, argv[1]);
          if ( key )
          {
            puts("Flag incorrect.");
            return 1;
          }
          else
          {
            puts("Flag correct!");
          }
        /* ... */
    ```
  - so ciphertext is `c^eer<M?tZX<*Ia,kX?*MX_)kX:Xik*g<,..v`, decryption is ASCII right shift by 7:
    ```pycon
    >>> ''.join(chr(ord(x) + 7) for x in 'c^eer<M?tZX<*Ia,kX?*MX_)kX:Xik*g<,..v')
    'jellyCTF{a_C1Ph3r_F1T_f0r_A_pr1nC355}'
    ```
