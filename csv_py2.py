# -*- encoding: utf-8 -*-
from __future__ import print_function
import codecs
import csv
import pytest
import unicodecsv

from StringIO import StringIO


SIMPLE_DATA = '''field1,field2
1.1,1.2
2.1,2.2
'''

UNICODE_DATA = u'''field1,field2
mehr ümlaute,für die welt
'''


def test_simple_read():
    """
    The simple reader is just that. It converts rows into lists
    and that's about it.
    """
    data = []
    for row in csv.reader(StringIO(SIMPLE_DATA)):
        data.append(row)

    # We get 3 datasets because the header is not automatically skipped
    assert 3 == len(data)

    # The first row contains the headers
    assert ['field1', 'field2'] == data[0]

    # And the rows after that contain the data
    assert [['1.1', '1.2'], ['2.1', '2.2']] == data[1:]


def test_dict_read():
    """
    The DictReader by default uses the content of the first row to
    create dictionaries for each row to access each field by name.
    """
    data = [row for row in csv.DictReader(StringIO(SIMPLE_DATA))]

    # Since the first row is consumed to detect the column names, we
    # only get 2 datasets.
    assert 2 == len(data)

    assert '1.1' == data[0]['field1']
    assert '2.2' == data[1]['field2']


def test_dict_read_custom_fieldnames():
    """
    The DictReader by default uses the content of the first row to
    create dictionaries for each row to access each field by name.
    """
    data = [row for row in csv.DictReader(StringIO(SIMPLE_DATA),
        fieldnames=['fielda', 'fieldb'])]

    # If you provide your own fieldnames, you get the first line
    # also as dataset
    assert 3 == len(data)

    assert '1.1' == data[1]['fielda']
    assert '2.2' == data[2]['fieldb']


def test_read_unicode_unsupported(tmpdir):
    """
    By default, the csv.reader doesn't support decoding of unicode values
    but instead returns bytestrings. And if you try to hand it a unicode
    data source, it just dies during decoding.
    """
    test_file = unicode(tmpdir.join("unicode.csv"))
    with codecs.open(test_file, 'wb+', encoding='utf-8') as fp:
        fp.write(UNICODE_DATA)

    with open(test_file, 'rb') as fp:
        data = [row for row in csv.reader(fp)]
        assert data[1][0] != u'mehr ümlaute'

    with codecs.open(test_file, 'rb', encoding='utf-8') as fp:
        with pytest.raises(UnicodeEncodeError):
            [row for row in csv.reader(fp)]


def test_reader_unicode_workaround(tmpdir):
    """
    To get around this issue there is an example in the docs
    (http://docs.python.org/2.7/library/csv.html#csv-examples) or unicodecsv.
    Note that you only need this if you're using Python 2.x. In 3.x this
    is fixed.

    Sadly, this doesn't get around the unicode datasource issue, though.
    """
    test_file = unicode(tmpdir.join("unicode.csv"))
    with codecs.open(test_file, 'wb+', encoding='utf-8') as fp:
        fp.write(UNICODE_DATA)

    with open(test_file, 'rb') as fp:
        data = [row for row in unicodecsv.reader(fp)]
        assert data[1][0] == u'mehr ümlaute'

    with codecs.open(test_file, 'rb', encoding='utf-8') as fp:
        with pytest.raises(UnicodeEncodeError):
            [row for row in csv.reader(fp)]


def test_simple_write(custom_dialect):
    """
    Writing is basically just creating a writer with an output file-like
    object and then calling writerow repeatedly on it with the row data.

    In this example I also use a custom dialect to change the line ending
    to the unix format.
    """
    output = StringIO()
    writer = csv.writer(output, dialect='custom')
    writer.writerow(['field1', 'field2'])
    writer.writerow(['1.1', '1.2'])
    writer.writerow(['2.1', '2.2'])
    assert SIMPLE_DATA == output.getvalue()


def test_write_quoting():
    """
    Especially for writing content CSV has specific quoting rules. For
    instance if you want to quote everything including numeric values,
    you can absolutely do that.
    """
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow([1, 1.2])
    assert '''"1","1.2"\r\n''' == output.getvalue()

    # Or don't quote them
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow([1, 1.2])
    assert '''1,1.2\r\n''' == output.getvalue()

    # Or quote only if it would otherwise confuse the parser
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["1,2", 1])
    assert '''"1,2",1\r\n''' == output.getvalue()

    # If we select QUOTE_NONE, then we should (and in this case must)
    # set an escape character to prevent the generation of invalid output.
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONE, escapechar='|')
    writer.writerow(["1,2", 1])
    assert '''1|,2,1\r\n''' == output.getvalue()


def test_evil_readability_fail():
    """
    If after the separator a whitespace appears, make sure that the result
    is actually what you expect.
    """
    test_data = '''"Expert python", "Trust me, I'm an expert"'''
    result = []
    for line in csv.reader(StringIO(test_data), quotechar='"',
            quoting=csv.QUOTE_ALL,
            # skipinitialspace is necessary here to prevent the parser to
            # create 3 records.
            skipinitialspace=True):
        result.append(line)
    assert 1 == len(result)
    assert 2 == len(result[0])


@pytest.fixture
def custom_dialect(request):
    """
    Register your own little dialect that for instance uses \n as line
    terminator instead of \r\n which is the default.
    """
    def cleanup():
        csv.unregister_dialect('custom')
    csv.register_dialect('custom', lineterminator='\n', delimiter=',')
    request.addfinalizer(cleanup)


def test_dialect_sniffer():
    """
    The csv package also comes with a helper to detect the dialect used
    in a given file by checking the actual data. Here it usually makes
    sense to probe the file and check like the first K or so.
    """
    simple_file = '''field1;field2\n1.1;1.2\n2.1;2.2'''
    # Let's make sure that this is actually a format that *can* be parsed:
    assert len(list(csv.reader(StringIO(simple_file)))) == 3

    dialect = csv.Sniffer().sniff(simple_file)

    # It correctly detects the delimiter
    assert ';' == dialect.delimiter

    # Sadly the sniffer isn't really good at detecting the line ending
    assert '\n' != dialect.lineterminator