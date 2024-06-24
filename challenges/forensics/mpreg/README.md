# [forensics] mpreg

<table><tbody>
<tr><th>Value</th><td>649 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Files</th><td><a href="./files/flag.mpreg4">flag.mpreg4</a></td></tr>
</tbody></table>

This challenge might need a little correction 💢💢💢

10 point hint: Tool \
20 point hint: Area to focus

---

raw notes:

  - [degen meme](https://www.urbandictionary.com/define.php?term=Need%20Correction%20%F0%9F%92%A2%F0%9F%92%A2)
  - taking a look at the header…
    ```
    $ xxd -l 160 flag.mp4
    00000000: 0000 0020 6674 7970 6973 6f6d 0000 0200  ... ftypisom....
    00000010: 6973 6f6d 6973 6f32 6176 6331 6d70 7265  isomiso2avc1mpre
    00000020: 6734 3100 0010 c66d 6f6f 7600 0000 6c6d  g41....moov...lm
    00000030: 7668 6400 0000 0000 0000 0000 0000 0000  vhd.............
    00000040: 0003 e800 0011 a800 0100 0001 0000 0000  ................
    00000050: 0000 0000 0000 0000 0100 0000 0000 0000  ................
    00000060: 0000 0000 0000 0000 0100 0000 0000 0000  ................
    00000070: 0000 0000 0000 0040 0000 0000 0000 0000  .......@........
    00000080: 0000 0000 0000 0000 0000 0000 0000 0000  ................
    00000090: 0000 0000 0000 0300 0005 d574 7261 6b00  ...........trak.
    ```
  - so the `ftyp` box is malformed; compatible brand should be corrected from `isomiso2avc1mpreg41` to `isomiso2avc1mp41`
  - flag is `jellyCTF{i_can_fix_her}`
