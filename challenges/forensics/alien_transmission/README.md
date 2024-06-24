# [forensics] alien_transmission

<table><tbody>
<tr><th>Value</th><td>373 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Files</th><td><a href="./files/alien_transmission.mp3">alien_transmission.mp3</a></td></tr>
</tbody></table>

Note: Volume warning

My radio picked up some weird interference -
I'm sure it's aliens but nobody believes me!!!

---

raw notes:

  - flag is visible with a spectrogram (e.g. using Audacity). the one below is generated with `ffmpeg -i ./files/alien_transmission.mp3 -lavfi showspectrumpic=s=1280x240:color=moreland:fscale=log:stop=8000:drange=48 ./spectrum.png`

    ![](./spectrogram.png)
  - flag is `jellyCTF{youre_hearing_things}`
