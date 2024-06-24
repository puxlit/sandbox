# [misc] just_win_lol

<table><tbody>
<tr><th>Value</th><td>890 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Connection info</th><td><a href="https://just-win-lol.jellyc.tf/">https://just-win-lol.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/just_win_lol.zip">just_win_lol.zip</a></td></tr>
</tbody></table>

looks like that new Balatro game has already got some knockoffs.
the RNG for this one sucks though - how are you ever meant to win?!
reminder: do not bruteforce, you won't win

10 point hint: pointer on where to start looking

20 point hint: advice on what to start doing

---

raw notes:

  - every time you draw a hand, the PRNG is seeded with the current time in seconds. note we have to get five wins in ten attempts. the endpoints are rate-limited (not that brute-forcing would really help)
  - so… we can take their Go code, and adapt it to spit out the next few winning hands (and what time they'd occur)
  - (in my run, I hit 1 and 2, was late to 3 and 4 by one second, and hit 5 + 6 + 7)
    ```
    [ec2-user@ip-172-30-0-229 winning]$ docker build --tag 'winning' . && docker run --rm -i winning
    [+] Building 1.4s (15/15) FINISHED                                                                                                                                                           docker:default
     => [internal] load build definition from Dockerfile                                                                                                                                                   0.0s
     => => transferring dockerfile: 349B                                                                                                                                                                   0.0s
     => [internal] load metadata for docker.io/library/golang:1.22                                                                                                                                         1.3s
     => [internal] load metadata for docker.io/library/alpine:latest                                                                                                                                       1.3s
     => [internal] load .dockerignore                                                                                                                                                                      0.0s
     => => transferring context: 2B                                                                                                                                                                        0.0s
     => [build 1/6] FROM docker.io/library/golang:1.22@sha256:969349b8121a56d51c74f4c273ab974c15b3a8ae246a5cffc1df7d28b66cf978                                                                             0.0s
     => [run 1/3] FROM docker.io/library/alpine:latest@sha256:77726ef6b57ddf65bb551896826ec38bc3e53f75cdde31354fbffb4f25238ebd                                                                             0.0s
     => [internal] load build context                                                                                                                                                                      0.0s
     => => transferring context: 254B                                                                                                                                                                      0.0s
     => CACHED [run 2/3] WORKDIR /app                                                                                                                                                                      0.0s
     => CACHED [build 2/6] WORKDIR /app                                                                                                                                                                    0.0s
     => CACHED [build 3/6] COPY go.mod go.sum /app/                                                                                                                                                        0.0s
     => CACHED [build 4/6] RUN go mod download                                                                                                                                                             0.0s
     => CACHED [build 5/6] COPY *.go /app/                                                                                                                                                                 0.0s
     => CACHED [build 6/6] RUN CGO_ENABLED=0 GOOS=linux go build -o /winning                                                                                                                               0.0s
     => CACHED [run 3/3] COPY --from=build /winning /app/                                                                                                                                                  0.0s
     => exporting to image                                                                                                                                                                                 0.0s
     => => exporting layers                                                                                                                                                                                0.0s
     => => writing image sha256:6e89cfa6a1589438dbdb1d4bd4193bef75b07035a3fbcab0efa312742e6ea695                                                                                                           0.0s
     => => naming to docker.io/library/winning                                                                                                                                                             0.0s
    t = 1718222734 (2024-06-12T20:05:34Z)
    Win 1 at t = 1718222750 (2024-06-12T20:05:50Z): [{9 d} {2 s} {7 h} {A s} {A s} {K s} {A c} {A c} {9 d} {T d} {8 c} {A h}]
    Win 2 at t = 1718222757 (2024-06-12T20:05:57Z): [{Q s} {Q c} {4 s} {Q c} {3 h} {9 c} {6 d} {A d} {K c} {5 c} {Q d} {Q d}]
    Win 3 at t = 1718222868 (2024-06-12T20:07:48Z): [{T c} {2 d} {T d} {A d} {J s} {T d} {T d} {5 h} {8 d} {8 c} {T s} {9 h}]
    Win 4 at t = 1718222981 (2024-06-12T20:09:41Z): [{K s} {5 d} {J c} {5 d} {5 c} {J d} {J d} {J s} {J h} {Q c} {K h} {3 h}]
    Win 5 at t = 1718223016 (2024-06-12T20:10:16Z): [{6 s} {7 d} {2 s} {9 c} {2 h} {7 s} {K h} {T s} {8 c} {2 s} {2 c} {2 s}]
    Win 6 at t = 1718223031 (2024-06-12T20:10:31Z): [{T h} {T c} {7 h} {J c} {J h} {T d} {A s} {2 h} {9 h} {T d} {T c} {6 s}]
    Win 7 at t = 1718223172 (2024-06-12T20:12:52Z): [{8 c} {4 s} {8 c} {8 d} {3 s} {7 h} {8 h} {A h} {J d} {8 d} {A d} {Q h}]
    Win 8 at t = 1718223213 (2024-06-12T20:13:33Z): [{5 s} {8 s} {5 h} {7 d} {3 d} {5 h} {8 s} {5 h} {5 d} {Q h} {6 s} {7 h}]
    Win 9 at t = 1718223234 (2024-06-12T20:13:54Z): [{T c} {T d} {K h} {T h} {T h} {Q c} {4 c} {8 c} {3 d} {3 c} {T s} {7 d}]
    Win 10 at t = 1718223249 (2024-06-12T20:14:09Z): [{K c} {3 s} {7 c} {7 h} {7 s} {7 h} {8 h} {8 h} {K h} {3 d} {K s} {7 h}]
    Win 11 at t = 1718223351 (2024-06-12T20:15:51Z): [{A d} {Q s} {K d} {T d} {6 h} {K c} {K c} {5 h} {6 h} {K d} {5 d} {K h}]
    Win 12 at t = 1718223377 (2024-06-12T20:16:17Z): [{5 c} {A d} {4 h} {9 d} {J s} {A d} {7 d} {A c} {Q c} {A c} {A s} {4 s}]
    Win 13 at t = 1718223422 (2024-06-12T20:17:02Z): [{9 s} {7 s} {8 s} {K s} {9 d} {9 c} {A c} {9 d} {9 c} {5 h} {3 c} {J h}]
    Win 14 at t = 1718223472 (2024-06-12T20:17:52Z): [{T h} {5 d} {J s} {3 c} {3 d} {9 c} {9 c} {J d} {3 s} {3 h} {4 c} {3 d}]
    Win 15 at t = 1718223476 (2024-06-12T20:17:56Z): [{J c} {J h} {7 h} {A s} {J c} {4 d} {5 h} {9 h} {J c} {7 s} {J c} {A c}]
    ```
  - flag is `jellyCTF{its_v3ry_stra1ghtf0rw4rd_s1mply_g3t_g00d_rng}`
  - meta: this feels like a slightly harder version of [[crypto] the_brewing_secrets](../../crypto/the_brewing_secrets/README.md), because now you gotta time your inputs. not sure why it's classified as "misc" instead of "crypto"
