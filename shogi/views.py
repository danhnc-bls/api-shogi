import json
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
import copy
from math import inf


col = 7
row = 5
KomaValues = {'W': 100000, 'C': 500, 'F': 1000, 'T': 200}


def _komas_to_json(komas):
    return {'S': komas['S'].tolist(), 'E': komas['E'].tolist()}


def _komas_from_json(json):
    return {'S': np.asarray(json['S']), 'E': np.asarray(json['E'])}


def _tagloc_to_json(tagloc):
    tl = {'S': {}, 'E': {}}

    for key in tagloc['S']:
        tl['S'][key] = tagloc['S'][key].tolist()

    for key in tagloc['E']:
        tl['E'][key] = tagloc['E'][key].tolist()

    return tl


def _tagloc_from_json(json):
    tl = {'S': {}, 'E': {}}

    for key in json['S']:
        tl['S'][key] = np.asarray(json['S'][key])

    for key in json['E']:
        tl['E'][key] = np.asarray(json['E'][key])

    return tl


def _legal_actions(tag, tl, km, casyx):
    s_or_e = tag.split('-')[-1]
    ops = 'E' if s_or_e == 'S' else 'S'
    komas_self = km[s_or_e]
    komas_enemy = km[ops]
    casy, casx = casyx[s_or_e]
    y, x = tl[s_or_e][tag]

    if tag[0] == 'W':
        if y == casy and x == casx:
            candidates = ((y-1, x-1), (y-1, x), (y-1, x+1),
                          (y, x-1), (y, x+1),
                          (y+1, x-1), (y+1, x), (y+1, x+1),
                          )
        elif y == casy-1 and x == casx-1:
            candidates = ((y, x+1), (y+1, x), (y+1, x+1))
        elif y == casy and x == casx-1:
            candidates = ((y-1, x), (y+1, x), (y, x+1))
        elif y == casy+1 and x == casx-1:
            candidates = ((y-1, x), (y-1, x+1), (y, x+1))
        elif y == casy+1 and x == casx:
            candidates = ((y, x-1), (y-1, x), (y, x+1))
        elif y == casy+1 and x == casx+1:
            candidates = ((y-1, x), (y, x-1), (y-1, x-1))
        elif y == casy and x == casx+1:
            candidates = ((y-1, x), (y+1, x), (y, x-1))
        elif y == casy-1 and x == casx+1:
            candidates = ((y, x-1), (y+1, x), (y+1, x-1))
        elif y == casy-1 and x == casx:
            candidates = ((y, x-1), (y, x+1), (y+1, x))
        actions = []
        for i in range(len(candidates)):
            my, mx = candidates[i]
            if komas_self[my, mx] == 0:
                actions.append(candidates[i])

    elif tag[0] == 'F':
        actions = []
        adds = np.arange(1, col)
        for i in range(len(adds)):
            my = y+adds[i]
            if (my < 1) or (my > col) or komas_self[my, x] != 0:
                break
            elif komas_enemy[my, x] != 0:
                actions.append([my, x])
                break
            else:
                actions.append([my, x])
        adds = np.arange(-1, -col, -1)
        for i in range(len(adds)):
            my = y+adds[i]
            if (my < 1) or (my > col) or komas_self[my, x] != 0:
                break
            elif komas_enemy[my, x] != 0:
                actions.append([my, x])
                break
            else:
                actions.append([my, x])
        adds = np.arange(1, row)
        for i in range(len(adds)):
            mx = x+adds[i]
            if (mx < 1) or (mx > row) or komas_self[y, mx] != 0:
                break
            elif komas_enemy[y, mx] != 0:
                actions.append([y, mx])
                break
            else:
                actions.append([y, mx])
        adds = np.arange(-1, -row, -1)
        for i in range(len(adds)):
            mx = x+adds[i]
            if (mx < 1) or (mx > row) or komas_self[y, mx] != 0:
                break
            elif komas_enemy[y, mx] != 0:
                actions.append([y, mx])
                break
            else:
                actions.append([y, mx])
        if (y == casyx['S'][0] and x == casyx['S'][1]) or (y == casyx['E'][0] and x == casyx['E'][1]):
            if komas_self[y-1, x-1] == 0:
                actions.append([y-1, x-1])
            if komas_self[y+1, x-1] == 0:
                actions.append([y+1, x-1])
            if komas_self[y+1, x+1] == 0:
                actions.append([y+1, x+1])
            if komas_self[y-1, x+1] == 0:
                actions.append([y-1, x+1])
        if (y == casyx['S'][0]-1 and x == casyx['S'][1]-1) or (y == casyx['E'][0]-1 and x == casyx['E'][1]-1):
            if komas_self[y+1, x+1] == 0:
                actions.append([y+1, x+1])
            if komas_self[y+2, x+2] == 0 and komas_enemy[y+1, x+1] == 0:
                actions.append([y+2, x+2])
        if (y == casyx['S'][0]+1 and x == casyx['S'][1]-1) or (y == casyx['E'][0]+1 and x == casyx['E'][1]-1):
            if komas_self[y-1, x+1] == 0:
                actions.append([y-1, x+1])
            if komas_self[y-2, x+2] == 0 and komas_enemy[y-1, x+1] == 0:
                actions.append([y-2, x+2])
        if (y == casyx['S'][0]+1 and x == casyx['S'][1]+1) or (y == casyx['E'][0]+1 and x == casyx['E'][1]+1):
            if komas_self[y-1, x-1] == 0:
                actions.append([y-1, x-1])
            if komas_self[y-2, x-2] == 0 and komas_enemy[y-1, x-1] == 0:
                actions.append([y-2, x-2])
        if (y == casyx['S'][0]-1 and x == casyx['S'][1]+1) or (y == casyx['E'][0]-1 and x == casyx['E'][1]+1):
            if komas_self[y+1, x-1] == 0:
                actions.append([y+1, x-1])
            if komas_self[y+2, x-2] == 0 and komas_enemy[y+1, x-1] == 0:
                actions.append([y+2, x-2])

    elif tag[0] == 'C':
        candidates = []
        if y-1 >= 1 and komas_enemy[y-1, x] == 0 and komas_self[y-1, x] == 0:
            candidates.append((y-2, x+1))
            candidates.append((y-2, x-1))
        if x-1 >= 1 and komas_enemy[y, x-1] == 0 and komas_self[y, x-1] == 0:
            candidates.append((y-1, x-2))
            candidates.append((y+1, x-2))
        if y+1 <= col and komas_enemy[y+1, x] == 0 and komas_self[y+1, x] == 0:
            candidates.append((y+2, x-1))
            candidates.append((y+2, x+1))
        if x+1 <= row and komas_enemy[y, x+1] == 0 and komas_self[y, x+1] == 0:
            candidates.append((y-1, x+2))
            candidates.append((y+1, x+2))
        actions = []
        for i in range(len(candidates)):
            my, mx = candidates[i]
            if my >= 1 and my <= col and mx >= 1 and mx <= row and komas_self[my, mx] == 0:
                actions.append(candidates[i])

    elif tag[0] == 'T':
        if s_or_e == 'S':
            candidates = [(y-1, x), (y, x-1), (y, x+1)]
            if (y == casyx['S'][0] and x == casyx['S'][1]) or (y == casyx['E'][0] and x == casyx['E'][1]):
                candidates.append((y-1, x-1))
                candidates.append((y-1, x+1))
            elif (y == casyx['S'][0]+1 and x == casyx['S'][1]-1) or (y == casyx['E'][0]+1 and x == casyx['E'][1]-1):
                candidates.append((y-1, x+1))
            elif (y == casyx['S'][0]+1 and x == casyx['S'][1]+1) or (y == casyx['E'][0]+1 and x == casyx['E'][1]+1):
                candidates.append((y-1, x-1))
        else:
            candidates = [(y+1, x), (y, x-1), (y, x+1)]
            if (y == casyx['S'][0] and x == casyx['S'][1]) or (y == casyx['E'][0] and x == casyx['E'][1]):
                candidates.append((y+1, x-1))
                candidates.append((y+1, x+1))
            elif (y == casyx['S'][0]-1 and x == casyx['S'][1]-1) or (y == casyx['E'][0]-1 and x == casyx['E'][1]-1):
                candidates.append((y+1, x+1))
            elif (y == casyx['S'][0]-1 and x == casyx['S'][1]+1) or (y == casyx['E'][0]-1 and x == casyx['E'][1]+1):
                candidates.append((y+1, x-1))
        actions = []
        for i in range(len(candidates)):
            my, mx = candidates[i]
            if my >= 1 and my <= col and mx >= 1 and mx <= row and komas_self[my, mx] == 0:
                actions.append(candidates[i])

    return actions


