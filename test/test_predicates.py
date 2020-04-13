from svnlog.predicates import both, either, negate, always_true, always_false


def test_matches_if_both_matched():
    assert both(always_true, always_true)(any)
    assert not both(always_true, always_false)(any)
    assert not both(always_false, always_true)(any)
    assert not both(always_false, always_false)(any)
    assert both(always_true, None)(any)
    assert both(None, None)(any)


def test_matches_if_either_matched():
    assert either(always_true, always_true)(any)
    assert either(always_true, always_false)(any)
    assert either(always_false, always_true)(any)
    assert not either(always_false, always_false)(any)
    assert either(None, always_true)(any)
    assert not either(None, always_false)(any)


def test_negate_matcher():
    assert negate(always_false)(any)
    assert not negate(always_true)(any)
    assert not negate(None)(any)
