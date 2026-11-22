#!/usr/bin/env python3
"""THE WORLD TODAY - front page for Sunday 22 November 2026, drawn by code.

Pure Python standard library only: a bytearray RGB canvas, an embedded
1-bit bitmap font (rasterized from Noto TTFs by my own work/rasterize.py),
and a hand-written PNG encoder (zlib + struct + CRC32). No Pillow, no
third-party imports, no font files read at run time, no network, no clock:
the same run always produces the same bytes.

Run:  python3 main.py        (writes entry.png in the current directory)
"""
import base64
import binascii
import hashlib
import struct
import zlib

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 40
CONTENT_W = PAGE_W - 2 * MARGIN  # 944

# ---------------------------------------------------------------- palette
NAVY = (15, 34, 60)        # masthead bar
NAVY_DEEP = (12, 27, 47)   # also-today band
GOLD = (198, 158, 38)      # rules and labels
CREAM = (247, 241, 226)    # paper
BAR_TINT = (241, 233, 213)  # story-6 bar background
RUST = (178, 63, 40)       # kicker bars and accents
INK = (30, 30, 32)         # body text
MUTED = (112, 106, 94)     # sources and footer
HAIR = (206, 196, 176)     # hairline rules
BAND_TEXT = (238, 234, 222)

# ---------------------------------------------------------------- font data
# 1-bit glyph bitmaps, rasterized from Noto TTFs by work/rasterize.py.
# CHARSET is the character set, in order. FONT_BLOB holds every glyph
# bitmap of every table, table by table (MAST, H1, H2, KICK, LAB, BODY,
# BODY2, SRC, FOOT), chars in CHARSET order; a glyph's byte length is
# ((width + 7) // 8) * height, so offsets are recovered by summing.
# TABLES[name] = [(advance, width, height, dx, top), ...] in CHARSET order.
CHARSET = ' "$\'()+,-./0123456789:;ABCDEFGHIJKLMNOPRSTUVWXYZ`abcdefghijklmnopqrstuvwxyz~·×Ü–—’'

