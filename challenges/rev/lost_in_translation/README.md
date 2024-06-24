# [rev] lost_in_translation

<table><tbody>
<tr><th>Value</th><td>676 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>kuuhaku0989</td></tr>
<tr><th>Files</th><td><a href="./files/awawa.txt">awawa.txt</a> · <a href="./files/src.py">src.py</a></td></tr>
</tbody></table>

So I tried making an AwaSCII translator to help with writing Awatalk, but I don't really know python so I just copied some code off the internet.
The output looks fine on first glance, but when I try to use it, it doesn't work.
Can you help me figure out what's wrong with it?

Due to technical limitations with AwaSCII, the flag format for this challenge is jellyCTF(awawawa) 

---

raw notes:

  - encoding starts with `awa`, then it takes the index (0 to 63) for the char from `lookup`, encodes it into eight binary digits, and substitutes 0 for ` awa` and 1 for `wa`. just need to write the reverse to decode the flag
    ```py
    awaflag = open("awawa.txt", "r").read()
    flag = open("flag.txt", "w")
    
    # copied from src.py
    lookup = "AWawJELYHOSIUMjelyhosiumPCNTpcntBDFGRbdfgr0123456789 .,!'()~_/;\n"
    
    assert awaflag.startswith("awa")
    awaflag = awaflag[3:].replace(" awa", "0").replace("wa", "1")
    assert len(awaflag) % 8 == 0
    
    output = ""
    
    for i in range(0, len(awaflag), 8):
        output += lookup[int(awaflag[i:i + 8], 2)]
    
    flag.write(output)
    ```
  - flag is `jellyCTF(C0p13D_tw0_b1T_t00_MuCh)`
  - meta: this is one of the handful of challenges that deviates from the `jellyCTF{}` flag wrapper