def _eliminate_dangerous_actions(tag, actions, tl, km, casyx):
    mod_actions = []
    for i in range(len(actions)):
        ny, nx = actions[i]
        if _check_kiki2whale(tag, ny, nx, tl, km, 'legal_action', casyx) == False:
            mod_actions.append(actions[i])
    return mod_actions


def _check_kiki2whale(tag, ny, nx, tlc, kmc, arg, casyx):
    tl = copy.deepcopy(tlc)
    km = copy.deepcopy(kmc)
    nexttl, nextkm = _get_next_state(tag, ny, nx, tl, km)
    s_or_e = tag.split('-')[-1]
    ops = 'E' if s_or_e == 'S' else 'S'

    if arg == 'legal_action':
        wloc = nexttl['S']['W-S'] if s_or_e == 'S' else nexttl['E']['W-E']
        tls = nexttl[ops]
    elif arg == 'check':
        wloc = nexttl['E']['W-E'] if s_or_e == 'S' else nexttl['S']['W-S']
        tls = nexttl[s_or_e]
    else:
        print('Error in check_kiki2Whale.')

    for tg, v in tls.items():
        legalact = _legal_actions(tg, nexttl, nextkm, casyx)
        for act in legalact:
            if act[0] == wloc[0] and act[1] == wloc[1]:
                return True
    return False