FONT_BLOB = (
    's8W+LJ+rtnJ+N[?5NDbD5N2VB5N2SA+2RpV+2IjU+2IdS%tOQX%tJm)%tJm)#68uK#66FXz!!*\'"!!*\'"!!*\'"!!*\'"!!*\'"!\'gA]!V(Yi#N7n_&&B@G+2K&g++Xsl5J[m"5J[m"J&)ZRJ)LogJ+3L=J,\'\'EJ,]KK5Q:]`5QBXA5QCKY+92<?&-)Y0#QOh>"98DZ!<<)g!\'gMY!"],)!!E9!#6Fl&564"HIfUYhIfU)XrrEB&rrEB&rrEB"rrEB"It7joIt7jo5Cj\'t+2JJ<#N6a)!Vq*C!!e#S!!*\'"!!*\'"!!*\'"!!*\'"!!*\'"!!*\'"!!*\'"s7h*5J+,\\\\5N"ca+2Au6+2AD;%tG1@#64u/z$ig8e!!)Kg"5j.i^]5I,!\'bu6IfKKK!!3*""9&9*rW!K.!"\\u-+8c*\\quAtZ!\'gA]J,B:rp],g=!.XbDs7cTop]1?h!<;fos7cTop]1?h!<;fos7cTop]1?h!<;foJ+s"np],gA!.XnH5PtLGqu@i:!$D+=&,ZD<rW!3&!!E3#!WN-"rr<%K!!#66!$AuV#J^<AhuEcH!!"tY!"?XC!-eJD*WQ0^!!!PF!!hE^"8Diuqu?cs!!3*"!WRZMs*t+L^]=Dm!<:sWs6p#<n,Rt5!.XbDJ+s"nquD6E!.XnHJ,B:rquD6E!.XnHJ,B:rquD6E!.XnHJ,B:rquD6E!.XnHJ,B:rp],g=!.XbDJ+*I<n,WLH!<:sWs1eX7J-#ZM!WN-#rW!&u!!D]j#N,Rm^]5GV!\'C5]Du]mRz!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!*\'!s53k]!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'!!!!\'zz++QSkJ)GhGs7$\'XJ+.sW5O]3Q#OhiR"5j9s"2G"h"ooVChuE`Ws8RTLz++SjVJ)L@bs5<q8s58CbJ)EQ,"onW3!!iQ1!#P\\Q!"],A!&+C,!$D7a!+5e7!+5dl!5JTM!5JSb!.Y*#!It1N!<<3%!rrB&!WWE)"onc+"98i1$ig\\9#QP\\A(]YBQ&-*7A0E<d,+93Ma?iXR75QF%L^];.M^]8lbz!!!!_HiO0G56(f`5JRO%5N!(M+7Kg9+7LBI+8?rQ+8A(q+8e@u+8e@u+9$cb+9$cb+9$cb+9$cb+9$cb+9$cb+92B9+92B9+92B9+92B9+92B9+92B9+92B9+92B9+92B9+9-ic+9-ic+9$cb+9$cb+9$cb+9$cb+9"M"+8e@u+8e@u+8d5U+8?rQ+8?BA+7Kg=+7KO55MuYA5JR<t5C``_IK0?QhuE`Wzrr<$"rr<$$rr<$(rr<$0rr<$@rr<%Krr<0$rrE)frrE)Frr@P0rr@NZrr>4nrr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$0rr<$@s*u3ks8Duu!!!&trW!2mIt/(!5N"ca5O^nq5PT`d5PT`d5Q$#h+8l/s+8l/s+8gWH+8gWH+8e@=+8d4r5PtPt5PtK]5PP3Y5O\\XQ5O\\XQ5MuMAJ%u$aIt.M!rVuouqu?]tp](9rhuE`^^]4?FJ,fQj!!!!]!!!"<!!<8[!!<=R!!<H+!!<W0!!b1X!"XSZs8W-!s8W-!s8N&us8N&us8N&us8N&us8N&us8Duu!!!&qqu?uks*u3LJ)EQLJ+,\\\\J,"NO5PT`D5Q$#H5Q$#H5Q$#H5Q$#H5Q!a]5Pu&-5PtK]5PtK]5PP3YJ+s!DJ+*F<J)C;,s*t(MrVup\'huE`Zqu?]ss1eU7J)C;,5PP3Y5PtK]+8c*=+8u6?+8u6?+9!;]+9+M)+9-ci+92<?+92<?+9)6>+9)6>+9)6>+8l-=5PT^.5O^mf5N!W6It.d_rVup_J,fQLs6p!g!<;Ng!!3,h!!!-$n,NFjs6p!g#64/m!!N>k!!!H-n,NFos6p!g)#s(*!"f2"!!"_Qn,NGrs6p!g@/o]r!5SX(!!%QLn,NK>s6p!h!<;Ng!s&Aj!!WH\'n,NXms6p!s!<;Ng#QXno!#P_9n,O""s6p"B!<;Ng?i^5r!+5g,n,WLgs8RWLs8W+Ls8W-!JH,ZLs*t(Ls6p!g!<;Ng!!*&g!!!$!n,NFgs6p!g!<;Ng!!*&g!!!$!n,NFhs6p!g"98,r!.Y%KJ.M\\[i",kfi",kfi",kfi",kfi",kfi",kfi",kfi!9;_E!QFD0Gjci0Gjci0Gjci!#P\\9!#P\\9!#P\\9!#P\\9!"f2*!##V:!#u%>J/A:d^b>cghuEb,n,NH<p](;Dp](;Dp](:Yqu?^]qu?^]qu?^]qu?^]r&asDr-SK/r;6OZr;6OZq"t,Aq#18Cq#18CnGWE;i-k\\+^cqi!J0+gk!!C::!!#4`z!!"**J,js=huW`dn,rFrp]pR)p^d-1r"&9-r#bD=r#bD5pcn6Qpcn6Qn:0p4J:I%g!.XJ<!.XJ<!<;Ng!<;Ng!<;6^!<;gY_#Nmgi;_^WnGhDgq#B7or;Y[sr;Y[sr;Z7.rr;I0rr;I0rr;I0rr;I0rr;I0rdXDZrdXDZrdXDZr\'0Zmr\'0Zmr#bDMp`JuIp^cj9n-A_1huia=^]F?tJ,k%I!!!8^!.Y%Kr."bHr."bHr."bHr."bHr."bHpj`>Dq#CBoq!\\7`0]2p20YdYg@))aB@))aBi4o<m^]4?8^]4?:J,fQOJ,fQS!!!!(!!!!0!!!!?!!!!?!!!!]!!!!]!!!"H!!!"D!!!#o!!!&h!!!&h!!!,j!!!,Z!!!8^!!!PF!!!PF!!"*k!!"*k!!#66!!%KK!!%KK!!)uu!!)uu!!3\'!!!2utz!!%I4!!2j:^^\'WFi",;fn/q-1p`Ju1r\'0ZUr\'0ZUrdXDBrdXDBrdXDBrdXDBr."JHr\'0r]r\'1)ipcn`gn/q[ki",kfJ-Z,L!!E9#!!3-"J,k*!huFl!n,`Rhp^curr#aksr]f=jrdWijs*rrKs8TkFs8Tk>s8Tk>s8Tk>s8Tk>s8Tk:s8Tk:s*qfdrdV]gr]f<Gr#ai%p^c9nn-AFn^]F?t!!!8^z!!%Im!!E!\\!!i9`J.MDs^`W%fi\'6]Qn3?Capj_cTpj_cTr."2Xr;Z7.r;Z6sr;Z6srr;Hurr;Hurr;Hurr;HurdXDJrdXDJrdXDJr]fl_r]fl_rZCnWrX\\cgrWi@>rW3&FrVup/rVup/rVup/rVup?qu?^=r!!-Cr#Ph[pc\\["pc\\["n3-gon3-goi\'.3+i\'.3+^`NP@J00;k!!e&P!!D3L!!#4`!$;2j^jj0"i;_a8i;_a8i.&Ol^`NOVzzzzz!!!!`J:GB7i;_a8i;_a8i;__b^d!>Z!"XTEi\'6.Ln:0qWn:0qWn3>hqi"(><zzzzz!!!!@J3VtAi.(6Gn:0qWn:0pln.5!nn,r.^huhm>^]T)l!#u!sz!$Ct9!!!!@qu?]s!$D+=!!!!`rVuou!\'gG_!!!!`rVuou!,ql;!!!";rr<$!!)NUp!!!#>s*t(L!6>+i!!!"Ss*t(L!Jg]j!!!%Ps1eU7!<`A;!!!*\'s53kW!s/G[!!!\'$s53kW"p+bn!!!3\'s6p!g"9AJk!!!-%s7cQo$ikeP!!!E-J,B9H#QTAP!!!i95PtK](]Zf"!!!Q15Q1W_0E<3o!!"\\Q+9)<@+93M`!!$C,+9)<@?iU`;J,hh7&-%.[^]4oFJ,m@b#QMR>J,fiS^]Arc#QMR?J,f]OhuS?."979]!!!-$n-=ID"98/rrW%HJs8W-!huE`fs24j:!!iP?s1eU>s1n[(!!iP>J+s!Ks1j-^!!iP>J,B9Os1j-`!!iP>5Q1Wfs1gku!!iP>5Q1Wfs1gku!!iP>5Q1Wfs1j-`!!iP>J,B9Os1j-^!!iP>J+s!Ks1n[(!!iP?s1eU>s24a7!!iQ(n,NFns2"_c!!iP>J+*FCs1j-Z!!iP>5PtKds1gku!!iP>+9)<Gs1f`V!!iP>+9-irs1f`VJ-Z+i+9-irs1f`VJ-Z+i+9-irs1f`VJ-Z+i+9)<Gs1f`V!!iP>+9)<Gs1gku!!iP>5PtKds1gko!!iP>J+*FCs1nYb!<<*!p](9oz!!Dcj!!"+VIt.NKJ:HJWrr>:Q"9&9bp]pcu5PPK_!$CtHqu@i6+8c*\\p`KD6+7MMm!$C\\pqu@hSJ,B9f!.XnH!!%NH!!!$!p](9os7cQo!<;fo!!*&o!!!$!p](9os7cQo!<;fo!!*&o!!!$!p](9os7cQo!<;fo!!*&o!!!$!qu?]ss82is!.XnH!!%NH!!!"Kqu?^>5PtK]3\'[<@!&u)"!!"u#rVuqC&,lP/GR+6K!-eVG!!)Khs*t..!<9h:^]6UW#CldZpcJNV!$?^ks8W,W!!!Q0_#=<6#QMSh^]4W>^`W%G#QMR]p](R!^^pDE#QMRMrr<<(^^\'l>#QMREs*t@S^^\'nT#QMRAs1em>^]XVp#QMRAs54.^^]XVp#QMRAs6p9n^]XW+#QMRAs6p9n^]XW+#QMRAs6p9n^]XW+#QMRAs6p9n^]XW+#QMRAs6p9n^]XW+#QMRAs6p9n^]XW+#QMRAs54.^^]XVp#QMRAs54.^^]XVp#QMRAs1em>^]XVP#QMREs*t@S^^\'mi#QMRErr<<(^^\'i=#QMRMqu@!%^^p2?#QMR]n,N^n^d$`W#QMShJ,fiS_#=<6s8W,W!!*\'!s8VQns1ea+#QMR>n-B!/!,r2C^]8<Ys1eUg#QMR>0F.Wn!&+ZX^]4oNs1eUG#QMR>&-r6N!#Pt@^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(s8N\'(s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4QDs1eU;#QMR>":+tB!!EQ,^]4cJs1eUC#QMR>$jZgJ!#u7D^]6J%s1eV^s8W-!r;Zfss6p9n^]X\'2s1eX(#QMR>E!QEY!&+ZX^]6%ns1eUg#QMR>0F.Wn!"]D8^]4oNs1eUG#QMR>(^L)V!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(huEcWs8RTLz!!!!"pj[eo!"\\!0n,NGQ^^p>C!<7QSrW!!!!!iN("9/?+rr<<\'!!E6$&,lP2rr=/?!!E6$+8c*@rW#1\\!!E-!5PtK`p],gAzJ,B9H!!%NHzs82is!!*&ozs7cQo!!*&ozs7cQo!!*&ozs7cQo!!*&ozs7cSDs+(.E!\'gJ`s7cR9rrE)o!$D4@s82j=rr@QH!$D4@J,B9grr@QH!$D4@5PtL\'rr>:]!$D4@5PtL\'rr=/?!$D4@&,lPNrr<<\'!$D4@#QFcGrr<*"!$D4@!<7Qkrr<%K^`WOU!$C,@n,NFjp`G"d!!!Pf!!*\'!r]gG_J.M\\<#QO8n#QMRAs53k^s1ea:huF#^^]XVp!!iP>"979Z#QMRAs53k^s1ea:huF#^^]XVp!!iP>"979Z#QMRAs53k^s1ea:huF#^^]XVp!!iP>"979Z#QMRAs53k^s1ea:huF#^^]XVp!!iP>"979Z#QMRAs53k^s1ea:huF#^s8W,W!!iP>"979Z#QMRAs53k^s1ea:huF#^^]XVp!!iP>"979Z#QMRAs53k^s1ea:huF#^^]XVp!!iP>"979Z#QMRAs53k^s1ea:huF#^^]XVp!!iP>"979Z#QMRAs53k^s1ea:huF#^^]XVp!!iP>"979Z#QMRAs53k^s1ea:huF#^^]XVp!!iP^#QO8ns8W\'_s8RWLs8N?(i!9:t#QMREs1em>^^\'nT#QMREs1em>^^\'nT#QMREs1em>^^\'nT#QMREs1em>^^\'nT#QMREs1em>^^\'nT#QMREs1em>^^\'nT#QMREs1em>^^\'nT#QMREs1em>^^\'nT#QMREs1em>^^\'nT#QMREs1em>i;`iW+92B!!<;rs!<;rs!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XnH!.XbD!.XbD!.XbD!<;fo!<;fo!<;Ng!<;Ng!<:sW!WTq8!WRZM"9&9##Q+Q%+5d,!zs8W(Js6p9nhuWk.#QMR>IK0WQ^]8TZ#QMR>Du^.C^]7aB#QMR>^]4W>^];.M#QMR?J,fiS^]OQ:#QMRD!!!9(^^L2C#QMRV!!!9(^b>`g#QMSI!!!9(^u,1m#QMU/!!!9(_>"!1#QM^:!!!9(a8>o;#QN-J!!!9(hu3TU#QOi(!!!9(s8N\'!#QN]]J,fiShuCIl#QN-M^]4W>ci;o\'#QMjEhuF#^_uK3+#QM^Ap](R!_>j91#QMX?qu@!%_#OB6#QMU>rW!3\'^jl@a#QMShrr<<(^d%jL#QMR]s1em>^^pI\\#QMREs54.^huj#Ks8W&uJ,K?Hrr<$0s53kW#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU=#QMR>"pb1D!!EQ,^]4KBs1eU;#QMR>$jZgJ!"9,4^]4cJs1eUS#QMR>*!cMZ!\'CMd^]8`es1e[5s8W-!r;Zfl!!E9$"98,r#QN]_s7cR!s53qXqu@!%huWlU!"]+f!WW&t&-(Pgs8E!+s53qXrW!o;huWlW!#tsr!PeX7)ungs^]+9Is53pmrr=kThuTJMJ2@5`!MBCB,QH[&TDsFOs53p=s1i.EhuSo=^dJ.[!K[8r_uJWqL]?;Ms53p5s58P0huSW5iIh0g!JCFBKE\'j1KE(Ios53p1s7$3khuSE/qZHlV!J1:J"979[JcGQKs53p.s8E-#huSB.rWE2Y!J(4J"979[J:IJ!s53p.J,BEKhuS@XqucuW!J#[p"979[J3Wf2s53p.5PP?\\huS?mn,r^K!Iu9]"979[J047_s53p.+5d8$huS?=huj#;"+Up?#QN`^rsunps8W-!huWlW"97ij"+UFPp](Br!WVop!rrB%qu?g!!WW-!!rrA:rW!$#!MBAl!rr@os*t1O!K[82!rr@Ws1e^:!Jg^5!rr@Ss53tZ!J1:?!rr@Qs7cZr!J(4F!rr@PJ,BBK!J#\\!!rr@P5Q1`b!Iu9l!rr@P+9-rn!It^\\K)bq&#QM[A!ItFTirB+1"97B]!It4No)JfA!WW#s!It1MqZ$YI!.Y"K!It0"rr<(M!\'gJ`!It.lrr<(M!$D4@!It.\\rr<(M!!iN(!It.Trr<(M!!E6$!It.Nrr<(M!!3*"!It.Mrr<(M!!%KK"+U@OIfTNK!!#4`!!!-%!!!!(nGE7d!$B!@!!!"KJ02Q,!WN-An,NRi!"\\i)#Q=]6qu@9,!!iK\'+8c*Drr=/=!!iN(5PtKds+!?3!!iOSJ,B9Os1j-^!!E8:J,B9Ks1n[4!!E8Zs7cQrs5<qP!!E8Zs7cQrs5<qP!!E8Zs7cQrs5<qP!!E8Zs7cQrs5<qP!!E8Zs7cQrs5<qP!!E8Zs7cQrs5<qP!!E8Zs7cQrs58D)!!E8ZJ,B9Ks1j-^!!E8:J,B9Os1gks!!iOS5PtKds*u3h!!iN(+8c*Drr<T/!"]&/#Q=]6qu?iu!"\\i)!WN-An,NH<J02Q,!\'e7`J,fQSi;<QT!!"*k!!*\'!s1eU>s24g9#QMX?J-Z+is54.^^jkhYs1j-Z#QMShr!38;J,BQO^jl7es1j-`#QMS(rWiJ=5Q1of^d%f\'s1gku#QMS(rWiJ=5Q1of^d%f\'s1j-^#QMShr!38;J,BQO^jl+as1j-R#QMU>i!9:ts1em>_>aK?s24a7#QOgS!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s53kWs8W+L!<<*!n,NG!s2"_c!!iP>J)C;3s1j-Z!!iP>5PtKds1gku!!iP>5Q1Wfs1gl!!!iP>+9)<Gs1f`V!!iP>+9)<Gs1f`V!!iP>+9)<Gs1f`V!!iP>+9)<Gs1f`V!!iP>5Q:]gs1gku!!iP>5PtKds1j-^!!iP>J+*FCs1nZm!!iQ(rr<$(s3L]F!!iPMs*t(Ss2Y/T!!iPEs1eU>s24lp!!iPAs53k^s2"a)!!iP?s6p!ns2"a1!!iP>s7cR!s1n[4!!iP>J,TEQs1j-`!!iP>5Q:]gs1gl!!!iP>+9-irs1f`VJ-Z+i&-\'EMs54"Zi;`iV!.XbDz!$4A?!!)d)n,NR[#Q+Q,i!95]&)[Qi!$C,$rr=.V"9/?chuiuZ5MuYD!.Wo-rr@Q<!WE(Kp]:-iJ,B9H!.Y"K!!%NK^]4@!s6p!g5QCW]!\'gM`!!",@s1eUFs8VQg#QOi!!!E9$qu?cts8DuuJ,fNK!$D7@J,fiSs*t(Ms8Tk7!.Y$a!!!Q0^`S(3s1gjL"96/dJ-#\\cs*t+L_#Jobs1nYb!.TP!^]8k7s1eVa!<9h7IfOuV!<)s_huNZT+7K=#!"\\i,huEfW%fcS0&)[Efs8W-!s+("Ls54uLn,r^K#Ct_7s54!0huj#;"+\\/hs53p.^]XVp!J%rfs53p.^]XVp!J#\\&s53p.J-5i0!.]S%s53m-J-5i0!.Y%Os53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!$s53kW!!E8Z!!!!(s6p!g!<<*!J,oWLrs/T!&-(Pf*WQHF^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igP4^]4cC#QMR>$igD0^]4W?"96.:#QOu,^]52O!WV\'X&-)_1huGG2!.XJ<?iU0kn,U6(!"\\u0J,fQOs8Duu!!!PF!!*\'!r#bss+90+V49,ol^]52O#QMR>(]Xg@^]52O#QMR>&-)h4huGG2"979Z0E;4ThuFl"!WVWh+92HBn,Qhr!WVWh?iU3,p]*PZ!<;fo^]4@ap]/)0!.XnHJ,fS!quD6I!\'gA^J,fR6rW.NL!\'gG`!!!!@rW<-#!$D4C!!!!@rrN0#!"])2!!!!0s+ULR!"]*a!!!!(s+C@P!!iPJ!!!!(s3(HC!!E8B!!!!$s6\'F_!!E8r!!!!"s7cQo!!3,hzs6p!g!!*&gzs53kW!!%N,zJ)C;,!!%N,z5JR7!!!#7!z5JR7!s8W*!!!!9(i",kW!\'bu649,WdhuJ7W!&sr`s53m,^]6=o#QN]^J%u%<!!E8Z!.Vca0E;4ThuNf8!&+BTs53nWhuGG2!WVWhs53l"!!3,h!<;Ng?iU6-n,`RY!+5d-s6p\'hn,Qhr!<;fps6p"R!!*&o!IskE^]4B7p]EbU!5JR7J+s+1p],gE!.XnK5PtM3!!%NH!^HS`J,fS!quRu<!It.M5Pt^-rW*!!!\'gGe+8u9@!!#7_":tJ6!!!!@rWEc2!rr<$+8uZZrrN0#!$D4L#QFi*!!!Q0#RCA6!!!!0rs/l0L&_2R&-&"%s+C@P!"]*s"94#S!!!9(QimAI!!!!(s,[?_bQ%VC#QO8os2Y0?!!E8j!WU4@!!!-$n,`Ra!!!!$s53nWp](9o!WV\'Xs6p!g!!3,X!<;Ng!!!\'"huNfH!!!!"s1eVan,NFg!<9h7J)C;,!!*&7!.Wo,!!!$!^]6UWzIt.M`huEaAs8R`Op]pio!"T&3s7cR(!!3,p!"8i.s7cR&!!*&s!#P\\9J,B9X!!%NJ!&+BQ5Q1Xj!!#7`!5JR7+9-kA!!!Q0JUd_#&-\'NI!!!9(_>jQ9#QNod!!!-$li7"c"98,r!!!\'"p](9o!<;fo!!!$!qu?]s!.XnH!!!"KrVuou!\'gJ`!!!!@rr<$!!\'gL6!!!";s*t(L!71\\\\!!!#>s1eU7!Jg^5!!!*\'s6p!g!Wi>j!!!3(s7cQo$ip>&!!!9)s82is(]]\'b!!"\\Q5Q1W_?iWFk!!$C,+9)<@^]5JVJ,t0#+9-inJ,g\\k^^#Ai+91:!rW3\'!rr<#t"98-\\s1eUF^`WT,!!`KGs*t(S!"]*[!!WE6s1eU=!!iP>!!E9,s53kc!!E8Z!!iQ,s6p"*!!3,h!#P\\:s7cRJ!!*&o!&+BQs82j>!!%NH!+5d,J,TF5!!#7_!5JR75Q:`!!!",@!.Y%L+9-nB!!!Q0JH,ZM&-\'NI!!!9(_Z0Z:#QNod!!!-$jo>A]"97un!!!\'"qu?]s!WVop!!!$!p](9o!<;fo!!!$!p](9o!<;fo!!!$!p](9o!<;fo!!!$!p](9o!<;fo!!!$!p](9o!<;fo!!!$!p](9o!<;fo!!!$!p](9o!WW&t!!#7`s53lAs8W,o5C`e7pc\\ZYs6r,N"97jM!!iP^0E;@Xi%P-As1g;g&-\'F!!$D5k+93M`!$D8+rr?F,5Q1Xj!.XtJ?i^6)!!!$!qu?]ts7cQo!WVop!!E8j!!!-$huE`^s53kW#QMR>!"]+F!!",@J,fQks*t(L5Q:]`!\'gJ`!!%NJ!!!"Kqu?]ss82is!WVop"p+c!!!WQ*n,NXps6p!m#QN]^"pb1D!!Wu6^]4iTs*t(Z+9-ik%R9sn!$4B)!!"\'irVup^J,TEJrr<#us8N&6J)EQL&+Bhn!VcZm!\'C5k!!<3$z5Q1W_"8mYa!"\\uln,OR*5PP4#pcnZV+8A(u!\'g6Cqu@i65Q1X)pcn`X#P^O_!!!!`rVuou5Q1W_!\'gG_!!#7_!!!!`rVup?s8E!#r]gA^&,\\Zk!\'g6CrW#1X5Q1Y4pcn`Xs7ehX!<;gYrW)un5Q1Z_pcn`Xs7ehX!<;gYrW)un5Q1Y4pj`8CJ,Ffq!\'gD]rW"&?^]+9=s$-PA!;HNo!<<)7!!",@^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(_>F9<s2Y.i#QN-M^^\'nms54.^nGht_s7$\'X#QN_3p]piWJ+s9Ki.(M,s1j-^#QMShr!38;5Ptcd^d%`%s1gks#QMS(r!38;5Ptcd^d%`%s1gks#QMS(r!38;5Ptcd^d%`%s1gks#QMS(r!38;J,BQO^jl7es58D%#QN_3p]piWJ+s9Kn:0p4s7$\'H#QNHVi",k4s1n[7a8Z,>!!)Kgz!$D1?!<,3u"8kCA#Q-gU&,77A+8?rQ5PQ>u5PQ>qJ+t,\\J+t,\\J+t,Ts7d\\Os7cQos7cQos7cQos7cQos7cQos7cQos7cQos7cQos7cQos7cQos7cQoJ+s!tJ+s"\'J+s"\'5PP5\'5PP5\'+8c+`&,ZFs#Q=b^"9&D<!.U%0!!hE^!!3-"J,fQks*t(L&-%.[!"]*[!!!9(J,fQSs*t(L#QK;S!!iOS!!!9(J,fQSs*t(L#QK;S!!iOS!!!9(J,oQRs*t4OL];l8s6\'E4+9!YfJ04\\Js+!?3+9-jUr#brhJ+sQSJ:I>)s+#Uo&-%1[p^dCTs7d-)JH,BTs+(.E&-%1[p^dCTs7cj!JH,BLs+(.E#QK>Sp]phLs7d-)JH,BTs+(.E&-%1[p^dCTs7d-)J:I>)s+#Uo&-%00p^dCT5PuW\'J3WrRs*u3h2ueC=r\\skm#QJH:^]XUls82jZzz+8c*=r]bo8r#ai%r#bD=r#b\\Up`KDup`KDup`KKbp^d@Rp^dCSp^dCSp^dE)p^dE)p^dE)p^dE)s8W-!p](<op](<op](<op](<op](<op](;Dp](;Dp]):`p])@"qu@d&quAo&quAnkquAnkrW#%_rr@9Es+\'S=J)c%Z!Up\'hz"96.:+6WD!5NDYAJ)gM.s5X(Zs24g:s24a:s24U6s24=.s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU:s1eU>s53k^s53nWs8RTLz!!!!0huE`W+7K7Pr\'0ZNr]gGP"8j8$n-Ak5oC*:g+8at<r"&T\'+8?BE!$CtHquAtV&,lPnp^d?(5PPcg!\'g5hrW#1X&,lPnp^d?(+8?BG!$CtHqu@9&&,ZD<r#b\\6#Q,\\5!!3!>huEb+5C`_6GPD.<"5j.Z!!hE^!!!Pf!!!!0p](9o+92B!!$D7@qu@i=s8N\'@s8W+L&-)\\0J.M\\[s1em>s8Tk8s8W,7!$D7@^^oo:s1gkW!<9ia^]=DMs1eVa_#JobJ&))7!.TP!^]8ias1eX6!.VcaquAt>!VcX*p]nS7!<;rs!<<)7!!!Q0^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(^]4?>s1eU7#QMR>!!iP>!!!9(_u9W@s3L^q#QN]]^^\'o0s54.^iW%g@s5<qH#QN`^n-B!/s6p9n_#O07s1n[0#QMU>p]pi7s7cj!_#O07s1n[0#QMU>p]pi7s7cj!_#O07s1n[0#QMU>p]pi7s7cj!_#O07s1n[0#QMU>p]pi7s7cj!_#O07s1n[0#QMU>p]pi7s7cj!_#O07s1n[0#QMU>p^dD_s7h*Dr;ZcsGQ7jF!!iN(#QK;Zs*t@SJ-Z+)#QFc+rVurnzzzz5Q?6Es*tX[J-Z+)#QK;Zs*t@SJ-Z+)#QK;Zs*t@SJ-Z+)#QK;Zs*t@SJ-Z+)#QK;Zs*t@SJ-Z+)#QK;Zs*t@SJ-Z+)#QK;Zs*t@SJ-Z+)#QK;bs1f0F_#OH4!$2+?J%u\'ahuNf8!WV\'Ys53qXhuNf8!.Vca56(Z`zzz!"],!"97iks6p\'hn,`RY!WVWis6p\'hn,`RY!WVWis6p\'hn,`RY!WVWis6p\'hn,`RY!WVWis6p\'hn,`RY!WVWis6p\'hn,`RY!WVWis6p\'hn,`RY!WVWis6p\'hn,`RY!WVWis6p\'hn,`RI!WV\'Ys53qX^]FJN"93lRrr<<\'!!i9!+2@jV!!*\'!^]4?7+90+V!!!9(^]4?7#QMR>!!!9(^]4?7#QMR>!!!9(^]4?7#QMR>!!!9(^]4?7#QMR>!!!9(^]4?7#QMR>!!!9(^]4?7#QMR>!!!9(^`WIS#QMRAhuF#^^]T)e#QMRA!!!9(^]jc=#QMRJ!!!9(^_d%O#QMRn!!!9(^gI-B#QMTt!!!9(_;G:n#QM^2!!!9(a7oW7#QN-F!!!9(chmbC#QN]Z!!!9(s8Duu#QOi\'!!!9(hu<ZV#QN]]!!!9(ci8Lq#QN-M^]4W>a8`pT#QMjEhuF#^_uJWp#QM^An,N^n_>j!)#QMX?p](R!_#O00#QMShqu@9-i\'72@s8W\'\'s+(.LJ3X\'a&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*tX[J.M[1&-%.js*u3k_#OH0zz!!!-#!.Vca5Q?fEJcG3>&-\'EE_uKK3#QM.1k!/bD#QNc_j<+@$#QMX?r#bn<#QMU>p`KM9#QMU>p`KM9#QMU>p`KM9#QMU>p^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)#QK>Sp^dB)&-\'HFp^dB)&-\'HFp^dCTs8Vlort#/!z!!!!$quAt]O8f1js1eTL#QM.1^^\'nus54.^_>iEus2"a)#QMU>n-B!/s6p9n_#Nm/s+(.=#QK>Sn-AuDs6p9nJH,*Ds+(.=#QK>Sn-AuDs6p9nJH,*Ds+(.=#QK>Sn-AuDs6p9nJH,*Ds+(.=#QK>Sn-AuDs6p9nJH,*Ds+(.=#QK>Sn-AuDs6p9nJH,*Ls1n[(&-\'HFq#CBhs8N\'!z+8u6?!<+(U!!E32n,N^k&,6,8r!3-"+8cBC!\'g5`rr>:Y#QFdRp]phLJ+s9KJ:I>!s1n[0#QMU>p]pi7s7c]r_#O03s1n[0"961:p]LQ3s7c]r_#O03s1n[0"961:p]LQ3s7cj!^jl+as1j-Z#QMShp]phL5PPK`J3Wf6rr=/9#QFc7r!33$#Q+i)!!E-0p](?o&)[Ef59GCU!!D]j!!!!"quAt]L]7>bs.B>,#QKqdi!9:ds54.^i;`9Os5<qH#QMShp]pi7J+s9K^jl+as1j-^#QMShr!38;J,BQO^jl7es+#Us#QK=(r!37PJ,BQOJ:IJ%s+#Us#QK=(r!38;J,BQO^jl7es1j-^#QMShp]pi7J+s9K^jl+as1j-Z#QN`^n-B!Os6p9nYlEVds,m>s#QL:nJ-Z+0rr<<(JFEODs*t(L#QK;S!!iOS!!!9(J,fQSs*t(L#QK;S!!iOS!!!9(J,fQSs*t(L&-\'EF!"]+F!!#7`n,NFgz!<)ru!!E7Vs7d-)kPr=>r[7`]+8e(tJ3WrRs+!?3+9-k@p^dCTJ+sQSJ:I>)s+(.E&-%1[p^dCTs7d-)JH,BTs+(.E&-%1[p]phLs7cj!JH,BLs+(.E#QK>Sp^dCTs7d-)JH,BTs+(.E&-%1[p^dCTJ+sQSJ:I>)s+#Uo&-%/Er#brh5PuW\'J04\\Js*tXZ2ueC5s(D@^"94/VJ,h\\:s*t(L#QK;S!!iOS!!!9(J,fQSs*t(L#QK;S!!iOS!!!9(J,fQSs*t(L&-%.[!"]+F!!!Q0^]4@!s6p!gz!!Dur5Q?fD!"]+%rr<T0^]/fhs5X-0#QNc_J-Z+js*t@S_>f#js2"_c#QMX?!!iOTrW!3\'JbT3Ms*t(L#QK;S!!iOS!!!9(J,fQSs*t(L#QK;S!!iOS!!!9(J,fQSs*t(L#QK;S!!iOS!!!9(J,fQSs*t(L#QK;S!!iOS!!!9(J,fQSs*t(L#QK;S!"]+F!!!Q0^]4B7s8Duu!.XbD"5nY/&&:D[++QSk5Caj6It/X!It/X!It/X!s1f_ls54t!s7cQos8N\'!J,eF,J,f9DJ,fNK5QCb65QCc!+92B!#QOh^!WW2h!.Y%<!"],!4ot]QIK4lerW"&0rW"&0rr<T!rr<Sfrr<SfIfLS+5Cai++2C&?#N5@W!\'^G`!!.TM!!.TM!!@`O!!e#S!"XS[!\'bu6!<7QL#QK;S&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[&-%.[#QK;S#QK;S#QK;S"96.:!WV,/!.XtJ!"ZjFz!.Y"Zs55"!"979irr`;Z&,u\\1i",hgs54Ff!WV\'grrN/X&,u\\1i",hgs54Ff!WV\'grrN/X&,u\\1i",hgs54Ff!WV\'grrN/X&,u\\1i",hgs54Ff!WV\'grrN/X&,u\\1i",hgs54Ff!WV\'grr`;Z&,ub3i",his54FfKE\'j?s+C@0#QKSZi!9:;s54"ZmJl)Fs7u]a!<;ThrW!H/z!!!"Ks1e`p5Q:]a^`WRV!Iu9l!!.T\\rr<(M&-%.\\!!iOS!rrT+^]OQAs1e[9"96.@!!E8Z"onc*huj#\\s54:c!WVWt!!3,h#QOl)n-B!os7dE2!.Xb\\!!%ND&-)][r%J*N5Q!28!\'gB(!!#7_?iU0Kra5^++9"M*!$D6V!!!Q0^]4?Fs*t(L#QK;S!!iOS!!!9(!!!!$rr<$!z!!%NKJ.DVj^`WRV%fc]^+8u6^J-,c^rr=-k!rrl3!$?^m!"])0+2A\'\\#QFcg^]jcDs+!>l"98],J3Vrp!!iOSJ)C_8"93n$n-f:!s1j-R#QOu,_#Nm@!!3,8s7dE2!WV*Xp_Wu3s5:Ze&-)_1iLg$%!!*&XTDUAC!<;R2r#bt>s76d#+92Cko+1h.!!%N>&-$#;!.XhMs$-Pa5Q1of^]4@!rWiJ=!!#7]"93lO!$D+@s*t(L+8c0>J,fQkp]:DF!!",9!WN-"!"\\i)rr<$!&,6/)zz+92*@qu@!%n,_GI!WVWh^]4E8n,\\%>!<;NhJ,fS!p]CKr!.XnN!!!!`r!WQ*!$D1G!!!!@rt#/1!"])`!!!!(s53kW!!iP>!!!!$s1eU7!!3,X!!!!"s6p!g!!*&gzJ+s!D!!*&s!!!!"^\\e\'3!!=>B!!!!\'+9)<@!"9D<!!!!)#QK;S!#Pt@^]4?g"96.:!+5j-huEbm!WVWh!5JU7n,NK>!<;fo#J^?>quHcsTE"r,z!.Y%,&,77HJ-!G-rr<(M&-%.\\J.M[1!<<B)J-,cVs1e[9"96.@!!E8Z"on](huj#\\s6pEs!WVWp!!*&o(]XR9p_Wu2J+sQT!.Xo#!!#7]+92C+ra5^++9#XJ!$D5+!!!Q0^]4?Fs*t(L#QK;S!!iOS!!!9(!!!!$rr<$!"9&9#!!3\'!!!!\'!zqu?]s!;lfs!!%6D!!!"Dz2uipY!&+BQ!!"\\Q!!!!Az?iU0,!5JR7!!\'e7!!!%M!!!!$z"onW\'!#P\\9!!D-Zzz!!!!`i#hq^!$D2&!\'gB@!.Xo#!.Xbt!<;OB!WVXC!WV(#"96.Z"96.:#QK;S&,uV0&,uV0+8u6?5PtK]5PtK]J+s!Ds7cQos6p!hs53kZs53n[s1eX?s*t+Ts*t1^rr<-CrW!$BrW!$bqu?tOqu?tOp](j)n,OR1s8W*!!!!!0huI.)Dua9*2uqkj$in(^"ouGH#6DVJ"+bu1!Q+nF!.FnJ!!!!/!\'e8Ki.\'\\bi;_a8i;__bi.&NaJ,fQL!!!#7!!0mn!!@aj!!`K`!"JuK!"8i;!#P\\@!&+BTJ7&?X^q]pMiICn.ErZ1?4obQ_)uos=*WQ0?2ZNgX@t4OZ_8$$OJD^D0!,qoB!&sre!#ttU!"Ju_!!`L3!!@be!!0k8z!8n(^!!!,r+2@jV"8j8!!!!-!+5d,!#Q-gE!!!9%5MuMA"8j8!!!!-!+2@jV!Vd2@zzzzzz!<<*!#QOQ0s53ku!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!iP>!"8i4s1eUC!!E8:!!iQ,s1eU?!!E8:!#P\\:s53kg!!*&W!&+BQJ+*GG!!#7Q!5JR7&,ZN[!!!-$rVuou!"ZjF!<<*!rr<$!!<<*!s8W-!qu?]sz!$;2*^jk9li;`<Hn:0qWn3?Can-AFbn,qSNhugasJ-Q&_!,qpg!;k^Oi;;I0i;)=,i:5aqhuE`W!!!&8!!0k8&,6,hrr@QK!<<#urQYEA^]=>K!<9h7J%u%Kn,OR.!!iK\'!WN-#rr<)WJ:ZU.nc&UhrrE)u!<;rs&)[Eg^]4DN!!0k8q"XXZq"X@J!"XT%!$;2)!\'UC3!.4co!;lil!;HQh!;HQh!;HQh!;HQh!;HQl!.4co!.4c1!\'UB)!$;1OJ,fRs!.4c1!\'^H*!$?_%J.I/@J.KF#^^%X[^^%X[^^%X[^^%X[^^n3kJ.I/PJ0+b5!\'UBH!.4bH!!!!$^]V@S^]V@S^]VCPs8W-!rr^%=^]V@S^]V@S^]4@!5!D/XI!g/=s1nZMs1nZM!!%Cqrr.9F!;HQh!Vc]b!Up3\\"5jFB#J^S[&&8^+%tGaP*rmA_4odbHIK4`qHiX\'Ep](9o!"\\Q!+8c+\'quD6G!.K@sr\'(2Z561U\'!;mo=r#^Ia++X,.JG:4:p`G%a*ru3\\!;o%]r\'(1156-34!\'gG_+8c*Ln,NFg!!2isp]pR)pcnP\'pj`\'!pbDOEp]:-jp]:-jp]:-jp]:-jp]:-jp]:-jp]:-i!!!Q!!\'gA]s8E#urr@F2!&-V;!\'^G`56([J!!%HJ!.FnJqu?cm!!D]j#N,Rm^]5I,!\'^G`IK0BJs+(.LJH,Y"s8RTL!!",1!.XnHs8E"Jrr@:n!!#4`!\'^G`4obS3!$D+=+7K7Pp])E8!!*$!!\'^G`56([JJ,he6^cqi!rrE)u!<;rsJ+*F<!!!!`!!%KK!<3$!rr<*"!!E6$"9/?+rr<SE!"ZgE+$T`h56*l3!.7!2pcecYs1n[7_#OGM!\'^G`56([J!!#4`!\'^I5rdXosrdXor!.4co!.4cr^jl-/rdXo,rr>7`56*nJ56*p`J,fNJrr;nGn,NFg!!!\'!!"]&/+8u7)rW#._!.FnJHiO0E!!)ii!<;rss8E#urrE$_!;mphp`G%]++X82JG^L>IQmg^rr>:_!$D+=&,6,)!!*\'!_#OGMs8Tn7s1eUVJ,g[A!$;1@56([I!!%HJ!.FnJqu?`p!!2ip!VcWsn,NR[!!D]j#N,RehuF;\'!"ZjF++O=k!!!Q!!\'gA]J,TFtIfTC2!;o%]r\'(1156-34!\'gA]+8>gXp]*PV!.XtJr\'(2V*ru\'XJG:4:r#Yq<IfOuu!.XtJ+8>g9z!"\\Q!5PP5.quD6G!;q<Hr\'(2V*ru\'X!;IXdp`G%a5Cie6J:ITL5Q:^*hZ*Wu!!#4`!\'UA_rW%0?!.XbDJ+*Gf^]4?7!\'#H,rd57Wz!!%Cqrr.9F*\'\\q&4pV,gz!!#5I5!F@AI!>VlrVuuu!!3\'!"9/?\'rr<0$!!iOS#L@o*c[ZPP^^nK$%u9\'bLYs9Si\'7825QC4;s6tO<pjN8=IKB6A!;u`pr;6Qms7cTorrE*!JH,Y"r\'/!p&&A)R_#+_Yr#^Ihs+(.K!<<\'!s8RWI+2Idb_#+_Yr"$U@&&A)b_#OGMs8RWLrrE)sz!WN-)s54Ff^`WTl5D-a9!!%HJ!.FnJIK0BG!!)os!;lfsqu?`p!!%HJ!.FnJIK0@t!!#66^d%k7+90+es1ea:J,fQLs6p$grW)uuJH,Ybr\'/!p&)d?jnGECXqucHd"7Z3jnGECXqucHd"7Z3jnGECXr!20X&)d@M_#OGMs8RWLrW)uf!<<&urr;utrqlco!;lip!;lisr;Z]pr;Z]m!;lip!;lip!;lisrr;utrr;utr;Z]pr;Z]m!;lip!;lip!;lisr;Z]pr;Z]m!;lip!;lip!;lip!;lipz!<9h>s6pR!n/q\\g5JZ2AJ,k\'!!.FnJIK0BI!!)p]nGGN?r\'0]K5Oa+(n9tK/IKT(h"7SO-n3?sB+91g@s6p-j^]4?7qucHd"7Z3jnGECXqucHd"7Z3jnGECXqucHgs7$\'gnGiOXs8VTd"7Z3jnGECXqucHd"7Z3jnGECXqucHd"7Z3jnGhGHi;__b^cqf`!\'^HJ!\'^HJ!\'^HJ!\'^HJ!\'^HJ!\'^HJ!\'^I5JH+R-i;_^?i!80Fi!80Fi!80Fi!80Fi!80Fi!80Fi!80Fi!80Fi!80Fi!80Fi!80Fi!80Fi8<Jm_#M4M!.4eE#N5Lji;=\\4r#^Ie561V1!;ufrrVQZop]1?`!<;Ngs6p$gp]1?l!<2lrr-eYDIfTC2!;o\'3r#``P&&A)Ri;<i<quHWpquHWpquHWpquHWpquHWpquHWpquHWpquHWpquHWpquHcrs8N&ts8N#u5J[:!5J[;LJ&))7J&))7J&)*"s1nZMs1nZMs1nZns1nZns1nZns1nTnn%ennn%ennn%enncbTJYcbTJYcbTJYO21[CO21[CO21[C&&A*-&&A*-&&A2Fr;Qcps+(%IJGfG_r;Y^Qs5<hPnGN=Ur;HEgrV6<gr;?Klr;;$Ar\'1,W5Q(F$r;7Z7r"&`\'&,c>1r;6Zpqucis!!!\'"J-Z,4+91gPs7eg2r-nbFIK9:p!<.EIIf9=rquD3D!.OhGIf9=rIK4hG!<.EIr-nbF5D/kUs7d]9n-B!O"93lO!!*&g!<;rss8N*!rrDs]JG^L>r#^Ie++X82JG^L>r-s7srrE)u!<;rss6p$d!!)os!;lfsqu?`p!!)os!;lfsqu?`sn,WLd!<<\'!s8N)s5CiYRJG^L>r#^Ie++X8RJH,WLs8E#uquHcl!;u`pr-eYDIK9:1!;o\'3r#^Ie&&A)Ri;<i<!!!Q)5Q?64J,]EequHWpquD3HJ&";<+8?BE"9&<#!\'^HJJ3WOQs8N&ts87B9!!*\'!_#OGMs8Tn7s1ea+!!D]j"7Q9mn,NR[!!D]j"7Q9mn,NR[!!D]j"7Q9mn,NR[!!D]j"7Q9mn,NR[!!D]j"7Q<g"7Z3jnGECXqucHd"7Z3jnGECXqucHd"7Z3jnGECXqucHd"7Z3jnGECXqucHd"7UaEn:(]$J,eFks1f`VJ-Z&R!!!#s!VlQnq"t0fHirke"7UaAi\'%D(56p+2#J_Dl^`SWQ+-1p_T7@I0J.LN;#N#Ldrr<<\'!!E3#"9&9&qu?cq!!2utp]nSur"%_7r"%_7r"%_7Hk5._INS(WINS(WINS(W4s0:h5!Jf;5<eo<5<eo<++F%T++/M++8gWX+8gWX&,:Y4&,8BI&,8BI&,8BI#Ojsn#OihN#OihNrW2eC"7UdBn3709+,AbrcbL(KJ-Z+)#QFc+rVuuu!!2ut"9&9&rW!3\'!"[t;&)VmZO2*sbi\'.J9IKT*="8Mcpr;6ZdqucG;#N1%9i\'.af57bOOT7A#U!"])0#Q=].rW!&u!!E-!!VcWqp](?i!!2ip!VcWqp](?i!!2ip!VcWqp],gD^jlC"J,d<6s1eUVJ,he6!\'^G`IK0BG!!2ut!VcWsn,N^_!!hE^&&8/eJ,g[A!\'^G`IK0@ts1n[7_#OGMs8Tn4!.Fo4!$;1OJ-Wjpn3?h8r]gE"56)c**s_g1s*t(J+8d5Y+8eA&J,fOumm#+uzqu?`p!!)os!;lfsqu?`p!!)rl!<<#us8E#urrE$_JG^L>r#^Ie++X82JG^L>r#^Ie++X82JGqc`s8N*!rrE)u!;lZo!!!!$n/qWordXiq*<#s9!;lip!;lip!;lip!.G?+r\'1*Dr"&]*z!$?^k++O>5J,g[A!$?^k++OUBJ04fA5Q?7`s+#S`JGpX@r#^Ie%tOQgJG]q.r"">U%tOR"JGpX@J,b%Ks+!?6J0461!!!!$n,OR.!\'gG_J,]Lt*ru3\\JG^L>s8RWLs+(.LJG]BIqu?`p!!%HK!.PLZ5Q:^*rr<<\'z!!!9%&,[OI+.+.#++PG`J,\'\'=s7d[d++PG`++PG`++PG`++PG`++PG`++PG`++OU3!$D5k5Q?7`s+#S`JGpX@r#^Ie%tOQgJG]q.r"">U%tOR"JGpX@It)uus+!?6J04fA!$?^k++O>5J8d`\'J,]LurW%HG!"[uf!!!#s!!)os!;lfsqu?`p!!)os!;uTls8E#urrE*!JH%iarZ?[g++X82JG^L>r#^Ie++X82JG^L>r#^Ie++X82JG^L>r#^Fhr;?Kj!!!#sr;?Kjr;?Kjr;?Kjr;?Kj!!!8^#N,jF#N,R^z#N,jF#N,jF#N,jF#N,jF#N,jF#N,jF#N,jF#N,jF#N,jF#N,jF&)dK\'s1nYbIK0?J!;lfsqu?`p!!)os!;lfsqu?`p!!)p=JG_V3r-eYDquH]j!<;Ngs6p$ghuNfH!<;fos82lpquHYD!;q<Hr\'(2Z++X82^]=<1r;?Kjr;?Kjr;?Kjr;?Kjr;?Kjr;6Qi561T[s1n[7s5<qWs5<l@a5Hq=LZ&(PKCJd\\KCJd\\KCJd\\KCJd\\KCJd\\KCJd\\KCJd\\KCJd\\KCJd\\KCJd\\KCJd\\KCAm9!;l`qs8N*!s+(,6JGpX@r#^Ie++X82JG^L>r#^Ie++X82JG^L>r#^Ie++X82JG^L>"7Q:4quAt\\!.Y"KIm8J_++X8"_#+_Yr"$U@&&A)R_#+_Yr#^H<++Sk@J3X&6+8u6Np](9o!!)coqu-TqrW)uu!<,35r#^Ie++X82JG^L>r#^Ie++X82JG^L>r]br5rrE*!!<<#us82lp!!)os!;lfsqu?`p!!)os!;lfsqu?^%^]5JVJ3X\'aJ,b%K5Ci_TJG^L>r"">U%tOQgJG]q.r"">U++X>4J:E\'!J,b$`s*u3[J,g[A!$?^k++O>5J,g[A!$?^k++O>5J,o*9nGi"XnGi"W!;lip!;lip!;lip!;lip!;lip!;lip!"\\!Pr."YEq#!,L!<)uu^jkhqp]p]tquHYFr:\'Xar;ZQlhuE`W!"T&?!$;1_!.XeDq#C+2!$;1_!$;1_!$;1_!$;1_!$;1_p`K8Ap]pQozr#^Ie++X82JG^L>r#^Ie++X82JG^L>r#^Ie++X82JG^L>r\',`3s+#V!J:ITL+7F^[z!;mACr"$Sj&&<W9J:8Sj59Bki56)ci!$AoT+8u6NrW!K,!"\\u-#P\\9(p](Ek!!D]jzr\',hlr\',tpHp>[0IQtlgIXfDR5(Cno5\'ub65C;jL5Pso"+8Pqe+7]@2+7]@2&+TZ"&+KT!&)dEe&)dEe#N5R]!!!"J&&<Z:J3Q8K+27dtrW!K.!!iE%#P\\9(p](Qs!"]&/+8u6^^ApJ_J:AYkILj6l&)[Ef!;mACr"$Sl&&<W9J:8Sj59Bki56)ci!$AoT+8u6NrW!K,!!iE%#P\\9(p](Ek!!D]j"7Q9mn,N^O!"[ufJ%u&6J,k\'!!.4bH!!%NJJ,Xrs!;llm!Vccd#N,jF&&99;56*nJJ,]KIs8N&t56:f)s8W-!_>XE7I")(oHiO-HE&dW?r;;\'>5O]cQ&&9:F5Oa0tr;?>=E\',6[!!!!0T)]DZ!"Y\\%#EAcaz!;lrgqucHd"7Z3jnGECXqucHd"7Z3jnGECXqucHd"7Z3jnGECXqucHd"7Z3jnGECXIL#@l#N1+3i\'77W+9-irrVuou!!!$!r;Z]pqu?]s!!!$!s8W#ss8W#ss8Vus!!!"JIXHNjq"XXap\\4FVpBL[\'!$C-Kn:0Br!.Ouu!\'buUi!8`VnAk%unGhEr^]siE!!!#gnF5r:n/`W54Eu*qE:EAdn8NVsGW\\)0!:Y5X4?OZ+*Zc@D*Zc@B4?Rk5!!!!(!!`K/!!`N(nGht_!!`K/!!`K/!-ia5Gjt2&rr)ltnG)JQ#Cm&0#Cm<b%fd+?*WR5]49.JD490U+GQ;sgn,VqX++QSkJ)GVAGjtLtq!e(Jq!e(Jq!`OtH16=A5N!X!!!!7S++QS+It7QLDh&@K%tG1@%tG1@%tG1@%tG1@%tGaPJ)L@rEUWtt!:U$I"5jF"#Cm<b*WS;&J+3L-s6q+\\J)GhG1%555!T4(<++PHk"7Q<[!:U$YoC2e<J%u$a!T4(<#N,jF&)\\Pf*T0*=H/N]#s7lWhs7cWQ!T4":s1nZMs1n+(n,VqXs+(-bs54";!T4":"5s3ps1nX7!!!8^+5fBAHiSBkGQ@cZs5<kFq!e(Jq!`OtJ+,\\\\+2@jVs7$\'Xs6p$X!T4":"5j9s#J^Rp%tG/j%fd[O*WSA(++QT6J+.^PGjp.>5N!W65JVd,Gjt4lnF1_mJ)EQ,!!"*k5JVd,q=+1KnF65Bq=&n\'5O]*N!:U$IBAe9TIfKHK!:]dQz!!)N`n,NH5I!>VkzG^+IXnF-[u#N--N&)[uf*q16?5\'T275PTa+J,FORpceHon/q[\\s7$\'Xq"XXZq"XaUs5<qHq"XW/piuT/s7lW`s1f0\'+8A(iHnb<qp]0d`n,VqXn,VqXp],O=J+,\\l+7K71s+(.-s7lBapjDj!pcS=6pcS=6pcS>!q"Xmas7$\'(s5<q8s5<YPp]1\'hs1nZMs1nC0p]1\'hp]1?Ps5<q8s1nZMs1nC0p]1\'hp]1?0s1nZMp]1\'hp]1\'hp]1\'h#Oii15PTUCp]1\'hn,W(XoDJ4Xn9k"YI!gGA5PuVu!!)dVpcS=6pcS=6pcSTSs8;oppcS=6pcS=6pcS=6pcSTVIlohU4?P_g4?P_is8O/_+!2RH+!2RH+!2RH+!2RGrqu9\\I/*L3nG2SNi;^UmJH(0"JH*F^i;)=,nG)eRq"T73!;HQh!;HQh!;HQh!;HQh!;HQh!;HQh!<;!Wi;_a5#Jg6J_#=k[rXZgD+2Imu_#GLlpHQIf^VKTU_"[`AoD?>po>\'th_"%$3n`.F_*rI)Y*rd;]*rhi+T(h+5hXga:rp]pVrpYC+IdfN3i\'7!dr-U^\'5562g+7LBA+7LBI+8?n)5(EJpp^cio!<7TLi;`<BnG)MJnG)MMnGhGH_"[p)!;HQh!;HQh!<3\'!i;`<BnG)MJnG2SRnGhGH_#(qCi;)m;nG)eRHp<.2i;^U^_!h?n!;lhH!\'buE^]WKsi.Ktf_#M4M!!!$!q#C-hp^_lcJ.I/@J.I/@J.I/@J.I/@J.I/@J.I2*4SV&64SV&64SV&64SV&64SV&64SV$`I"1oUp`JDo!:W2A4SV$`I!Bm`GWba`n3$1]n/pR1i"+`V^^n3c_!lSrnG%7tpiuT3G^943H2R/Wr:#!gn3>e!5MtB`ceq$Ki#e$<+-42ZLVOu:_"^*<4FDB9p`AoHn.4Ff^^n3ki#gl@n3$JnI/&*Y54C]0I!Bm`n3$2)i#gl!^^n3kJ-UT0J-UT0J-UT0JH,EEq#Bgan,_GL^^%XcJ.DW%!\'UBF!.4eHq#C-hpinnB%fcSo^d$a;n,VqXn3?Dkn9FHtn9OMQn3:jl!:U!X!:U!X!:U!g_#N?knG)MJnF5rBnG)MJnGi"Xi;^Rm!!!!@i\'6.L^j#j(!-eM=!-eKg!.Woki#f`7!!)cop]1\'hp]1(2pcnP\'piuRYGkcOYG^+IXpjMp%p`F_\\!!!!@^d$b)n9FGIpj`)=pild`!.8`Mn/q-"!"XTE^d!?3!\'C72JH(-^!\'C6D!\'C6D!\'C6D!\'C6D!\'C5]!$Cu#pj`\'`piq%.GkcN.G^0"3pcnNqp]1\'hpi5eQn:/4R!:U!X!:U!X!:U!gi;`<FnG)MJnG)MBnF5r:nF5r:nF5pdq"OghnF5r:nF5r:nF5r:%Ncbm!$31&*Zc@D*Zc@D*ZcB:rqlcc!:U!X!:U!X!:]LJi:Gn$_#Jrb!<7TL_"6LSi:6=+q!deBnF5r:nF5r:nF5r:nF-DX!<;N\'s8V$Us5<_Ci:uj#q!m;3n_ip,i:-9pnF>H+n_ip,huEcWi;`<FnG)MJnG)MBnF5r:nF5r:nF5oI!$B!@n:0qPpiq%.G^+IXG^0"5n3?Ca^]4?7!;F;/i;N0?nG)MBnG)MJnG)MQnGhGH_!h?n!:U!X!:Tsg!!!!@pcnP\'piuRYGkcOYG^+IXpjMp%p`K82p]1\'hp]1\'hp](9o!;D$DJH(/t!;HQh!:U!X!:U!X!:U!X!!!!`^jj.F^j#j.!.TM@^^&d"i+\'QP^jgk7!#tu$!\'C72JH(-^!\'C6D!\'C6D!\'C6D!\'buuJ00:A!!!#gnF5r:nF5r:nF5r:nF5rCnGi!-n3:jl!!!#gq!deJn9OMKi\'$!_i\'5"!^`S(;J.I/1!!)QZi:6Esqt%UMqnRRU^jEi35JM_5^OSO5J3P+U+!1J)*rl9@q"T.(IGd?J+2AtK++PHK5N$tJH1:V(!!)N`q!`OtH167?4lAQ_+2Au6++OlP%tG/j%feforW)irzs1nZM"2G.l%tG`%*WS;&HiSZSs5<q83"UQns7!qa!!$Erq!\\8kJFUGP^jgl!!$;2*J:GB+i*jD$!!!!?i#gkchuEcP4SV&64SV&64SV&64SV&64SV&64SV$`I"1oUp`JDo!!!$!i;_^8zs8W#ss82is!-ibXnF5?9r;>@*!!!E-56-1`r;c`qHiQA2%tG1@s+(+L$ig\\9!8ueN^]6?5E,aani8EP_E,[cr!,um:3&ilW3&ilWE,a_T!#ttY!#u"=J/eP/!#tt=!,uo8huEcPp]0f&!!!KK*\'?2?E,]dSi#D`H!-\\G;JFe<OJE)1OJG4S<J:@P_z*^9R@%LrsY%Lrsg!.P"CJ7jB;J-Q&b!$2,&!-eMDJH(->!<3%CJ-UT0!\'UBI!!e#ZJ;8[T!<)ru!!!!0!$;1_!\'^I-!-\\G+!<7TLJ-Q&Z!!!"K!.Ouf!,qpf!.TM(J-UU[JH#WK!!!!(!\'^I.!,qqr!<3\'!JFe<_JFe;@J3O#6!!!$!JH(-)J-Q&b!"JuM!#tu$!&ss<!#tug!;D$<J9LuW!.P"CJE)1?JH(.L!!!!=!.P"C!9\\mmJG4ToJ:E(OJ-Q((!.4bH!-%FHzn8JAHn8J@-!!$tWi8=S8!$;1_!\'buqJ3/:.^jj.L_"$@Qi8EMn!<3\'!JE)1CJH#WLJE)1?JE)1[JH#TS!\'e8K^j#iu!:U!X!:Tu-!-eK.^`U>l!!!$!!<7T0^u<)f^u<)f^uN5n_#Jra!!*\'!i8FV6i8EPnrrE&ti8EPmi8EPOi!4cSi\'5#%!,qr-!;GDqi,R\\#i\'6-AhuE`W!9(`P^u<)f_#M4M^u<)f^u<)f^u<\'/r-3I2G^+IXGl7I>*#oq<*#oq<*#oq<r:g6l!98UmJF<L;!;lir!<)ue!9\\mqJE+EFi8EPOi8EPOi;`fW!;Lg6q"XXZq#1!dq#._k\\F6rr39N7$!;PLIi;DO2i;V[&i:#Uei8`bUi8NT!!\'e8Ii-=a1E:@i9E,]c8n9FFei#f`7!!!$!!<7T4JEMIGJH#WK!8mk8!8mk8!!!$!!<7T4JEMIO!<3&u!:KpN!9\\mm^`3?(J:@Rg!:Tu9!\'^Go!!e%pJH#WKz!<7TLJ/eP/!#ttY!#ttY!#ttY!#tt=!9(`P^u<)f^u<)f^u<)f_"5?kJ3O#6!!!#Xi:4VQ^iR;<J3/9GJ3O#U!$;1^!!!#Zcf<=Fc?IQXrce9hr\'($BHp2d;GQ7a6^jEjYJ3O#U!$2,)!\'c!\\JFgS8huEcK^iP$UJ3O#u!$2+]!$2+]!$2+]!!!$!JH(-)!"T&N!#tu$!-eK_!<7TLJ,jOJ!\'UC4J-UT,J:E+@JG4ToJ:E(L!!!#W!8mk8!<)uu!;D$,JEMIGJEMI_!<)ru!\'bsSnF5r;Im3o5!!@`RJ-1<dJ:E)jJFe<_JFe<_J:E)6J,fR5!.TN?JFe<kJFER.!.TM`J,fQL5(7a*rci[4G^+IX5Ce66F+Ek4o76F_o72=@5C`id6\\\'Z:IK0?JhuM[8huN`VrrDeDkCD`GkCD`GkCD`G!8uc8i8EPOi8EPOhuF`:!#usu*#oq<*#oq<r:g6lhuM[8huMqjmf<=equHWprW)Bek5a[q!8ueni8EPOi8EPOi;WNOr:dkeSEHF*SEHF*SEHFA!<3&nJEMIGJEMIGJEMIGJ3Es_J9-84_"5A5^iP$UJ3O#6!<)uu!;D$,JEMIGJEMI_!<)uV!8mk8!8miAJ:E)jJFe<_JFe<_J:E)6J-1<(J-1<(JGf??i8EPOi8?fuo([YU&-)V/0Q;L?E,]c8E.0tNkCD`GkCD`GkCD`GkCES_It.M!j1s]*pOIGfG6!*m4odbH*!#/lkIgi)J%1"\'J,"H]4RbK&o72%8IfMY4*WSA(IfO\\Co75l:o76RcG6!*m56*kI4ocW()ur)$p]0d`s8NQK4EtiFs*9.pJ;4,Dn8JBImX.!Am`%Hk56(Z`!!(uniP=EfiP=EfiP=EfiP>\'#It0``!!!$!rr<\'!s8W*!nDN4)!;ubB!#U1aq"R#ohYn?/!8udC!!$tWi8EPOi8EO4Du]mrE,[Kb0JIHbE8U^5(`<5h(`6Z=i4o?^!8uc8!$!sX0Q:u=i8=T_mdBN*md>OO!!#-/HlO+G*#opuIdR[U*&qp;rrE%9%X`X6%fZA+!$31FIW!I2%LrJf@,Ut^%M&L9!!#3%i;W`<k5K`.!<3N=*#oqX3,ekHmd>IMmcNqb!!%E7mdC(\'%UOA[!8uc8!!(s8!!(s8!!!",i8DBN!\'C6F!\'UC,!-\\Em!<7T0JE).[rpK4RrpK7SquAs&E8][4E.:(P!<2HMkND$krqlcoi8FP2i8FP2!;td5i;DNki8=S85Ce"ZDueermssGKF+Aaj5C`_6!9`P.s8V9FkN;j?E,]c8E,]dk!&uqt3&ilW3&l0PhuN35r:p\'brpJqLi8EPOi8EPkqu?`ei:Gmui;;I4i8<JLi83DKhuEcKJFe<gJGXlSJDYn\'JB*2\\J,fR6J9-82^u<)f^u<(K^jgl!zr;Q-PrqPF0huN]SmdC#Nr9i_JIcfR54<>"3qu?`s3&ilW3&ilW!9`P.kND$ks*aqJ!98Um!9X?+!.Fos!\'UBF!\'C5]!9Z?13:ChTn:0qUn9s5?i&T]q!9X?+!.Fo3!\'C6F!.FqB!98S0!9X@V!.Fo3!\'C6$!#ttY!#tt=rsg(i3,ij:s6q]B!.JeqIdZWQ!5QCcr;Q-0mf*+a!.ORui8FT`!!``6J,e]pkPp#3!.Oq1s58\'L!\'GXJpi(1kE,]arJ,e]pkPp#:DLMT$^qfm9m`s,\'c<t#[?smAM?sm@r0E<d\\0JG170JN"c!5QCccJ83ir7oT5^qdb$^qdb$^]4B7i;_a\'i6L9+i6L9+huN]Cm`s,\'c2`=nkND#XIK0BGrpJ)"rqsRI^]4@as6&S.s*k7Y#64c!pu&s\'^q]qtm-oBBh#%.kE;XZoE,^2P!!)3FkND#XIfKK3md>OO4?*<@mbmQls58CBHbb!D42:jaIXF8*Id[:"mV[K$4?,=qn,NId*&oosi;@WpJ7.;#!:G4oHu8q5HiW?mkND$kkPou2!;lfs!<;fo!!(s8^]<$>f[p0@)#r7@pj=/&)k[*H(]_@e^q]pM3&#;Zi8EPOi8A!NE%i+/i,EWh3&ilW3&ilOE+%T(!"8i9!"8l-JH(-.!"8i9!!!"<?sqmm!;HNoi8=S8$k+*m3&iU2?sqp.!!#4`Er]^#@=[<eiIKm;iIG?e@t8V#56(Z`!\'GZ,*#oq<*#oq<)uotg!+UN]J-1<(J-Q&Y!"8iE!&+C\\!<7QL!.OuYJ-1<(J-,d8!!`K+J,t0$JAZp;z!!`K7!"T&K!\':0:!+Q#h!<9h:!!<3\'!!*#V^qdbb#6P&5L].8R!$;2#!,qpG!,_f:JDl%;J73t:J9-6*z!<7QMJ-1<(!!`K.!"Ju;!#ttY!#P\\q!!!!`!-<[#J7F+R!$2,i!+UQ<JDl$"J3O#6!!!!`!-<\\NJDl%;J7F+ZJ,t0&J-1<,!.FnJ!!(s8z!8uc8!,ulWzE+%V>!!!!/!"JuN!#ko"!\'>]cJ:G@C^u3#di4r_#!<3&ZJDl%;JE)1Z!98UgJDn<&^uKtF!!!!`^i4h^!8mjm!5JTM!5JTm!8mj%J3SPa!!!$!!98Ug^u4//i8EPOi8EPO^u<)lJGoNKs5;hni;_`ni8EPn!<;!8i8EPni8EPOhuEaA^i7*I!8mjm!5JTTi5":/i8EO<i\'6-"!!!#W^u3#d^u3#d_#M4.^u3#d^u3#d^u3!.r%KfY0JG170JG3Y!#usu*#oq<*#oq<*#ogj!!!#ZJE$Xl!:Bjb!;HQl!:BjL!9X@BJDn9Di8EPOi8EPOi8EPn!!)LJn9FGIpiuT/r7Lu#m?m@0kEtELk841!i8F+_pu(r*r8@#$mbm9dj5AtUiS`YP!!#66EPUMji*a?>^i7).^i84>i8AUj5C`_6!!)uuk5aOmj+-0?k5bJ]huM[8huM[8huE`WrrD54j+-0?j+-:mrW)?dk5aNBj+-+(!!#66E<\'AH?iY-G49,ll"+UK("+\\:>rr<$!!!*&7)uprY)uprY)uprY)uprY)uprY)uos=i5"9di5"9di5"9di5"9di5"<eF21!?z^qemDiP8lPF+?&s1B9W>*rm>^*WQZM!!\'olj2^3"B?"TPG4\'Ni5&<?/4?OTC*&mouiP9Mb1B9W>*WR/[*WSD)1B;KH@=Z20!!(uniIH!"Er\\E)*WR5]$ig\\9$ig\\9$ig8-s*t3%!rrQ+%KHn;)uqqu0E?%lhuNem!8qfU!!%KK,6.gr"+YlOj+-0?kCA&4!!\'e7^];.M^]=B7irJ+i_goXTj+-0?k5bJ]!!!!`E+%V^i*^Oh!!0k9^]D4O^d#VU^gY%;^u<)f^gY$"^d#U7!!!!`!-<[!JDl%YJ7&@b!-*NRJ,fQL4tpqpr,?UoE,]c8Du]l&^iR;"^u<)f^u<(;^iR:U^]D4OJ7F+Z!!!#7!5JTM!5JU7!94(>JAZoTJAZoTJAZoTJAC(C!5QCc^qdb$^q_W`!!"],0JG170JG170JMtr^qdb$a3NK8q#&FWa2#L+^qdb$^qdb$^q]pMrqPZHiuGrF_[OEk_[OEk_[HMFrrD\'Zj+,$t_goXT_goXT_gh^e56,bT@DLj;iP8m;@DHr756(Z`!!*$!irJ+i_goXTj+-0?k5bJ]^];.M^];.Mz5JV?U@DLj;iP=Ef@DHs"5JR<8!Pe`O!Pe[8!;u?E^qdb$^q]r"io"c>#7&<K!!$tWr,?UoE,]c849,?]_goXT_goXT_goXT_gpp#It.M!!!\'oej+-.iB)m)T2?5o@49-?$!!(%ZkEtGBDn\'YgIIKAg3:Joc!!)&0G5sN$)uprY4odJ@G6$ZR!!\'oej+(V>B)m)T2?5o@)uprY)upfU2urFJ!!!$!"qDUi3,i:*!!%Csc[Yuq!8uc8_rlJ24FZJ1!!#(\\zi5"9di5"9di5"9di5"9di5"<eF21!?!!!$!zs8RTL!!!#Wi5!,.!8,rVfDkm[!\'UC4!,MXO!.4bg!"XSjJBrcG!"8i9!!\'gM^q]q(E+!)3i8EPOi*^LX2um?*0JG1?3&ilO0Q:F8)uprY)uprYs*u\'h)uprY!!$tG@))d;!8uc8!"9ha3&!%*?sqp.)utHg@fU"hj+-0?j+-0?j+(V>G5sf,!!!!YGh<iM(`4),(`44mIfMh9!rrE\'#64r.$ih+E0E>J\\s*u\'hrr>Cd!rrE\'*WSD)!rrFR"+\\DlrVuou!!!6(%fd[O56*VBB)q)ps*t=S#64u/!<0dL_#+ZI#7$:e!"T&o!,qpG!+5g,!:ta$JDl#gJ9(]Sz!<7QO!!<3+!!WE5!"8iI!#P\\q!&+Bm!.OuY!+Q"M!\'UBH!+Q#hJE)/iJ:@P!!#tug!+Q#hJE)1?J9QN.J-,cR!!`LO!!!#7huE`W!!(s8!+9aGz?sqp.!!!!/!$2+]!\'^H>!&K.TJ73ue^u3#DhuEcW!5j?)JAVBe!<3&:JAZoTJB*3>!!`Kg^b>b-!+5e7!8mib!+5eG!\'%b9^]4?7!<3&:JAK%;^qdb$^qdb%^qkQAJGoNKrkQ=brr0^K^qfpLrkQ=b_#D-b^qd_jJ03]/!,qpG!+5fei*]r#?uTL5?m";,!!!#8^qmh&^qmhd_#M3d^qmh&^qmh&^]8UuE,]c8E,]c8p])-J(`4),(`4),(`57%!!!#:!6,#a!8ISL!;HQl!6tSb!5efSJ,mC#^qdb$^qdb$rVurfE:@i9nG)M+nCb&%Yg9Q"0ZPle0E;+2_!o/7^t?HX^s9a8^rO7.^r*t(^]sj(^i84NE+!WmE8Y\\CE+!X(?o[\'d^]4?7rl;poa8YkL^qd_c!<)u=!5efS!65*=!6bGg!65)W!5j=,!.OuV!8mib!-eJb!!`K+J-,el!<)ru!!!$!J/eP/!#ttY!#ttY!#ttY!#ttY!!!#8^qmh&^qmh&^qmh&^qmhF^iP#jz!5ZJ0J73t<J9(]H!&jmA!$2+]!#tt=!5jiWNp"W!b\\#XZgcY?oGW^45GSi+7!98TN!&jmA!#ttY!\'UBA!-8-MJAHa9!9&H<J9LuO!\'UB&!#ttY!#ttY!#tt=!<7QO!!`K6!"8iI!&ss4!,qqr!<7QL?n_REG67qsj5]<P!!\'gM^tetM_o\'C0kPbH&IUM*li*^Uj!!!!"J,t0$J/s/iJ7F,iJDl%;J7F+NJ3SPa!$2,a!+Q#hJH(/X!+5eH!\'^G`!!#3%E.%S&E,]c8E,ZhJIt2$ZiIKm;iIGEgF+?K*!It9&B)k*q!5QCch#HEP_o\'C0_na%f^qdb$^qdb$^b@GB0JG170JG170JG2"huLR.^rOaUq!e(6cGoq#^qdb$^qdb$^qdb@nGg#](rmK6(rmK6(rmK6(u5/O_o\'C0_o!MqIfNu/iIKm;iIG?eF+?IT!!(gSj28dPj6-EW^qd`+J:E)ZJE)1=JDl#gJ9-6*J,t0$J,t0$JDC(\\^qdb$^q`\']i*\\YW#0-WB+CKTp?smAM?uS4._o\'C0_o\'OXIfRB:_Z8j"AcQECIK2J149-?$a#M+!mkA[aD=Du3H/L^@38ifsB)m)T49-?$49.PFB)prl_goW)k5])oFoX]+49.JD)upfU2ummthuNcU%NH<>E+&ZaJH(-"!5RLm!64GS3.1/6&cb,rz_8*n&_8*n&_8*n&_8*n&iP9Mb56(Z`rrE*!!!!#Wi4o<mpt/[K(d.fMGW[#grYQIPi4qSX!+93m^qdb$^u/U>!!(qb?na8g0Q:E-^]52g)#b?h(gpae_!h>3huE`o3&!$o?spdc!.8Cu`l?$<ApaRYE:>P80JG170ED"T"qD%Y0OXk[r!!?649buoqu?^**\'AUbbl8([!.J<`GRao^#5eH$5%%drk/PDQ49,B\\"q1n[(cX3g!.O\'BI!k(rk\'R./I-/GgDDh\\-GQ7a%?iU0,@,M"bi*ZNb!+=a#^]4?O!\'C6D!&agh!.Fq.!5efSJ,oMe`m"A#`l@oV5@@mWi8A!^56(]]`l#^3_oL(#!;sXJ_#2!`_#+31^qdb`^qdb$!!#66Dua8GhuMqjiIG?eEI^9(!!!#:_o\'Cl_o\'C0!:XB(?smAM@.4.5(`4),(`4),)"7M*cJ7(AnCZO?`W3fi^qdb$^qfjJ!9(`P_"5A5_"YY$^tul^^s\'Roj5]b.gY^>t`rH*(!+CCd^u3#d^u3":^i=lhzr6EU5r4p+`^]=;XcHQ4=bfn\',Ic0.\'4:VQ"qu?`s(`4),(`4),!5l^l_o\'C0`dRmf_oLnODEL$D(]XQU0[DHAE,T-6i-F7+i&SS,^]<M74?,;_ChC]f`o_)"3#EJL(]aOF$lCrX@,V%B?iU1S%L.C%c@,c/^qfll`l?$Bqu?_E@,Si9@!hqY"pTNgk/PDQIK0@qB#ahc@"&)8?srb;?smAM?iYXf`l?#1IKg"(!5QCcr63C/bfn;H^];0c^qdb$^b@GB0JG170JG170]2rH^qeb#nF5r"beV$0^qdb$^qd_c!<9j[i6:-\'i6:-\'i6:*Zr63C/bfn92HtLF>a(B]!!;t\'\\`m2g+^qd_c!.JPB`l;V>"pP83!;O@F^qdb$!.;T?3"-5n!+940?smAM@!D[qbfn;TbkqI\\cKo@l3&o-tcG8;PJ&$D]F+A=^c>5I"3,HUSc>7<A3&iTGhuNZp(bf?*quH]r!8mhWDEKn+joBc/!5l^l_o\'C0`dRpc!<;fo!!\'gM_"cR/:]M&Sd*R"W(An^T^qd`N0OS;(^qdb$^gLQc?smA]0JHmB@))ar0`Ea[0EC%H_!h=(huFTJ0JHmB@)0Q;CsL&?`l;hB!&/B]0JG170JGKQ$k*O]0OXm)bR=o)$jI4>!"9i04D`7@$k.Mk?srmB"q:D0*,o<$r5Q`oHiX-M$k*si0JIH*Cs6]TCrXJB!\'"f7`pS9a%!Vb[huE`W!8miBhuE`W!5QCc(cXW?CjtNe_slI*bkTE-bkrN&@,Si9i*\\_KnD)%\'a2Z-Eq"VY?_"b^\\_"d]?^qf`\\^qd`,F(!qP_rG5k!63$u`r<ut`l@LU?smAM?srIX0JG170JG170]2rVbh2FSnCYt1^qdb$^qdb$pq_L@JE)1CJG4TgJDGb3JDGaqk2uC:hTjEd*WU6]@=Z1E_19@PiIGD<4obQ_nD)73h!i+p_!p.\'bhW!Gbfi\'5^u0GG%Li78r\\-#[0JG170ZM,P`l?$<`d@d(`l;n4Ccj[:c="q*c=$*KHbb!DHb_AO0n@:3CcFC6Ci784`b]HN3&!$?rXK>R3&"aurW(ka3,B"Nbfotb!5QD>gs"!dbkM/TCr!j%i-YM)"pQu\'`l?$\\IK2?DcMkW;HiO.k?smAM?smAM0Q+nM`o_^S:4*&W_!q9Gbfn;ThuEab?smAM?uQ)G0JG170JG2"huLR.^tA/7nG(W9^qdb$^qdb$^bYuJ^s\'U<^s\'U<^s\'SJr63C/bfgo?`l?#1HiPkUbfn;TpqX\\\\0Q+nM`o_^S"pQd>^qdb$^bFufE#];]!+92B?smAMGQ7a+k2tf<IK0Alb]nAW0E;+/^tjOuJ9QNf!-8,?m!(4/I*;T7b^=Y[0JIJ(!#QP,?srm4p5B"05X]EJ3,ASB!63$u`l?$<`d@da!<;Ng!5QCc!!',
)

