from app.models.utils import short_id


def test_short_id_generation():
    id1 = short_id()
    id2 = short_id()
    assert id1 != id2
    assert len(id1) == 8
    assert len(id2) == 8


def test_short_id_with_prefix():
    prefix = "test_"
    id1 = short_id(prefix=prefix)
    id2 = short_id(prefix=prefix)
    assert id1.startswith(prefix)
    assert id2.startswith(prefix)
    assert id1 != id2
    assert len(id1) == len(prefix) + 8
    assert len(id2) == len(prefix) + 8


def test_short_id_custom_length():
    length = 12
    id1 = short_id(length=length)
    id2 = short_id(length=length)
    assert len(id1) == length
    assert len(id2) == length
    assert id1 != id2
