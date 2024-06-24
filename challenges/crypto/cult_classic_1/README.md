# [crypto] cult_classic_1

<table><tbody>
<tr><th>Value</th><td>335 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Files</th><td><a href="./files/01.zip">01.zip</a> · <a href="./files/01_welcome.txt">01_welcome.txt</a></td></tr>
</tbody></table>

> "We are not a cult" - Starknights (probably)

This challenge contains two flags:
- Submit the first flag to ```cult_classic_1``` 
- Submit the second (final) flag to ```cult_classic_2```

Flags for this challenge are **case insensitive**. 

- Please open a ticket in Discord if you believe you have the correct password and are running into unzipping issues
- First hint is for Stage 1
- Second hint is for Stage 2
- Third hint is for stage  3

---

raw notes:

  - first letter of each non-blank line in `01_welcome.txt` (above the ASCII art) spell out `PRINCESS`, which is the password to `01.zip`
  - `02.txt` contains Base64-encoded `Li brx fdq ghfrgh wklv, brx fdq kdyh wkh qhaw nhb: ELJQHUG`, which looks like a Caeser cipher; decryption is [A-Z] left shift by 3 (or drop it into <https://www.dcode.fr/rot-cipher>), and you get `If you can decode this, you can have the next key: BIGNERD`, which is the password to `02.zip`
  - <https://www.dcode.fr/cipher-identifier> identified `03.txt` as likely using the Vigenère cipher, which can be decrypted using <https://www.dcode.fr/vigenere-cipher> with the previously obtained key (`BIGNERD`)
    ```
    OWZ OEU, KFZKF E WOBO LBV PRVZ KSJFUUA YB JRU: KMRYCTWG{BNVW_ZV_KCYG_E_NDSU_AC}
    LFZFDKE CFXS RUHVEHZ QY ASK RWMX, GEBH UPOF OVB BVJ CVFFFMJ SSIZBZJ: NPZHO
    ```
    ```
    NOT BAD, HERES A FLAG FOR YOUR EFFORTS SO FAR: JELLYCTF{THIS_IS_JUST_A_WARM_UP}
    HOWEVER YOUR JOURNEY IS NOT OVER, TAKE THIS KEY AND PROCEED FORWARD: ALIEN
    ```
  - meta: this is one of the handful of challenges that deviates from the `jellyCTF{}` flag wrapper (due to case insensitivity)