def _get_next_state(tag, ny, nx, tagloc, komas):
    s_or_e = tag.split('-')[-1]
    ops = 'E' if s_or_e == 'S' else 'S'

    nexttl = copy.deepcopy(tagloc)
    nextkm = copy.deepcopy(komas)
    cy, cx = nexttl[s_or_e][tag]
    n = nextkm[s_or_e][cy, cx]
    nextkm[s_or_e][cy, cx] = 0
    nextkm[s_or_e][ny, nx] = n

    nexttl[s_or_e][tag] = np.array([ny, nx])
    remtag = [k for k, v in nexttl[ops].items() if (v[0] == ny and v[1] == nx)]
    if len(remtag) != 0:
        remtag = remtag[0]
        nextkm[ops][ny, nx] = 0
        del nexttl[ops][remtag]

    return nexttl, nextkm


def _chakusyu(tag, ny, nx, tagloc, komas, casyx):
    kihu = ''
    s_or_e = tag.split('-')[-1]
    if _check_kiki2whale(tag, ny, nx, tagloc, komas, 'check', casyx) == True:
        # StateDisp['text'] = f'チャングン（王手）！'
        # StateDisp['foreground'] = get_koma_color(s_or_e)
        # TODO: HANDLE THIS
        # Should return a message
        print('チャングン（王手）!')

    tl, km = _get_next_state(tag, ny, nx, tagloc, komas)
    tagloc[s_or_e] = tl[s_or_e]
    komas[s_or_e] = km[s_or_e]

    tagloc, komas = _remove_defeated_koma(tag, ny, nx, tagloc, komas)

    komatype = tag.split('-')[0]
    kihu = s_or_e + ' ' + komatype + ' ' + str(ny) + ' ' + str(nx)

    return tagloc, komas, kihu


def _remove_defeated_koma(tag, y, x, tagloc, komas):
    s_or_e = tag.split('-')[-1]
    ops = 'E' if s_or_e == 'S' else 'S'

    tl = tagloc[ops]
    remtag = [k for k, v in tl.items() if (v[0] == y and v[1] == x)]
    if len(remtag) != 0:
        remtag = remtag[0]
        komas[ops][y, x] = 0
        del tagloc[ops][remtag]

    return tagloc, komas


def _change_turn(turns, komas, tagloc, search_level, casyx):
    init_flag = 0
    txt = ''
    kihu = ''

    s_or_e = 'S' if turns % 2 == 0 else 'E'
    cplayer = _get_cplayer(s_or_e)

    if _is_finish(s_or_e, komas, tagloc, casyx):
        if _is_lost_whale(s_or_e, komas):
            txt = f'{cplayer}の勝ちです（クジラ奪取）'
        elif _is_tsumi(s_or_e, komas, tagloc, casyx):
            txt = f'{cplayer}の勝ちです（詰み）'
        elif _is_under_two(s_or_e, komas):
            txt = f'{cplayer}の勝ちです（2コマ以下）'
        init_flag = 1
    else:
        turns += 1

        s_or_e = 'S' if turns % 2 == 0 else 'E'
        cplayer = _get_cplayer(s_or_e)

        if turns % 2 != 0:
            t, ny, nx = _search_by_minmax(s_or_e, tagloc, komas, search_level, search_level, casyx)
            tagloc, komas, kihu = _chakusyu(t, ny, nx, tagloc, komas, casyx)
            turns, init_flag, txt, _tagloc, _komas, _kihu = _change_turn(turns, komas, tagloc, search_level, casyx)

    return turns, init_flag, txt, tagloc, komas, kihu


