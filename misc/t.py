step = 1000
keys_lv1 = zip(range(0, 9000, step), range(1000, 10000, step))
for key_lv1 in keys_lv1:
    start = key_lv1[0]
    end = key_lv1[1]
    print('\n', start, end)
    step_lv2 = 100
    keys_lv2 = zip(range(start, end - step_lv2, step_lv2),
                   range(start + step_lv2, end, step_lv2))
    for key_lv2 in keys_lv2:
        print(key_lv2)
