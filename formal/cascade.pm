// PRISM DTMC, finite abstraction of the three canonical traces.
// naive routing delegates away the sink check; checked routing always mediates.
dtmc
const bool checked;
const int trace; // 0=T*, 1=Tb, 2=Tj
module cascade
 s : [0..4] init 0;
 [] s=0 -> (s'=1);
 [] s=1 & checked & trace!=1 -> (s'=3);
 [] s=1 & (!checked | trace=1) -> (s'=2);
 [] s=2 & trace=0 -> (s'=3);
 [] s=2 & trace!=0 -> (s'=4);
 [] s=3 -> (s'=3);
 [] s=4 -> (s'=4);
endmodule
label "bad_execute" = s=4 & trace!=1;
label "execute" = s=4;
