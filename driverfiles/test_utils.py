#!/usr/bin/python
"""test_utils module"""

def assert_equal(ground_truth, value):
    """Check for equality between two objects"""

    if ground_truth != value:
        raise Exception("Assert Equal Fail: '%s' should equal '%s' but it doesn't." % (value, ground_truth))

def assert_in(value, search_list):
    """Assert that a provided value is in a given list"""

    if value not in search_list:
        raise Exception("Assert In Fail: Could not find object '%s' in list '%s'" % (value, search_list))

def assert_equal_len(lista, listb):

    if len(lista) != len(listb):
        raise Exception("Assert Equal Len Fail: Lists were different sizes. (%d, %d) ('%s', '%s')" % (len(lista), len(listb), lista, listb))    
