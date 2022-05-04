from collections import OrderedDict

print("Before deleting:\n")
od = OrderedDict()
od['2022-03-26'] = 1
od['2022-02-26'] = 2
od['2022-03-05'] = 3
od['2022-03-12'] = 4

new_list = sorted(od.items(), key=lambda x: x[0])
print("Sorted keys", new_list)

for key, value in od.items():
    print(key, value)

print("\nAfter deleting:\n")
od.pop('2022-03-05')
for key, value in od.items():
    print(key, value)

print("\nAfter re-inserting:\n")
od['2021-10-23'] = 3
for key, value in od.items():
    print(key, value)