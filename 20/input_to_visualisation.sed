s/^([a-z]+)/  \1/
s/^%([a-z]+)/  \1 [style=dashed]; \1/
s/^&([a-z]+)/  \1 [style=bold]; \1/
1i\
digraph {
1i\
\ \ node [shape=box]
$a\
\ \ rx [style=filled, fillcolor=red, fontcolor=white]
$a\
}