TABLES = {'MAST': [(14, 0, 0, 0, 0), (28, 25, 15, 1, 43), (34, 30, 51, 2, 46), (15, 13, 15, 1, 43), (26, 22, 56, 3, 47), (26, 22, 56, 1, 47), (34, 27, 27, 3, 35), (20, 12, 21, 3, 11), (19, 17, 2, 1, 17), (20, 11, 12, 4, 11), (13, 14, 54, 0, 46), (34, 32, 45, 1, 44), (34, 31, 44, 1, 44), (34, 32, 44, 1, 44), (34, 32, 45, 1, 44), (34, 33, 43, 0, 43), (34, 30, 44, 2, 43), (34, 31, 45, 2, 44), (34, 30, 43, 2, 43), (34, 32, 45, 1, 44), (34, 31, 45, 1, 44), (19, 11, 34, 4, 33), (19, 12, 43, 3, 33), (47, 48, 43, 0, 43), (43, 41, 43, 1, 43), (42, 37, 45, 3, 44), (48, 44, 43, 1, 43), (40, 39, 43, 1, 43), (39, 37, 43, 1, 43), (49, 43, 45, 3, 44), (50, 49, 43, 1, 43), (26, 24, 43, 1, 43), (26, 27, 58, -2, 43), (47, 46, 43, 1, 43), (41, 39, 43, 1, 43), (58, 56, 43, 1, 43), (48, 47, 43, 1, 43), (49, 43, 45, 3, 44), (40, 39, 43, 1, 43), (45, 45, 43, 1, 43), (36, 34, 45, 1, 44), (41, 41, 43, 0, 43), (46, 45, 44, 1, 43), (43, 43, 43, 0, 43), (65, 67, 43, -1, 43), (47, 47, 43, 0, 43), (45, 45, 43, 0, 43), (43, 39, 43, 2, 43), (20, 16, 10, 2, 46), (38, 35, 35, 2, 34), (40, 38, 47, 0, 46), (33, 30, 35, 2, 34), (40, 38, 47, 2, 46), (36, 32, 35, 2, 34), (26, 31, 47, 0, 47), (35, 36, 50, -1, 36), (41, 40, 46, 0, 46), (23, 22, 47, 0, 47), (23, 20, 62, -2, 47), (40, 41, 46, 0, 46), (23, 21, 46, 1, 46), (61, 60, 34, 0, 34), (41, 40, 34, 0, 34), (38, 34, 35, 2, 34), (40, 38, 47, 0, 33), (40, 38, 47, 2, 33), (34, 33, 33, 0, 33), (30, 28, 34, 1, 33), (27, 25, 41, 1, 40), (41, 39, 34, 1, 33), (38, 38, 33, 0, 33), (51, 53, 33, -1, 33), (42, 42, 33, 0, 33), (35, 38, 47, -1, 33), (33, 32, 33, 0, 33), (34, 27, 11, 3, 27), (20, 11, 12, 4, 27), (34, 26, 27, 4, 35), (46, 45, 57, 1, 56), (30, 32, 2, -1, 17), (60, 62, 2, -1, 17), (18, 12, 20, 3, 43)], 'H1': [(8, 0, 0, 0, 0), (15, 12, 9, 2, 23), (18, 17, 27, 1, 25), (9, 5, 9, 2, 23), (11, 9, 29, 1, 23), (11, 10, 29, 0, 23), (18, 16, 17, 1, 20), (9, 8, 9, 0, 4), (10, 10, 5, 0, 11), (9, 7, 6, 1, 5), (13, 14, 23, 0, 23), (18, 17, 25, 1, 24), (18, 13, 23, 1, 23), (18, 17, 24, 1, 24), (18, 17, 25, 1, 24), (18, 18, 23, 0, 23), (18, 16, 24, 1, 23), (18, 17, 25, 1, 24), (18, 18, 23, 0, 23), (18, 17, 25, 1, 24), (18, 17, 25, 1, 24), (9, 7, 19, 1, 18), (9, 8, 23, 0, 18), (22, 23, 23, 0, 23), (22, 18, 23, 2, 23), (20, 19, 25, 1, 24), (24, 20, 23, 2, 23), (18, 15, 23, 2, 23), (18, 14, 23, 2, 23), (23, 20, 25, 1, 24), (24, 20, 23, 2, 23), (12, 11, 23, 1, 23), (11, 11, 30, -3, 23), (21, 20, 23, 2, 23), (18, 15, 23, 2, 23), (30, 26, 23, 2, 23), (26, 22, 23, 2, 23), (25, 23, 25, 1, 24), (20, 17, 23, 2, 23), (21, 20, 23, 2, 23), (18, 16, 25, 1, 24), (19, 18, 23, 0, 23), (24, 20, 24, 2, 23), (21, 21, 23, 0, 23), (31, 31, 23, 0, 23), (21, 22, 23, 0, 23), (20, 20, 23, 0, 23), (19, 18, 23, 0, 23), (12, 10, 6, 1, 25), (19, 16, 19, 1, 18), (20, 17, 26, 2, 25), (16, 15, 19, 1, 18), (20, 17, 26, 1, 25), (19, 17, 19, 1, 18), (12, 14, 25, 0, 25), (20, 17, 26, 1, 18), (21, 17, 25, 2, 25), (10, 6, 25, 2, 25), (10, 11, 33, -3, 25), (20, 18, 25, 2, 25), (10, 6, 25, 2, 25), (31, 28, 18, 2, 18), (21, 17, 18, 2, 18), (20, 18, 19, 1, 18), (20, 17, 26, 2, 18), (20, 17, 26, 1, 18), (15, 12, 18, 2, 18), (16, 14, 19, 1, 18), (14, 13, 23, 0, 22), (21, 17, 19, 2, 18), (18, 19, 18, 0, 18), (27, 28, 18, 0, 18), (18, 19, 18, 0, 18), (18, 19, 26, 0, 18), (16, 15, 18, 0, 18), (18, 16, 6, 1, 14), (9, 7, 6, 1, 14), (18, 15, 15, 2, 19), (24, 20, 31, 2, 30), (16, 14, 5, 1, 11), (32, 30, 5, 1, 11), (7, 7, 8, 0, 23)], 'H2': [(6, 0, 0, 0, 0), (10, 8, 6, 1, 16), (13, 12, 19, 0, 17), (6, 4, 6, 1, 16), (7, 7, 20, 0, 16), (7, 7, 20, 0, 16), (13, 12, 12, 0, 14), (6, 5, 6, 0, 3), (7, 7, 4, 0, 8), (6, 5, 5, 1, 4), (9, 9, 16, 0, 16), (13, 12, 17, 0, 16), (13, 9, 16, 1, 16), (13, 12, 16, 0, 16), (13, 12, 17, 0, 16), (13, 13, 16, 0, 16), (13, 11, 17, 1, 16), (13, 12, 17, 0, 16), (13, 12, 16, 0, 16), (13, 12, 17, 0, 16), (13, 12, 17, 0, 16), (6, 5, 14, 1, 13), (6, 6, 16, 0, 13), (15, 16, 16, 0, 16), (15, 13, 16, 1, 16), (14, 13, 17, 1, 16), (16, 15, 16, 1, 16), (12, 11, 16, 1, 16), (12, 10, 16, 1, 16), (16, 14, 17, 1, 16), (17, 14, 16, 1, 16), (9, 8, 16, 0, 16), (7, 8, 21, -2, 16), (15, 14, 16, 1, 16), (12, 11, 16, 1, 16), (21, 18, 16, 1, 16), (18, 15, 16, 1, 16), (18, 16, 17, 1, 16), (14, 12, 16, 1, 16), (15, 14, 16, 1, 16), (12, 11, 17, 1, 16), (13, 13, 16, 0, 16), (17, 14, 17, 1, 16), (14, 15, 16, 0, 16), (21, 22, 16, 0, 16), (15, 15, 16, 0, 16), (14, 14, 16, 0, 16), (13, 13, 16, 0, 16), (8, 8, 4, 0, 17), (13, 12, 14, 0, 13), (14, 12, 18, 1, 17), (11, 11, 14, 0, 13), (14, 13, 18, 0, 17), (13, 13, 14, 0, 13), (9, 10, 17, 0, 17), (14, 13, 19, 0, 13), (14, 12, 17, 1, 17), (7, 5, 17, 1, 17), (7, 8, 23, -2, 17), (14, 13, 17, 1, 17), (7, 4, 17, 1, 17), (22, 19, 13, 1, 13), (14, 12, 13, 1, 13), (14, 13, 14, 0, 13), (14, 12, 19, 1, 13), (14, 13, 19, 0, 13), (10, 9, 13, 1, 13), (11, 11, 14, 0, 13), (10, 9, 16, 0, 15), (14, 12, 14, 1, 13), (13, 13, 13, 0, 13), (19, 19, 13, 0, 13), (13, 13, 13, 0, 13), (13, 13, 19, 0, 13), (11, 11, 13, 0, 13), (13, 12, 5, 0, 10), (6, 5, 5, 1, 10), (13, 11, 11, 1, 13), (17, 14, 22, 1, 21), (11, 11, 4, 0, 8), (22, 22, 4, 0, 8), (5, 5, 6, 0, 16)], 'KICK': [(4, 0, 0, 0, 0), (8, 6, 5, 1, 12), (9, 9, 14, 0, 13), (4, 3, 5, 1, 12), (5, 5, 15, 0, 12), (5, 5, 15, 0, 12), (9, 9, 9, 0, 10), (5, 4, 5, 0, 2), (5, 5, 3, 0, 6), (5, 4, 4, 0, 3), (7, 7, 12, 0, 12), (9, 9, 13, 0, 12), (9, 7, 12, 0, 12), (9, 9, 12, 0, 12), (9, 9, 13, 0, 12), (9, 9, 12, 0, 12), (9, 9, 13, 0, 12), (9, 9, 13, 0, 12), (9, 9, 12, 0, 12), (9, 9, 13, 0, 12), (9, 9, 13, 0, 12), (5, 4, 10, 0, 9), (5, 4, 12, 0, 9), (11, 12, 12, 0, 12), (11, 9, 12, 1, 12), (10, 10, 13, 0, 12), (12, 10, 12, 1, 12), (9, 8, 12, 1, 12), (9, 7, 12, 1, 12), (12, 11, 13, 0, 12), (12, 10, 12, 1, 12), (6, 6, 12, 0, 12), (5, 6, 16, -2, 12), (11, 10, 12, 1, 12), (9, 8, 12, 1, 12), (15, 13, 12, 1, 12), (13, 11, 12, 1, 12), (13, 12, 13, 0, 12), (10, 9, 12, 1, 12), (11, 10, 12, 1, 12), (9, 9, 13, 0, 12), (9, 9, 12, 0, 12), (12, 10, 13, 1, 12), (10, 11, 12, 0, 12), (15, 16, 12, 0, 12), (11, 11, 12, 0, 12), (10, 10, 12, 0, 12), (9, 9, 12, 0, 12), (6, 6, 4, 0, 13), (10, 9, 10, 0, 9), (10, 9, 14, 1, 13), (8, 8, 10, 0, 9), (10, 9, 14, 0, 13), (9, 9, 10, 0, 9), (6, 7, 13, 0, 13), (10, 9, 13, 0, 9), (11, 9, 13, 1, 13), (5, 3, 13, 1, 13), (5, 6, 17, -2, 13), (10, 9, 13, 1, 13), (5, 3, 13, 1, 13), (16, 14, 9, 1, 9), (11, 9, 9, 1, 9), (10, 10, 10, 0, 9), (10, 9, 13, 1, 9), (10, 9, 13, 0, 9), (7, 6, 9, 1, 9), (8, 8, 10, 0, 9), (7, 7, 12, 0, 11), (11, 9, 10, 1, 9), (9, 10, 9, 0, 9), (14, 14, 9, 0, 9), (9, 10, 9, 0, 9), (9, 10, 13, 0, 9), (8, 8, 9, 0, 9), (9, 9, 3, 0, 7), (5, 4, 3, 0, 7), (9, 8, 8, 1, 10), (12, 10, 16, 1, 15), (8, 8, 3, 0, 6), (16, 16, 3, 0, 6), (3, 4, 5, 0, 12)], 'LAB': [(3, 0, 0, 0, 0), (6, 6, 5, 0, 10), (7, 7, 11, 0, 10), (3, 3, 5, 0, 10), (4, 5, 13, 0, 10), (4, 4, 13, 0, 10), (7, 7, 7, 0, 8), (4, 3, 4, 0, 2), (4, 4, 3, 0, 5), (4, 3, 3, 0, 2), (5, 6, 10, 0, 10), (7, 7, 11, 0, 10), (7, 6, 10, 0, 10), (7, 8, 10, 0, 10), (7, 7, 11, 0, 10), (7, 8, 10, 0, 10), (7, 7, 11, 0, 10), (7, 8, 11, 0, 10), (7, 8, 10, 0, 10), (7, 7, 11, 0, 10), (7, 7, 11, 0, 10), (4, 3, 9, 0, 8), (4, 3, 10, 0, 8), (9, 9, 10, 0, 10), (9, 8, 10, 1, 10), (8, 8, 11, 0, 10), (10, 8, 10, 1, 10), (7, 6, 10, 1, 10), (7, 6, 10, 1, 10), (9, 9, 11, 0, 10), (10, 8, 10, 1, 10), (5, 5, 10, 0, 10), (4, 5, 13, -1, 10), (9, 8, 10, 1, 10), (7, 6, 10, 1, 10), (12, 11, 10, 1, 10), (11, 9, 10, 1, 10), (10, 10, 11, 0, 10), (8, 7, 10, 1, 10), (9, 8, 10, 1, 10), (7, 7, 11, 0, 10), (8, 8, 10, 0, 10), (10, 8, 11, 1, 10), (8, 9, 10, 0, 10), (13, 13, 10, 0, 10), (9, 9, 10, 0, 10), (8, 9, 10, 0, 10), (8, 8, 10, 0, 10), (5, 5, 3, 0, 10), (8, 7, 9, 0, 8), (8, 7, 11, 1, 10), (7, 7, 9, 0, 8), (8, 8, 11, 0, 10), (8, 8, 9, 0, 8), (5, 6, 10, 0, 10), (8, 8, 12, 0, 8), (9, 7, 10, 1, 10), (4, 4, 10, 0, 10), (4, 5, 14, -1, 10), (8, 8, 10, 1, 10), (4, 2, 10, 1, 10), (13, 11, 8, 1, 8), (9, 7, 8, 1, 8), (8, 8, 9, 0, 8), (8, 7, 12, 1, 8), (8, 8, 12, 0, 8), (6, 5, 8, 1, 8), (6, 6, 9, 0, 8), (6, 6, 10, 0, 9), (9, 8, 9, 0, 8), (7, 8, 8, 0, 8), (11, 11, 8, 0, 8), (8, 8, 8, 0, 8), (7, 8, 12, 0, 8), (6, 6, 8, 0, 8), (7, 7, 3, 0, 6), (4, 3, 3, 0, 6), (7, 7, 7, 0, 8), (10, 8, 13, 1, 12), (6, 6, 3, 0, 5), (13, 13, 3, 0, 5), (3, 3, 4, 0, 10)], 'BODY': [(4, 0, 0, 0, 0), (7, 5, 6, 1, 13), (10, 8, 14, 1, 13), (4, 2, 6, 1, 13), (5, 5, 16, 0, 13), (5, 5, 16, 0, 13), (10, 9, 10, 0, 11), (5, 4, 5, 0, 2), (5, 5, 3, 0, 6), (5, 3, 4, 1, 3), (6, 7, 13, 0, 13), (10, 9, 14, 0, 13), (10, 6, 13, 1, 13), (10, 9, 13, 0, 13), (10, 9, 14, 0, 13), (10, 10, 13, 0, 13), (10, 8, 14, 1, 13), (10, 9, 14, 0, 13), (10, 9, 13, 0, 13), (10, 9, 14, 0, 13), (10, 9, 14, 0, 13), (5, 3, 11, 1, 10), (5, 4, 13, 0, 10), (11, 11, 13, 0, 13), (11, 10, 13, 1, 13), (11, 10, 14, 1, 13), (12, 11, 13, 1, 13), (9, 8, 13, 1, 13), (9, 8, 13, 1, 13), (12, 11, 14, 1, 13), (13, 10, 13, 1, 13), (6, 6, 13, 0, 13), (5, 6, 17, -2, 13), (11, 10, 13, 1, 13), (9, 8, 13, 1, 13), (15, 13, 13, 1, 13), (13, 11, 13, 1, 13), (13, 12, 14, 1, 13), (10, 9, 13, 1, 13), (11, 10, 13, 1, 13), (9, 9, 14, 0, 13), (9, 10, 13, 0, 13), (12, 10, 14, 1, 13), (10, 11, 13, 0, 13), (16, 16, 13, 0, 13), (10, 10, 13, 0, 13), (10, 10, 13, 0, 13), (10, 10, 13, 0, 13), (5, 5, 4, 0, 14), (10, 9, 11, 0, 10), (10, 9, 14, 1, 13), (8, 8, 11, 0, 10), (10, 10, 14, 0, 13), (10, 9, 11, 0, 10), (6, 7, 14, 0, 14), (10, 10, 15, 0, 10), (11, 9, 13, 1, 13), (4, 3, 13, 1, 13), (4, 5, 18, -1, 13), (9, 8, 13, 1, 13), (4, 2, 13, 1, 13), (16, 14, 10, 1, 10), (11, 9, 10, 1, 10), (10, 10, 11, 0, 10), (10, 9, 15, 1, 10), (10, 10, 15, 0, 10), (7, 6, 10, 1, 10), (8, 8, 11, 0, 10), (6, 6, 13, 0, 12), (11, 9, 11, 1, 10), (9, 9, 10, 0, 10), (13, 14, 10, 0, 10), (9, 9, 10, 0, 10), (9, 9, 15, 0, 10), (8, 8, 10, 0, 10), (10, 9, 4, 0, 8), (5, 3, 4, 1, 8), (10, 8, 8, 1, 10), (12, 10, 17, 1, 16), (8, 8, 3, 0, 6), (17, 17, 3, 0, 6), (3, 3, 6, 0, 13)], 'BODY2': [(4, 0, 0, 0, 0), (7, 5, 5, 1, 12), (9, 9, 14, 0, 13), (4, 2, 5, 1, 12), (5, 5, 15, 0, 12), (5, 5, 15, 0, 12), (9, 9, 9, 0, 10), (4, 4, 5, 0, 2), (5, 5, 2, 0, 5), (4, 3, 3, 1, 2), (6, 6, 12, 0, 12), (9, 9, 13, 0, 12), (9, 5, 12, 1, 12), (9, 9, 12, 0, 12), (9, 9, 13, 0, 12), (9, 9, 12, 0, 12), (9, 8, 13, 1, 12), (9, 9, 13, 0, 12), (9, 9, 12, 0, 12), (9, 9, 13, 0, 12), (9, 9, 13, 0, 12), (4, 3, 10, 1, 9), (4, 4, 12, 0, 9), (10, 11, 12, 0, 12), (10, 9, 12, 1, 12), (10, 10, 13, 0, 12), (12, 10, 12, 1, 12), (9, 7, 12, 1, 12), (8, 7, 12, 1, 12), (12, 11, 13, 0, 12), (12, 10, 12, 1, 12), (5, 5, 12, 0, 12), (4, 5, 16, -2, 12), (10, 9, 12, 1, 12), (8, 7, 12, 1, 12), (15, 12, 12, 1, 12), (12, 10, 12, 1, 12), (12, 12, 13, 0, 12), (10, 8, 12, 1, 12), (10, 9, 12, 1, 12), (9, 9, 13, 0, 12), (9, 9, 12, 0, 12), (12, 10, 13, 1, 12), (10, 10, 12, 0, 12), (15, 15, 12, 0, 12), (9, 10, 12, 0, 12), (9, 10, 12, 0, 12), (9, 9, 12, 0, 12), (4, 4, 4, 0, 13), (9, 8, 10, 0, 9), (10, 8, 14, 1, 13), (8, 8, 10, 0, 9), (10, 9, 14, 0, 13), (9, 9, 10, 0, 9), (6, 7, 13, 0, 13), (10, 9, 13, 0, 9), (10, 8, 13, 1, 13), (4, 2, 12, 1, 12), (4, 4, 16, -1, 12), (9, 8, 13, 1, 13), (4, 2, 13, 1, 13), (15, 13, 9, 1, 9), (10, 8, 9, 1, 9), (10, 9, 10, 0, 9), (10, 8, 13, 1, 9), (10, 9, 13, 0, 9), (7, 6, 9, 1, 9), (8, 7, 10, 0, 9), (6, 6, 12, 0, 11), (10, 8, 10, 1, 9), (8, 9, 9, 0, 9), (13, 13, 9, 0, 9), (8, 9, 9, 0, 9), (8, 9, 13, 0, 9), (8, 7, 9, 0, 9), (9, 9, 3, 0, 7), (4, 3, 3, 1, 7), (9, 8, 8, 1, 10), (12, 10, 16, 1, 15), (8, 8, 2, 0, 5), (16, 16, 2, 0, 5), (3, 3, 5, 0, 12)], 'SRC': [(3, 0, 0, 0, 0), (5, 5, 5, 0, 10), (7, 7, 11, 0, 10), (3, 3, 5, 0, 10), (4, 4, 13, 0, 10), (4, 4, 13, 0, 10), (7, 7, 7, 0, 8), (3, 3, 4, 0, 2), (4, 4, 2, 0, 4), (3, 3, 3, 0, 2), (5, 5, 10, 0, 10), (7, 7, 11, 0, 10), (7, 4, 10, 1, 10), (7, 7, 10, 0, 10), (7, 7, 11, 0, 10), (7, 8, 10, 0, 10), (7, 7, 11, 0, 10), (7, 7, 11, 0, 10), (7, 7, 10, 0, 10), (7, 7, 11, 0, 10), (7, 7, 11, 0, 10), (3, 3, 9, 0, 8), (3, 3, 10, 0, 8), (8, 9, 10, 0, 10), (8, 7, 10, 1, 10), (8, 8, 11, 0, 10), (9, 8, 10, 1, 10), (7, 6, 10, 1, 10), (7, 6, 10, 1, 10), (9, 9, 11, 0, 10), (10, 8, 10, 1, 10), (4, 4, 10, 0, 10), (4, 5, 13, -2, 10), (8, 8, 10, 1, 10), (7, 6, 10, 1, 10), (12, 10, 10, 1, 10), (10, 8, 10, 1, 10), (10, 10, 11, 0, 10), (8, 7, 10, 1, 10), (8, 7, 10, 1, 10), (7, 7, 11, 0, 10), (7, 8, 10, 0, 10), (10, 8, 11, 1, 10), (8, 8, 10, 0, 10), (12, 12, 10, 0, 10), (8, 8, 10, 0, 10), (7, 8, 10, 0, 10), (7, 7, 10, 0, 10), (4, 4, 3, 0, 10), (7, 7, 9, 0, 8), (8, 7, 11, 1, 10), (6, 6, 9, 0, 8), (8, 7, 11, 0, 10), (7, 7, 9, 0, 8), (4, 6, 10, 0, 10), (8, 7, 12, 0, 8), (8, 6, 10, 1, 10), (3, 2, 10, 1, 10), (3, 4, 14, -1, 10), (7, 6, 10, 1, 10), (3, 2, 10, 1, 10), (12, 11, 8, 1, 8), (8, 6, 8, 1, 8), (8, 8, 9, 0, 8), (8, 7, 12, 1, 8), (8, 7, 12, 0, 8), (5, 5, 8, 1, 8), (6, 6, 9, 0, 8), (5, 5, 10, 0, 9), (8, 6, 8, 1, 7), (7, 7, 7, 0, 7), (10, 11, 7, 0, 7), (7, 7, 7, 0, 7), (7, 7, 11, 0, 7), (6, 6, 7, 0, 7), (7, 7, 3, 0, 6), (3, 3, 3, 0, 6), (7, 7, 7, 0, 8), (10, 8, 13, 1, 12), (6, 6, 2, 0, 4), (13, 13, 2, 0, 4), (2, 3, 4, 0, 10)], 'FOOT': [(3, 0, 0, 0, 0), (5, 5, 4, 0, 9), (7, 7, 11, 0, 10), (3, 2, 4, 0, 9), (4, 4, 11, 0, 9), (4, 4, 11, 0, 9), (7, 7, 7, 0, 8), (3, 3, 4, 0, 2), (4, 4, 2, 0, 4), (3, 3, 3, 0, 2), (4, 5, 9, 0, 9), (7, 7, 10, 0, 9), (7, 4, 9, 1, 9), (7, 7, 9, 0, 9), (7, 7, 10, 0, 9), (7, 7, 9, 0, 9), (7, 7, 10, 0, 9), (7, 7, 10, 0, 9), (7, 7, 9, 0, 9), (7, 7, 10, 0, 9), (7, 7, 10, 0, 9), (3, 3, 8, 0, 7), (3, 3, 9, 0, 7), (8, 8, 9, 0, 9), (8, 7, 9, 1, 9), (8, 8, 10, 0, 9), (9, 8, 9, 1, 9), (7, 5, 9, 1, 9), (6, 5, 9, 1, 9), (9, 8, 10, 0, 9), (9, 7, 9, 1, 9), (4, 4, 9, 0, 9), (3, 4, 12, -1, 9), (7, 7, 9, 1, 9), (6, 5, 9, 1, 9), (11, 9, 9, 1, 9), (9, 7, 9, 1, 9), (9, 9, 10, 0, 9), (7, 6, 9, 1, 9), (7, 7, 9, 1, 9), (7, 7, 10, 0, 9), (7, 7, 9, 0, 9), (9, 7, 10, 1, 9), (7, 8, 9, 0, 9), (11, 12, 9, 0, 9), (7, 7, 9, 0, 9), (7, 7, 9, 0, 9), (7, 7, 9, 0, 9), (3, 3, 3, 0, 10), (7, 6, 8, 0, 7), (7, 6, 11, 1, 10), (6, 6, 8, 0, 7), (7, 7, 11, 0, 10), (7, 7, 8, 0, 7), (4, 5, 10, 0, 10), (7, 7, 10, 0, 7), (7, 6, 10, 1, 10), (3, 3, 9, 0, 9), (3, 4, 12, -1, 9), (6, 6, 10, 1, 10), (3, 2, 10, 1, 10), (11, 10, 7, 1, 7), (7, 6, 7, 1, 7), (7, 7, 8, 0, 7), (7, 6, 10, 1, 7), (7, 7, 10, 0, 7), (5, 4, 7, 1, 7), (6, 6, 8, 0, 7), (4, 5, 9, 0, 8), (7, 7, 8, 0, 7), (6, 7, 7, 0, 7), (9, 10, 7, 0, 7), (6, 7, 7, 0, 7), (6, 7, 10, 0, 7), (6, 6, 7, 0, 7), (7, 7, 3, 0, 6), (3, 3, 3, 0, 6), (7, 7, 6, 0, 7), (9, 7, 12, 1, 11), (6, 6, 2, 0, 4), (12, 12, 2, 0, 4), (2, 2, 4, 0, 9)]}

