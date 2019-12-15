possible modifiers
==================

## +hit chance

+10 1d8 +3  -> +10 to hit against AC, 1d8+3 dmg on hit

## advantage / disadvantage / elven accuracy
advantage +10 1d8 +3      == a +10 1d8 + 3
disadvantage +10 1d8 + 3  == d +10 1d8 + 3

## crit on 19 and 20
+10 1d8 +3 (c:19)

## crit on 19 and 20, attack with advantage
a +10 1d8 +3 (c:19)

## reroll ones
+10 2d8 + 2d6 + 3 (rr:1)   -> reroll all ones in all four dice rolls
+10 2d8 (rr:1) + 2d6 + 3   -> reroll all ones in the two d8 rolled

+10 2d8 + 2d6 + 3 (rr:3/1)   -> reroll up to three ones in all four dice rolls
+10 2d8 (rr:1/1) + 2d6 + 3   -> reroll up to one one in the two d8 rolled

## (half|no) damage on save, (always hits|against ac)
--> display ac [10-20], saving_throw [-5, 15] as x axis

- fireball: 3d8 dmg, con save, we have +5 spell atk, always hits, half damage on save
3d8 (s:+5,half)

- fireball, but no dmg on save
3d8 (s:+5,no)

--> requires 3d plot, damage depends on both ac and save
- fireball, but we must make a ranged spell attack with our +3 to hit, and target can still save for half dmg
+3 3d8 (s:+5,half)
