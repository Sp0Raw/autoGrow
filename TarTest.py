import tarantool
##server = tarantool.connect("10.242.4.109", 3301)


connection = tarantool.connect("127.0.0.1", 3302)
type(connection)
#<class 'tarantool.connection.Connection'>

# schema = {
#     0: { # Space description
#         'name': 'users', # Space name
#         'default_type': tarantool.  , # Type that used to decode fields that are not listed below
#         'fields': {
#             0: ('user_id', tarantool.NUM), # (field name, field type)
#             1: ('num64field', tarantool.NUM64),
#             2: ('strfield', tarantool.STR),
#             #2: { 'name': 'strfield', 'type': tarantool.STR }, # Alternative syntax
#             #2: tarantool.STR # Alternative syntax
#         },
#         'indexes': {
#             0: ('pk', [0]), # (name, [field_no])
#             #0: { 'name': 'pk', 'fields': [0]}, # Alternative syntax
#             #0: [0], # Alternative syntax
#         }
#     }
# }
# connection = tarantool.connect(host = 'http://10.242.4.109', port=3301, schema = schema)

# demo = connection.space('users')
# demo.insert((0, 12, u'this is unicode string'))
# demo.select(0)
##[(0, 12, u'this is unicode string')]