# ---------------------------------------------------------------- content
MASTHEAD = "THE WORLD TODAY"
DATE_LINE = "SUNDAY, 22 NOVEMBER 2026"
KICKER_LINE = "SIX STORIES · ONE DAY"
FOOTER = ("All stories first reported on 22 November 2026 · "
          "Drawn entirely by code — no photography, no AI imagery")

LEAD = {
    "kicker": "CLIMATE · ANTALYA, TÜRKIYE",
    "headline": "COP31 runs into Sunday with no deal — fossil fuels still off the table",
    "body": ("A revised draft tabled early on Sunday still leaves out any move away "
             "from coal, oil and gas, and drops a $120bn adaptation-finance target. "
             "Nearly 200 nations stay divided."),
    "sources": "Reuters · AP · UN News",
}

STORIES = [
    {
        "kicker": "BAHRAIN",
        "headline": "Iran claims strikes on US Patriot radars in Bahrain",
        "body": ("Iran's IRGC says missiles and drones hit two US Patriot radars at "
                 "al-Riffa and Awali; Bahrain says a civilian industrial facility "
                 "caught fire with no casualties; the US denies claims of F-16 damage."),
        "sources": "Al Jazeera · IANS · euronews",
    },
    {
        "kicker": "LVIV, UKRAINE",
        "headline": "Russian strikes hit Lviv again, at least 5 dead",
        "body": ("A night air assault struck Lviv again; Zelenskyy says Russia fired "
                 "more than 50 missiles and about 500 drones, with parts of the city "
                 "without power."),
        "sources": "Reuters · Ukraine officials",
    },
    {
        "kicker": "GAZA AID",
        "headline": "Four nations urge Israel to let aid into flooded Gaza",
        "body": ("Australia, Canada, Italy and Britain jointly call on Israel to allow "
                 "humanitarian aid into flood-hit Gaza."),
        "sources": "Reuters · AP",
    },
    {
        "kicker": "HONG KONG",
        "headline": "Election Committee polls open, 856 chase 723 seats",
        "body": ("Voting begins in the Election Committee subsector elections, with "
                 "856 candidates contesting 723 seats."),
        "sources": "China Daily · SCMP",
    },
]

