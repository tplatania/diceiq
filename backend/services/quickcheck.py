
ORIENTATIONS = [
    (1,2,3,6,5,4),(1,3,5,6,4,2),(1,5,4,6,2,3),(1,4,2,6,3,5),
    (2,1,4,5,6,3),(2,4,6,5,3,1),(2,6,3,5,1,4),(2,3,1,5,4,6),
    (3,1,2,4,6,5),(3,2,6,4,5,1),(3,6,5,4,1,2),(3,5,1,4,2,6),
    (4,1,5,3,6,2),(4,5,6,3,2,1),(4,6,2,3,1,5),(4,2,1,3,5,6),
    (5,1,3,2,6,4),(5,3,6,2,4,1),(5,6,4,2,1,3),(5,4,1,2,3,6),
    (6,2,4,1,5,3),(6,4,5,1,3,2),(6,5,3,1,2,4),(6,3,2,1,4,5),
]
TOP_FRONT = {(o[0],o[1]):i for i,o in enumerate(ORIENTATIONS)}

def verify(name, lt, lf, rt, rf):
    from collections import Counter
    li = TOP_FRONT.get((lt,lf))
    ri = TOP_FRONT.get((rt,rf))
    if li is None:
        print(f'INVALID left die ({lt},{lf})')
        return
    if ri is None:
        print(f'INVALID right die ({rt},{rf})')
        return
    lo = ORIENTATIONS[li]
    ro = ORIENTATIONS[ri]
    l_axis = (lo[0],lo[1],lo[3],lo[4])
    r_axis = (ro[0],ro[1],ro[3],ro[4])
    print(f'\n{"="*50}')
    print(f'SET: {name}')
    print(f'Left die:  top={lt} front={lf} | axis faces: {l_axis}')
    print(f'Right die: top={rt} front={rf} | axis faces: {r_axis}')
    totals = []
    for l in l_axis:
        for r in r_axis:
            totals.append(l + r)
    dist = Counter(totals)
    sevens = dist.get(7, 0)
    point_numbers = {4, 5, 6, 8, 9, 10}
    print(f'\n  {"Total":<6} {"Count":<6} {"Bar":<10} Notes')
    print(f'  {"-"*45}')
    for n in range(2, 13):
        count = dist.get(n, 0)
        if n == 7:               note = "<-- SEVEN"
        elif n == 11:            note = "yo"
        elif n == 2:             note = "snake eyes"
        elif n == 12:            note = "midnight"
        elif n in point_numbers: note = "point"
        else:                    note = ""
        bar = "#" * count
        print(f'  {n:<6} {count:<6} {bar:<10} {note}')
    print(f'\n  Sevens on axis: {sevens}/16')

verify('All Sevens (4-2/3-5)',          4, 2, 3, 5)
verify('Hard Way (6-5/6-5)',            6, 5, 6, 5)
verify('3V Hard Six (3-2/3-6)',         3, 2, 3, 6)
verify('Parallel Sixes (6-3/6-3)',      6, 3, 6, 3)
verify('Crossed Sixes (6-2/6-3)',       6, 2, 6, 3)
verify('Mini-V Hard 4 (3-2/2-3)',       3, 2, 2, 3)
verify('2V Set (2-3/2-1)',              2, 3, 2, 1)

# -----------------------------------------------
# GOAL-DRIVEN SUMMARY TABLE
# Each set shows counts only for its target numbers
# -----------------------------------------------
print(f'\n\n{"="*100}')
print('DICEIQ — DICE SET GOAL-DRIVEN DISTRIBUTION TABLE')
print('Each set shows hit counts for the numbers it is designed to produce')
print(f'{"="*100}')

from collections import Counter

SETS = [
    # name, lt, lf, rt, rf, target_numbers
    ('All Sevens',     4,2,3,5, [7]),
    ('Hard Way',       6,5,6,5, [7]),
    ('3V Hard Six',    3,2,3,6, [6,8]),
    ('Parallel Sixes', 6,3,6,3, [4,5,9,10]),
    ('Crossed Sixes',  6,2,6,3, [4,5,6,8,9,10]),
    ('Mini-V Hard 4',  3,2,2,3, [5,9]),
    ('2V Set',         2,3,2,1, [4,10]),
]

ORIENTATIONS3 = [
    (1,2,3,6,5,4),(1,3,5,6,4,2),(1,5,4,6,2,3),(1,4,2,6,3,5),
    (2,1,4,5,6,3),(2,4,6,5,3,1),(2,6,3,5,1,4),(2,3,1,5,4,6),
    (3,1,2,4,6,5),(3,2,6,4,5,1),(3,6,5,4,1,2),(3,5,1,4,2,6),
    (4,1,5,3,6,2),(4,5,6,3,2,1),(4,6,2,3,1,5),(4,2,1,3,5,6),
    (5,1,3,2,6,4),(5,3,6,2,4,1),(5,6,4,2,1,3),(5,4,1,2,3,6),
    (6,2,4,1,5,3),(6,4,5,1,3,2),(6,5,3,1,2,4),(6,3,2,1,4,5),
]
TF3 = {(o[0],o[1]):i for i,o in enumerate(ORIENTATIONS3)}

def get_dist2(lt, lf, rt, rf):
    lo = ORIENTATIONS3[TF3[(lt,lf)]]
    ro = ORIENTATIONS3[TF3[(rt,rf)]]
    l_axis = (lo[0],lo[1],lo[3],lo[4])
    r_axis = (ro[0],ro[1],ro[3],ro[4])
    return Counter(l+r for l in l_axis for r in r_axis)

# Print each set as its own row
print(f'\n{"Set":<18} {"L top/front":<14} {"R top/front":<14} {"Target #s":<20} {"Hits/16":<10} {"7s/16":<8} {"Target %":<10} {"7-out %"}')
print(f'{"-"*100}')

for name, lt, lf, rt, rf, targets in SETS:
    dist = get_dist2(lt, lf, rt, rf)
    sevens = dist.get(7, 0)
    target_hits = sum(dist.get(n, 0) for n in targets)
    target_str = '+'.join(str(n) for n in targets)
    hits_detail = ' '.join(f'{n}:{dist.get(n,0)}' for n in targets)
    target_pct = f'{round(target_hits/16*100)}%'
    seven_pct = f'{round(sevens/16*100)}%'
    print(f'{name:<18} {str(lt)+"/"+str(lf):<14} {str(rt)+"/"+str(rf):<14} {target_str:<20} {hits_detail:<10} {sevens:<8} {target_pct:<10} {seven_pct}')
    print(f'{"":18} {"":14} {"":14} {"Breakdown:":<20} {hits_detail}')
    print()

print(f'{"="*100}')
print('Target % = how often target numbers hit on axis')
print('7-out %  = how often seven appears on axis')
print(f'{"="*100}\n')