def _get_cplayer(s_or_e):
    cplayer = 'プレイヤー' if s_or_e == 'S' else 'コンピュータ'
    return cplayer


def _is_finish(s_or_e, komas, tagloc, casyx):
    return _is_under_two(s_or_e, komas) or _is_lost_whale(s_or_e, komas) or _is_tsumi(s_or_e, komas, tagloc, casyx)


def _is_under_two(s_or_e, komas):
    ops = 'E' if s_or_e == 'S' else 'S'
    komas_mod = komas[ops].reshape(1, (col + 1) * (row + 1))[0]
    cntr = 0
    for i in range(len(komas_mod)):
        if komas_mod[i] != 0:
            cntr += 1
    return cntr <= 2


def _is_tsumi(s_or_e, komas, tagloc, casyx):
    ops = 'E' if s_or_e == 'S' else 'S'
    tl = tagloc[ops]
    for tag, v in tl.items():
        act = _legal_actions(tag, tagloc, komas, casyx)
        for i in range(len(act)):
            ny, nx = act[i]
            if _check_kiki2whale(tag, ny, nx, tagloc, komas, 'legal_action', casyx) == False:
                return False
    return True


def _is_lost_whale(s_or_e, komas):
    ops = 'E' if s_or_e == 'S' else 'S'
    km = komas[ops]
    widx = np.where(km == 1)[0]
    if len(widx) == 0:
        return True
    return False


def _calc_value_from_tagloc(s_or_e, tl, km, casyx):
    ops = 'E' if s_or_e == 'S' else 'S'

    # 自分のコマ
    value1 = 0
    for k, v in tl[s_or_e].items():
        value1 += KomaValues[k[0]]
    # 敵のコマ
    value2 = 0
    for k, v in tl[ops].items():
        value2 += KomaValues[k[0]]
    v = value1 - value2

    if _is_under_two(s_or_e, km) or _is_tsumi(s_or_e, km, tl, casyx) or _is_lost_whale(s_or_e, km):
        v -= 100000
    if _is_under_two(ops, km) or _is_tsumi(ops, km, tl, casyx) or _is_lost_whale(ops, km):
        v += 100000
    return v


def _search_by_minmax(s_or_e, tlc, kmc, depth, search_level, casyx):
    tl = copy.deepcopy(tlc)
    km = copy.deepcopy(kmc)
    ops = 'E' if s_or_e == 'S' else 'S'
    arg = 'min' if s_or_e == 'S' else 'max'

    if depth == 0:
        currentv = _calc_value_from_tagloc(s_or_e, tl, km, casyx)
        return currentv
    else:
        acts, values, childvalues = [], [], []
        for tag, v in tl[s_or_e].items():
            legalact = _legal_actions(tag, tl, km, casyx)
            legalact = _eliminate_dangerous_actions(tag, legalact, tl, km, casyx)
            if len(legalact) != 0:
                for i in range(len(legalact)):
                    ny, nx = legalact[i]
                    acts.append([tag, ny, nx])
                    nexttl, nextkm = _get_next_state(tag, ny, nx, tl, km)
                    cv = _search_by_minmax(ops, nexttl, nextkm, depth - 1, search_level, casyx)
                    childvalues.append(cv)

        if len(childvalues) != 0:
            if arg == 'max':
                idx = np.where(childvalues == np.max(childvalues))[0]
            elif arg == 'min':
                idx = np.where(childvalues == np.min(childvalues))[0]
            idx = np.random.choice(idx)
            if depth == search_level:
                return acts[idx]
            return childvalues[idx]
        else:
            if arg == 'max':
                return -inf
            elif arg == 'min':
                return inf


def index(request):
    return render(request, 'index.html')


