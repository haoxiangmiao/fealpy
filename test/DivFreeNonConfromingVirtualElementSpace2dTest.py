#!/usr/bin/env python3
# 
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import spdiags, bmat
from scipy.sparse.linalg import spsolve

from fealpy.functionspace import DivFreeNonConformingVirtualElementSpace2d
from fealpy.functionspace import ScaledMonomialSpace2d
from fealpy.mesh.simple_mesh_generator import triangle
from fealpy.mesh import PolygonMesh, QuadrangleMesh
from fealpy.pde.poisson_2d import CosCosData

class DivFreeNonConformingVirtualElementSpace2dTest:

    def __init__(self, p=2, h=0.2):
        self.pde = CosCosData()

    def index1_test(self, p=2):
        node = np.array([
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)], dtype=np.float)
        cell = np.array([0, 1, 2, 3], dtype=np.int)
        cellLocation = np.array([0, 4], dtype=np.int)
        mesh = PolygonMesh(node, cell, cellLocation)
        space = DivFreeNonConformingVirtualElementSpace2d(mesh, 3)
        idx = space.index1(p=p)
        print("p=", p, idx)

    def index2_test(self, p=2):
        node = np.array([
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)], dtype=np.float)
        cell = np.array([0, 1, 2, 3], dtype=np.int)
        cellLocation = np.array([0, 4], dtype=np.int)
        mesh = PolygonMesh(node, cell, cellLocation)
        space = DivFreeNonConformingVirtualElementSpace2d(mesh, 3)
        idx = space.index2(p=p)
        print("p=", p, idx)

    def matrix_test(self, p=2):
        """
        node = np.array([
            (-1.0, -1.0),
            ( 0.0, -1.0),
            ( 1.0, -1.0),
            (-1.0, 0.0),
            ( 1.0, 0.0),
            (-1.0, 1.0),
            ( 0.0, 1.0),
            ( 1.0, 1.0)], dtype=np.float)
        cell = np.array([0, 1, 2, 4, 7, 6, 5, 3], dtype=np.int)
        cellLocation = np.array([0, 8], dtype=np.int)
        mesh = PolygonMesh(node, cell, cellLocation)
        """

        node = np.array([
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)], dtype=np.float)
        cell = np.array([0, 1, 2, 3], dtype=np.int)
        cellLocation = np.array([0, 4], dtype=np.int)
        mesh = PolygonMesh(node, cell, cellLocation)
        space = DivFreeNonConformingVirtualElementSpace2d(mesh, p)
        print("G:", space.G)
        print("B:", space.B)
        print("R:", space.R)
        print("J:", space.J)
        print("Q:", space.Q)
        print("L:", space.L)
        print("D:", space.D)

    def matrix_A_test(self, p=2):
        node = np.array([
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)], dtype=np.float)
        cell = np.array([0, 1, 2, 3], dtype=np.int)
        cellLocation = np.array([0, 4], dtype=np.int)
        mesh = PolygonMesh(node, cell, cellLocation)
        space = DivFreeNonConformingVirtualElementSpace2d(mesh, p)
        A = space.matrix_A()
        print(A)

    def matrix_P_test(self, p=2):
        node = np.array([
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)], dtype=np.float)
        cell = np.array([0, 1, 2, 3], dtype=np.int)
        cellLocation = np.array([0, 4], dtype=np.int)
        mesh = PolygonMesh(node, cell, cellLocation)
        space = DivFreeNonConformingVirtualElementSpace2d(mesh, p)
        P = space.matrix_P()
        print(P)

    def stokes_equation_test(self, p=2, maxit=4):
        from scipy.sparse import bmat
        from fealpy.pde.Stokes_Model_2d import CosSinData
        from fealpy.mesh.simple_mesh_generator import triangle
        h = 0.1
        pde = CosSinData()
        domain = pde.domain()
        error = np.zeros((maxit,), dtype=np.float)
        for i in range(maxit):
            mesh = triangle(domain, h, meshtype='polygon')

            if 0:
                fig = plt.figure()
                axes = fig.gca()
                mesh.add_plot(axes)
                plt.show()

            uspace = DivFreeNonConformingVirtualElementSpace2d(mesh, p)
            pspace = ScaledMonomialSpace2d(mesh, p-1)

            isBdDof = uspace.boundary_dof()

            udof = uspace.number_of_global_dofs()
            pdof = pspace.number_of_global_dofs()

            uh = uspace.function()
            ph = pspace.function()
            uspace.set_dirichlet_bc(uh, pde.dirichlet)

            A = uspace.matrix_A()
            P = uspace.matrix_P()
            F = uspace.source_vector(pde.source)


            AA = bmat([[A, P.T], [P, None]], format='csr')
            FF = np.block([F, np.zeros(pdof, dtype=uspace.ftype)])
            x = np.block([uh.T.flat, ph])
            isBdDof = np.block([isBdDof, isBdDof, np.zeros(pdof, dtype=np.bool)])

            gdof = 2*udof + pdof
            FF -= AA@x
            bdIdx = np.zeros(gdof, dtype=np.int)
            bdIdx[isBdDof] = 1
            Tbd = spdiags(bdIdx, 0, gdof, gdof)
            T = spdiags(1-bdIdx, 0, gdof, gdof)
            AA = T@AA@T + Tbd
            FF[isBdDof] = x[isBdDof]
            x[:] = spsolve(AA, FF)
            uh[:, 0] = x[:udof]
            uh[:, 1] = x[udof:2*udof]
            ph[:] = x[2*udof:]

            up = uspace.project(pde.velocity)
            up = uspace.project_to_smspace(up)
            integralalg = uspace.integralalg
            error[i] = integralalg.L2_error(pde.velocity, up)
            h /= 2

        print(error)
        print(error[0:-1]/error[1:])

    def project_test(self, u, p=2, mtype=0, plot=True):
        from fealpy.mesh.simple_mesh_generator import triangle

        if mtype == 0:
            node = np.array([
                (-1, -1), (1, -1), (1, 1), (-1, 1)], dtype=np.float)
            cell = np.array([0, 1, 2, 3], dtype=np.int)
            cellLocation = np.array([0, 4], dtype=np.int)
            mesh = PolygonMesh(node, cell, cellLocation)
        elif mtype == 1:
            node = np.array([
                (-1, -1), (1, -1), (1, 1), (-1, 1)], dtype=np.float)
            cell = np.array([0, 1, 2, 3, 0, 2], dtype=np.int)
            cellLocation = np.array([0, 3, 6], dtype=np.int)
            mesh = PolygonMesh(node, cell, cellLocation)
        elif mtype == 2:
            h = 0.1
            mesh = triangle([-1, 1, -1, 1], h, meshtype='polygon')
        elif mtype == 3:
            node = np.array([
                (-1, -1), (1, -1), (1, 1), (-1, 1)], dtype=np.float)
            cell = np.array([[0, 1, 2, 3]], dtype=np.int)
            mesh = QuadrangleMesh(node, cell)
            mesh.uniform_refine()
            mesh = PolygonMesh.from_mesh(mesh)


        cell, cellLocation = mesh.entity('cell')
        edge = mesh.entity('edge')
        cell2edge = mesh.ds.cell_to_edge()
        uspace = DivFreeNonConformingVirtualElementSpace2d(mesh, p)
        up = uspace.project(u)
        up = uspace.project_to_smspace(up)

        integralalg = uspace.integralalg
        error = integralalg.L2_error(u, up)
        print(error)
        if plot:
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            mesh.find_node(axes, showindex=True)
            mesh.find_edge(axes, showindex=True)
            mesh.find_cell(axes, showindex=True)
            plt.show()
def u2(p):
    x = p[..., 0]
    y = p[..., 1]
    val = np.zeros(p.shape, p.dtype)
    val[..., 0] = y**2/4
    val[..., 1] = x**2/4
    return val

def u3(p):
    x = p[..., 0]
    y = p[..., 1]
    val = np.zeros(p.shape, p.dtype)
    val[..., 0] = y**3/8
    val[..., 1] = x**3/8
    return val

test = DivFreeNonConformingVirtualElementSpace2dTest()
#test.index1_test(p=1)
#test.index1_test(p=2)
#test.index1_test(p=3)
#test.index2_test(p=3)
#test.index2_test(p=4)
#test.test_matrix(p=2)
#test.test_matrix_A()
#test.test_matrix_P()
test.project_test(u2, p=2, mtype=0, plot=False)
#test.project_test(u3, p=3, mtype=3, plot=False)
#test.stokes_equation_test()
