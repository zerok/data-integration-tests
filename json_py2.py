import collections
import json


python_data = {
    'title': 'PyGRAZ Meetup 2013.11',
    'location': {
        'name': 'Spektral'
    },
    'participants': ['Horst Gutmann', 'Thomas Aglassinger', 'you']
}

sorted_python_data = collections.OrderedDict()
sorted_python_data['title'] = 'PyGRAZ Meetup 2013.11'
sorted_python_data['location'] = {'name': 'Spektral'}
sorted_python_data['participants'] = ['Horst Gutmann', 'Thomas Aglassinger', 'you']


def test_dumps_without_indent():
    expected = """{"participants": ["Horst Gutmann", "Thomas Aglassinger", "you"], "location": {"name": "Spektral"}, "title": "PyGRAZ Meetup 2013.11"}"""
    assert json.dumps(python_data) == expected

def test_dump_with_indent():
    expected = '''{
    "participants": [
        "Horst Gutmann",
        "Thomas Aglassinger",
        "you"
    ],
    "location": {
        "name": "Spektral"
    },
    "title": "PyGRAZ Meetup 2013.11"
}'''
    # By default the separator always has a space trailing which we don't
    # want for the item separator but do for the key-value one.
    assert json.dumps(python_data, indent=4,
        separators=(',', ': ')) == expected


def test_dump_with_sorted_order():
    expected = '''{
    "title": "PyGRAZ Meetup 2013.11",
    "location": {
        "name": "Spektral"
    },
    "participants": [
        "Horst Gutmann",
        "Thomas Aglassinger",
        "you"
    ]
}'''
    assert json.dumps(sorted_python_data, indent=4, 
        separators=(',', ': ')) == expected


def test_load_with_sorted_order():
    input_data = '''{
    "title": "PyGRAZ Meetup 2013.11",
    "location": {
        "name": "Spektral"
    },
    "participants": [
        "Horst Gutmann",
        "Thomas Aglassinger",
        "you"
    ]
}'''
    assert sorted_python_data == json.loads(input_data,
        object_pairs_hook=collections.OrderedDict)


def test_dump_with_encoder():
    class CustomEncoder(json.JSONEncoder):
        def __init__(self, *args, **kwargs):
            super(CustomEncoder, self).__init__(*args, **kwargs)
            self.item_separator = ','
            self.indent = 4
    expected = '''{
    "title": "PyGRAZ Meetup 2013.11",
    "location": {
        "name": "Spektral"
    },
    "participants": [
        "Horst Gutmann",
        "Thomas Aglassinger",
        "you"
    ]
}'''
    assert expected == CustomEncoder().encode(sorted_python_data)
    assert expected == json.dumps(sorted_python_data, cls=CustomEncoder)