def init_data(request):
    col = 7
    row = 5

    nums = [1, 2, 2, 3, 3, 4, 4, 4]

    locs_self = np.array([[6, 3], [7, 1], [7, 5], [7, 2], [7, 4], [5, 1], [5, 3], [5, 5]])
    tags_self = ('W-S', 'F1-S', 'F2-S', 'C1-S', 'C2-S', 'T1-S', 'T2-S', 'T3-S')

    komas1 = np.zeros((col+1, row+1))
    for i in range(len(nums)):
        komas1[locs_self[i, 0], locs_self[i, 1]] = nums[i]

    locs_enemy = np.array([[2, 3], [1, 1], [1, 5], [1, 2], [1, 4], [3, 1], [3, 3], [3, 5]])
    tags_enemy = ('W-E', 'F1-E', 'F2-E', 'C1-E', 'C2-E', 'T1-E', 'T2-E', 'T3-E')

    komas2 = np.zeros((col+1, row+1))
    for i in range(len(nums)):
        komas2[locs_enemy[i, 0], locs_enemy[i][1]] = nums[i]

    request.session['init_flag'] = 0
    request.session['turns'] = 0
    request.session['col'] = col
    request.session['row'] = row
    request.session['tagloc'] = {'S': dict(zip(tags_self, locs_self.tolist())), 'E': dict(zip(tags_enemy, locs_enemy.tolist()))}
    request.session['komas'] = {'S': komas1.tolist(), 'E': komas2.tolist()}
    request.session['casyx'] = {'S': (6, 3), 'E': (2, 3)}
    request.session['search_level'] = request.GET.get('search_level')

    return JsonResponse(
        {
            'komas': request.session['komas'],
            'tagloc': request.session['tagloc'],
            'init_flag': 0,
            'message': '',
        },
        safe=True
    )


def legal_actions(request):
    tag = request.GET.get('tag')
    tl = _tagloc_from_json(request.session['tagloc'])
    km = _komas_from_json(request.session['komas'])
    casyx = request.session['casyx']

    actions = _legal_actions(tag, tl, km, casyx)
    actions = _eliminate_dangerous_actions(tag, actions, tl, km, casyx)

    return_actions = []
    for i in actions:
        x = []
        for j in i:
            x.append(int(j))
        return_actions.append(x)

    return JsonResponse(return_actions, safe=False)


def press_legal_actions(request):
    tag = request.GET.get('tag')
    ny = request.GET.get('ny')
    nx = request.GET.get('nx')
    tagloc = _tagloc_from_json(request.session['tagloc'])
    komas = _komas_from_json(request.session['komas'])
    casyx = request.session['casyx']
    search_level = int(request.session['search_level'])

    pos = [int(ny), int(nx)]

    tagloc, komas, kihu_1 = _chakusyu(tag, pos[0], pos[1], tagloc, komas, casyx)

    turns, init_flag, txt, tagloc, komas, kihu_2 = _change_turn(request.session['turns'], komas, tagloc, search_level, casyx)

    request.session['tagloc'] = _tagloc_to_json(tagloc)
    request.session['komas'] = _komas_to_json(komas)
    request.session['turns'] = turns
    request.session['init_flag'] = init_flag

    return JsonResponse({
        'komas': _komas_to_json(komas),
        'tagloc': _tagloc_to_json(tagloc),
        'init_flag': request.session['init_flag'],
        'message': txt,
        'kihu': [kihu_1, kihu_2],
    })

# ============== Online game ==============
def legal_actions_online(request):
    request.session['casyx'] = {'S': (6, 3), 'E': (2, 3)}
    data = json.loads(request.GET.get('data'))
    request.session['tagloc'] = data['tagloc']
    request.session['komas'] = data['komas']
    # -------------------------
    tag = request.GET.get('tag')
    tl = _tagloc_from_json(request.session['tagloc'])
    km = _komas_from_json(request.session['komas'])
    casyx = request.session['casyx']

    actions = _legal_actions(tag, tl, km, casyx)
    actions = _eliminate_dangerous_actions(tag, actions, tl, km, casyx)

    return_actions = []
    for i in actions:
        x = []
        for j in i:
            x.append(int(j))
        return_actions.append(x)

    return JsonResponse(return_actions, safe=False)

def check_win(request):
    txt = ''
    data = json.loads(request.GET.get('data'))
    tagloc = data['tagloc']
    komas = {
        'S': np.array(data['komas']['S']),
        'E': np.array(data['komas']['E']),
    }
    casyx = {'S': (6, 3), 'E': (2, 3)}
    s_or_e = 'S'
    cplayer = _get_cplayer(s_or_e)

    if _is_finish(s_or_e, komas, tagloc, casyx):
        if _is_lost_whale(s_or_e, komas):
            txt = f'{cplayer}の勝ちです（クジラ奪取）'
        elif _is_tsumi(s_or_e, komas, tagloc, casyx):
            txt = f'{cplayer}の勝ちです（詰み）'
        elif _is_under_two(s_or_e, komas):
            txt = f'{cplayer}の勝ちです（2コマ以下）'

    return JsonResponse({
        'message': txt,
    })