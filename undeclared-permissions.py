from xml.dom.minidom import parseString

data = '' # string data from file
with open('AndroidManifest.xml', 'r') as f:
    data = f.read()
      
dom = parseString(data)
nodes = dom.getElementsByTagName('uses-permission') # xml nodes named "uses-permission"
nodes+= dom.getElementsByTagName('permission')
activities = dom.getElementsByTagName('activity')
providers = dom.getElementsByTagName('provider')
receivers = dom.getElementsByTagName('receiver')
services = dom.getElementsByTagName('service')

print("")
print("======Permissions Used======")
print("")

permissions1 = [] # holder for all permissions as we gather them
# Iterate over all the uses-permission nodes
for node in nodes:
    permissions1 += [node.getAttribute("android:name")] # save permissionName to our list

permission_list1 = list(set(permissions1))


for permission_sorted_1 in sorted(permission_list1): # sort permissions and iterate
    print(permission_sorted_1) # print permission name


print("")
print("======Permissions Declared in IPC Components======")
print("")

permissions2 = []

for activity in activities:
	if activity.getAttribute("android:permission"):
		permissions2 += [activity.getAttribute('android:permission')]

for provider in providers:
	if provider.getAttribute("android:permission"):
		permissions2 += [provider.getAttribute('android:permission')]

	if provider.getAttribute("android:readPermission"):
		#permissions2 += [provider.getAttribute('android:permission')]
		permissions2 += [provider.getAttribute('android:readPermission')]


for receiver in receivers:
	if receiver.getAttribute("android:permission"):
		permissions2 += [receiver.getAttribute('android:permission')]

for service in services:
	if service.getAttribute("android:permission"):
		permissions2 += [service.getAttribute('android:permission')]

# Print sorted list
permission_list2 = list(set(permissions2))


for permission_sorted_2 in sorted(permission_list2): # sort permissions and iterate
    print(permission_sorted_2) # print permission name


print("")
print("======Undeclared Permissions======")
print("")

undeclared_list = []
for element in permissions2:
	if element not in permissions1:
		undeclared_list.append(element)

undeclared = list(set(undeclared_list))

for undeclared_sorted in sorted(undeclared): # sort permissions and iterate
    print(undeclared_sorted) # print permission name