import unittest
from pxr import Usd, Sdf, Kind


s = Usd.Stage.CreateInMemory('TestModelKind.'+'usda')
p = s.DefinePrim('/World', 'Xform')
model = Usd.ModelAPI(p)
model.SetKind(Kind.Tokens.assembly)
print(model.GetKind())
print(model.IsModel())
print(model.IsGroup())
# self.assertEqual(model.GetKind(), '')
# self.assertFalse(model.IsModel())
# self.assertFalse(model.IsGroup())
#
# self.assertEqual(model.GetKind(), Kind.Tokens.assembly)
# self.assertTrue(model.IsModel())
# self.assertTrue(model.IsGroup())