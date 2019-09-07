# -*- coding: utf-8 -*-

import re
PASS_FLAG = '    PASS    '
FAIL_FLAG = '--- FAIL ---'

def assert_equal(expected, actual, message='', verbose=True):
    passed = expected == actual

    if verbose:
        if passed:
            print(PASS_FLAG, message)
        else:
            details = '\tExpected [{expected}] but got [{actual}]'
            details = details.format(expected=expected, actual=actual)
            print(FAIL_FLAG, message)
            print(details)

    return passed

def assert_approx(expected, actual, max_difference, message='', verbose=True):
    passed = abs(expected - actual) <= max_difference

    if verbose:
        if passed:
            print(PASS_FLAG, message)
        else:
            details = '\tExpected [{expected} (± {max_difference})] but got [{actual}]'
            details = details.format(expected=expected, max_difference=max_difference, actual=actual)
            print(FAIL_FLAG, message)
            print(details)

    return passed

def assert_similar_text(expected, actual, message='', verbose=True):
    pattern_string = "(?i)(" + expected + "?.*)(?:\n|$)"
    pattern = re.compile(pattern_string)
    parts = pattern.findall(actual)
    
    passed = len(parts) > 0
    if verbose:
        if passed:
            print(PASS_FLAG, message)
        else:
            details = '\tExpected [{expected}] but got [{actual}]'
            details = details.format(expected=expected, actual=actual)
            print(FAIL_FLAG, message)
            print(details)
    return passed

def assert_true(value, message='', verbose=True):
    passed = value == True

    if verbose:
        if passed:
            print(PASS_FLAG, message)
        else:
            print(FAIL_FLAG, message)

    return passed

def assert_false(value, message='', verbose=True):
    passed = value == False

    if verbose:
        if passed:
            print(PASS_FLAG, message)
        else:
            print(FAIL_FLAG, message)

    return passed

def assert_in(good_list, actual, message='', verbose=True):
    passed = actual in good_list

    if verbose:
        if passed:
            print(PASS_FLAG, message)
        else:
            details = '\tActual [{actual}] not an acceptable value: {good_list}'
            details = details.format(actual=actual, good_list=good_list)
            print(FAIL_FLAG, message)
            print(details)

    return passed

def assert_not_in(bad_list, actual, message='', verbose=True):
    passed = actual not in bad_list

    if verbose:
        if passed:
            print(PASS_FLAG, message)
        else:
            details = '\tActual [{actual}] is in an unacceptable value: {bad_list}'
            details = details.format(actual=actual, bad_list=bad_list)
            print(FAIL_FLAG, message)
            print(details)

    return passed

def assert_in_range(min_acceptible, max_acceptible, actual, message='', verbose=True):
    passed = min_acceptible <= actual <= max_acceptible

    if verbose:
        if passed:
            print(PASS_FLAG, message)
        else:
            details = '\tActual [{actual}] not in valid range [{min_acceptible} thru {max_acceptible}]'
            details = details.format(actual=actual, min_acceptible=min_acceptible, max_acceptible=max_acceptible)
            print(FAIL_FLAG, message)
            print(details)

    return passed
