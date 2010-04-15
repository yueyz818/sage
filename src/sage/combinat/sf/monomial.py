"""
Monomial symmetric functions
"""
#*****************************************************************************
#       Copyright (C) 2007 Mike Hansen <mhansen@gmail.com>,
#                     2010 Anne Schilling <anne at math.ucdavis.edu> (addition)
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import classical, sfa, dual
import sage.libs.symmetrica.all as symmetrica
from sage.rings.all import ZZ, QQ, Integer, PolynomialRing
from sage.combinat.partition import Partition, Partitions

class SymmetricFunctionAlgebra_monomial(classical.SymmetricFunctionAlgebra_classical):
    def __init__(self, R):
        """
        TESTS::

            sage: m = SFAMonomial(QQ)
            sage: m == loads(dumps(m))
            True
        """
        classical.SymmetricFunctionAlgebra_classical.__init__(self, R, "monomial", 'm')

    def dual_basis(self, scalar=None, scalar_name="",  prefix=None):
        """
        The dual basis of the monomial basis with respect to the standard
        scalar product is the homogeneous basis.

        EXAMPLES::

            sage: m = SFAMonomial(QQ)
            sage: h = SFAHomogeneous(QQ)
            sage: m.dual_basis() == h
            True
        """
        if scalar is None:
            return sfa.SFAHomogeneous(self.base_ring())
        else:
            return dual.SymmetricFunctionAlgebra_dual(self, scalar, scalar_name, prefix)


    def _multiply(self, left, right):
        """
        EXAMPLES::

            sage: m = SFAMonomial(QQ)
            sage: a = m([2,1])
            sage: a^2
            4*m[2, 2, 1, 1] + 6*m[2, 2, 2] + 2*m[3, 2, 1] + 2*m[3, 3] + 2*m[4, 1, 1] + m[4, 2]

        ::

            sage: QQx.<x> = QQ['x']
            sage: m = SFAMonomial(QQx)
            sage: a = m([2,1])+x
            sage: 2*a # indirect doctest
            2*x*m[] + 2*m[2, 1]
            sage: a^2
            x^2*m[] + 2*x*m[2, 1] + 4*m[2, 2, 1, 1] + 6*m[2, 2, 2] + 2*m[3, 2, 1] + 2*m[3, 3] + 2*m[4, 1, 1] + m[4, 2]
        """
        #Use symmetrica to do the multiplication
        A = left.parent()
        R = A.base_ring()

        #Hack due to symmetrica crashing when both of the
        #partitions are the empty partition
        #if  R is ZZ or R is QQ:
        #    return symmetrica.mult_monomial_monomial(left, right)

        z_elt = {}
        for (left_m, left_c) in left._monomial_coefficients.iteritems():
            for (right_m, right_c) in right._monomial_coefficients.iteritems():

                #Hack due to symmetrica crashing when both of the
                #partitions are the empty partition
                if left_m == [] and right_m == []:
                    z_elt[ left_m ] = left_c*right_c
                    continue

                d = symmetrica.mult_monomial_monomial({left_m:Integer(1)}, {right_m:Integer(1)}).monomial_coefficients()
                for m in d:
                    if m in z_elt:
                        z_elt[ m ] = z_elt[m] + left_c * right_c * d[m]
                    else:
                        z_elt[ m ] = left_c * right_c * d[m]
        return z_elt

    def from_polynomial(self, f, check=True):
        """
        This function converts a symmetric polynomial `f` in a polynomial ring in finitely
        many variables to a symmetric function in the monomial
        basis of the ring of symmetric functions over the same base ring.

        EXAMPLES::

            sage: P = PolynomialRing(QQ, 'x', 3)
            sage: x = P.gens()
            sage: f = x[0] + x[1] + x[2]
            sage: m = SFAMonomial(QQ)
            sage: m.from_polynomial(f)
            m[1]
            sage: f = x[0]**2+x[1]**2+x[2]**2
            sage: m.from_polynomial(f)
            m[2]
            sage: f=x[0]^2+x[1]
            sage: m.from_polynomial(f)
            Traceback (most recent call last):
            ...
            ValueError: x0^2 + x1 is not a symmetric polynomial
            sage: f = (m[2,1]+m[1,1]).expand(3)
            sage: m.from_polynomial(f)
            m[1, 1] + m[2, 1]
            sage: f = (2*m[2,1]+m[1,1]+3*m[3]).expand(3)
            sage: m.from_polynomial(f)
            m[1, 1] + 2*m[2, 1] + 3*m[3]
        """
        assert self.base_ring() == f.base_ring()
        d = dict([(e,c) for e,c in f.dict().iteritems() if tuple(sorted(e)) == tuple(reversed(e))])
        out = self.sum(d[la]*self(Partition(la)) for la in d.keys())
        if check and out.expand(f.parent().ngens(),f.parent().gens()) <> f:
            raise ValueError, "%s is not a symmetric polynomial"%f
        return out


    class Element(classical.SymmetricFunctionAlgebra_classical.Element):
        def expand(self, n, alphabet='x'):
            """
            Expands the symmetric function as a symmetric polynomial in n
            variables.

            EXAMPLES::

                sage: m = SFAMonomial(QQ)
                sage: m([2,1]).expand(3)
                x0^2*x1 + x0*x1^2 + x0^2*x2 + x1^2*x2 + x0*x2^2 + x1*x2^2
                sage: m([1,1,1]).expand(2)
                0
                sage: m([2,1]).expand(3,alphabet='z')
                z0^2*z1 + z0*z1^2 + z0^2*z2 + z1^2*z2 + z0*z2^2 + z1*z2^2
                sage: m([2,1]).expand(3,alphabet='x,y,z')
                x^2*y + x*y^2 + x^2*z + y^2*z + x*z^2 + y*z^2
            """
            condition = lambda part: len(part) > n
            return self._expand(condition, n, alphabet)

# Backward compatibility for unpickling
from sage.structure.sage_object import register_unpickle_override
register_unpickle_override('sage.combinat.sf.monomial', 'SymmetricFunctionAlgebraElement_monomial',  SymmetricFunctionAlgebra_monomial.Element)
