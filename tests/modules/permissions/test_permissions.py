from donut.testing.fixtures import client
from donut.modules.permissions.helpers import has_permission


def test_has_permission(client):
    # user csander is ruddock full member
    assert has_permission(3, 1)
    # user reng is IHC member (through pos relation)
    assert has_permission(2, 2)
    # user syu is not head of devteam
    assert not has_permission(4, 1)
    # test bad inputs
    assert not has_permission(0, 0)
    assert not has_permission('bogus', 'inputs')