BAR_STORY = {
    "kicker": "ISRAEL",
    "headline": "Eisenkot invites Likud to coalition talks, first meeting Sunday",
    "body": ("Eisenkot, mandated to form a government, invites Netanyahu's Likud for "
             "a new round of coalition talks, with the first meeting set for Sunday."),
    "sources": "Maariv · Reuters",
}

BRIEFS = [
    ("France sees a fourth straight weekend of cost-of-living protests.",
     "The Paris Eye"),
    ("Kenya's last Ebola patient discharged; DR Congo death toll passes 5,300.",
     "C54"),
]

TABLE_ORDER = ("MAST", "H1", "H2", "KICK", "LAB", "BODY", "BODY2", "SRC", "FOOT")


# ---------------------------------------------------------------- font engine
def load_fonts():
    """Decode the blob into {table: {char: (adv, w, h, dx, top, rows)}}."""
    raw = base64.a85decode("".join(FONT_BLOB), adobe=False)
    fonts = {}
    pos = 0
    for name in TABLE_ORDER:
        table = {}
        for ch, (adv, w, h, dx, top) in zip(CHARSET, TABLES[name]):
            nbytes = ((w + 7) // 8) * h
            table[ch] = (adv, w, h, dx, top, raw[pos:pos + nbytes])
            pos += nbytes
        fonts[name] = table
    assert pos == len(raw), "font blob length mismatch: %d != %d" % (pos, len(raw))
    return fonts


def text_width(font, text, tracking=0):
    """Advance width of text in one font table (tracking added between chars)."""
    total = 0
    for ch in text:
        g = font.get(ch)
        if g is None:
            g = font[" "]
        total += g[0] + tracking
    return total - tracking if text else 0


def wrap_text(font, text, width, tracking=0):
    """Greedy word wrap. Returns a list of lines; never drops a word."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(font, trial, tracking) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                # A single word wider than the column: hard-split it.
                while text_width(font, word, tracking) > width:
                    cut = 1
                    while (cut < len(word)
                           and text_width(font, word[:cut + 1], tracking) <= width):
                        cut += 1
                    lines.append(word[:cut])
                    word = word[cut:]
                cur = word
        if cur:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Sheet:
    def __init__(self):
        self.buf = bytearray(CREAM * (PAGE_W * PAGE_H))

    def rect(self, x, y, w, h, color):
        r, g, b = color
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(PAGE_W, x + w)
        y1 = min(PAGE_H, y + h)
        for yy in range(y0, y1):
            base = yy * PAGE_W * 3
            for xx in range(x0, x1):
                o = base + xx * 3
                self.buf[o] = r
                self.buf[o + 1] = g
                self.buf[o + 2] = b

    def diamond(self, cx, cy, radius, color):
        """A small rotated square, drawn row by row."""
        r, g, b = color
        for dy in range(-radius, radius + 1):
            half = radius - abs(dy)
            y = cy + dy
            if 0 <= y < PAGE_H:
                base = y * PAGE_W * 3
                for xx in range(cx - half, cx + half + 1):
                    if 0 <= xx < PAGE_W:
                        o = base + xx * 3
                        self.buf[o] = r
                        self.buf[o + 1] = g
                        self.buf[o + 2] = b

    def blit(self, x0, y0, w, h, rows, color):
        stride = (w + 7) // 8
        r, g, b = color
        for row in range(h):
            y = y0 + row
            if y < 0 or y >= PAGE_H:
                continue
            base = y * PAGE_W * 3
            brow = rows[row * stride:(row + 1) * stride]
            for col in range(w):
                if brow[col >> 3] & (0x80 >> (col & 7)):
                    x = x0 + col
                    if 0 <= x < PAGE_W:
                        o = base + x * 3
                        self.buf[o] = r
                        self.buf[o + 1] = g
                        self.buf[o + 2] = b

    def text(self, font, x, baseline, text, color, tracking=0,
             align="left", width=None):
        """Draw text; baseline is the y of the text baseline. Returns start x."""
        w = text_width(font, text, tracking)
        if align == "center":
            x = x + (width - w) // 2
        elif align == "right":
            x = x + width - w
        cx = x
        for ch in text:
            g = font.get(ch)
            if g is None:
                g = font[" "]
            adv, gw, gh, dx, top, rows = g
            if gw and gh:
                self.blit(cx + dx, baseline - top, gw, gh, rows, color)
            cx += adv + tracking
        return x


# ---------------------------------------------------------------- png encoder
def write_png(sheet, path):
    raw = bytearray()
    for y in range(PAGE_H):
        raw.append(0)  # filter type 0: no filtering
        raw += sheet.buf[y * PAGE_W * 3:(y + 1) * PAGE_W * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", PAGE_W, PAGE_H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return png


# ---------------------------------------------------------------- page layout
def build_page(fonts):
    s = Sheet()
    report = []

    # --- masthead: deep-blue bar, gold double rule -----------------------
    s.rect(0, 0, PAGE_W, 124, NAVY)
    title_w = text_width(fonts["MAST"], MASTHEAD, tracking=3)
    tx = (PAGE_W - title_w) // 2
    s.diamond(tx - 30, 52, 7, GOLD)
    s.diamond(tx + title_w + 30, 52, 7, GOLD)
    s.text(fonts["MAST"], 0, 76, MASTHEAD, CREAM, tracking=3,
           align="center", width=PAGE_W)
    s.text(fonts["LAB"], MARGIN, 106, DATE_LINE, CREAM)
    s.text(fonts["LAB"], MARGIN, 106, KICKER_LINE, GOLD,
           align="right", width=CONTENT_W)
    s.rect(0, 117, PAGE_W, 3, GOLD)
    s.rect(0, 122, PAGE_W, 1, GOLD)
    report.append("masthead 0-124, title width %d" % title_w)

    # --- lead story, full width ------------------------------------------
    y = 142
    s.rect(MARGIN, y + 2, 10, 10, RUST)
    s.text(fonts["KICK"], MARGIN + 18, y + 12, LEAD["kicker"], RUST)
    y += 30
    head_lines = wrap_text(fonts["H1"], LEAD["headline"], CONTENT_W)
    assert len(head_lines) <= 2, "lead headline needs %d lines" % len(head_lines)
    for line in head_lines:
        s.text(fonts["H1"], MARGIN, y + 32, line, INK)
        y += 40
    body_lines = wrap_text(fonts["BODY"], LEAD["body"], CONTENT_W)
    assert len(body_lines) <= 3, "lead body needs %d lines" % len(body_lines)
    for line in body_lines:
        s.text(fonts["BODY"], MARGIN, y + 17, line, INK)
        y += 23
    y += 4
    s.text(fonts["SRC"], MARGIN, y + 13, LEAD["sources"], MUTED)
    y += 20
    lead_bottom = y
    report.append("lead %d-%d: headline %d lines, body %d lines"
                  % (142, lead_bottom, len(head_lines), len(body_lines)))

    # --- hairline ----------------------------------------------------------
    s.rect(MARGIN, lead_bottom + 8, CONTENT_W, 1, HAIR)
    grid_top = lead_bottom + 22

    # --- 2x2 card grid -----------------------------------------------------
    card_w = (CONTENT_W - 14) // 2
    card_h = 192
    for idx, st in enumerate(STORIES):
        cx = MARGIN + (idx % 2) * (card_w + 14)
        cy = grid_top + (idx // 2) * (card_h + 14)
        s.rect(cx, cy, card_w, 3, RUST)
        s.text(fonts["KICK"], cx, cy + 26, st["kicker"], RUST)
        hlines = wrap_text(fonts["H2"], st["headline"], card_w)
        assert len(hlines) <= 2, "card %d headline needs %d lines" % (idx, len(hlines))
        hy = cy + 34
        for line in hlines:
            s.text(fonts["H2"], cx, hy + 22, line, INK)
            hy += 27
        blines = wrap_text(fonts["BODY2"], st["body"], card_w)
        assert len(blines) <= 4, "card %d body needs %d lines" % (idx, len(blines))
        by = hy + 6
        for line in blines:
            s.text(fonts["BODY2"], cx, by + 16, line, INK)
            by += 21
        s.text(fonts["SRC"], cx, cy + card_h - 6, st["sources"], MUTED)
        report.append("card %d (%s): %d headline lines, %d body lines, y %d-%d"
                      % (idx + 2, st["kicker"], len(hlines), len(blines),
                         cy, cy + card_h))
    grid_bottom = grid_top + 2 * card_h + 14

    # --- story 6: full-width bar -------------------------------------------
    bar_top = grid_bottom + 14
    bar_h = 124
    s.rect(MARGIN, bar_top, CONTENT_W, bar_h, BAR_TINT)
    s.rect(MARGIN, bar_top, CONTENT_W, 2, GOLD)
    s.rect(MARGIN, bar_top + 2, 5, bar_h - 2, RUST)
    bx = MARGIN + 18
    bw = CONTENT_W - 18 - 12
    s.text(fonts["KICK"], bx, bar_top + 24, BAR_STORY["kicker"], RUST)
    bhlines = wrap_text(fonts["H2"], BAR_STORY["headline"], bw)
    assert len(bhlines) <= 1, "bar headline needs %d lines" % len(bhlines)
    s.text(fonts["H2"], bx, bar_top + 52, bhlines[0], INK)
    bblines = wrap_text(fonts["BODY"], BAR_STORY["body"], bw)
    assert len(bblines) <= 2, "bar body needs %d lines" % len(bblines)
    by = bar_top + 60
    for line in bblines:
        s.text(fonts["BODY"], bx, by + 17, line, INK)
        by += 23
    s.text(fonts["SRC"], bx, bar_top + bar_h - 8, BAR_STORY["sources"], MUTED)
    bar_bottom = bar_top + bar_h
    report.append("bar %d-%d: headline %d lines, body %d lines"
                  % (bar_top, bar_bottom, len(bhlines), len(bblines)))

    # --- ALSO TODAY: dark band ----------------------------------------------
    band_top = bar_bottom + 12
    band_h = 92
    s.rect(MARGIN, band_top, CONTENT_W, band_h, NAVY_DEEP)
    s.text(fonts["LAB"], MARGIN + 16, band_top + 22, "ALSO TODAY", GOLD)
    by = band_top + 30
    for num, (brief, src) in enumerate(BRIEFS, 1):
        line = "%d. %s (%s)" % (num, brief, src)
        one = wrap_text(fonts["BODY"], line, CONTENT_W - 32)
        assert len(one) <= 1, "brief %d needs %d lines" % (num, len(one))
        s.text(fonts["BODY"], MARGIN + 16, by + 17, one[0], BAND_TEXT)
        by += 23
    band_bottom = band_top + band_h
    report.append("also-today band %d-%d" % (band_top, band_bottom))

    # --- footer ---------------------------------------------------------------
    s.text(fonts["FOOT"], MARGIN, band_bottom + 22, FOOTER, MUTED,
           align="center", width=CONTENT_W)
    report.append("footer baseline %d (page bottom %d)"
                  % (band_bottom + 22, PAGE_H))
    assert band_bottom + 22 <= PAGE_H - 8, "page overflow"
    return s, report


def main():
    fonts = load_fonts()
    sheet, report = build_page(fonts)
    png = write_png(sheet, "entry.png")
    print("entry.png: %d bytes, md5 %s"
          % (len(png), hashlib.md5(png).hexdigest()))
    for line in report:
        print("  " + line)


if __name__ == "__main__":
    main()
