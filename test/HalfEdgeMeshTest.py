#!/usr/bin/env python3
# 
import numpy as np
import matplotlib.pyplot as plt

from fealpy.mesh import PolygonMesh, HalfEdgeMesh


class HalfEdgePolygonMeshTest:

    def __init__(self):
        pass



    def refine_test(self, plot=True):
        node = np.array([
            (0.0, 0.0), (0.0, 1.0), (0.0, 2.0),
            (1.0, 0.0), (1.0, 1.0), (1.0, 2.0),
            (2.0, 0.0), (2.0, 1.0), (2.0, 2.0)], dtype=np.float)
        cell = np.array([0, 3, 4, 4, 1, 0,
            1, 4, 5, 2, 3, 6, 7, 4, 4, 7, 8, 5], dtype=np.int)
        cellLocation = np.array([0, 3, 6, 10, 14, 18], dtype=np.int)

        mesh = PolygonMesh(node, cell, cellLocation)
        mesh = HalfEdgeMesh.from_polygonmesh(mesh)

        NE = mesh.number_of_edges()
        NC = mesh.number_of_cells()
        
        if True:
            isMarkedCell = np.zeros(NC+1, dtype=np.bool)
            isMarkedCell[2] = True
            mesh.refine(isMarkedCell, dflag=False)
        
        if True:
            NC = mesh.number_of_cells()
            isMarkedCell = np.zeros(NC+1, dtype=np.bool)
            isMarkedCell[6] = True
            mesh.refine(isMarkedCell, dflag=False)
        
        if True:
            NC = mesh.number_of_cells()
            isMarkedCell = np.zeros(NC+1, dtype=np.bool)
            isMarkedCell[3] = True
            mesh.refine(isMarkedCell, dflag=False)
            
        if True:
            NC = mesh.number_of_cells()
            isMarkedCell = np.zeros(NC+1, dtype=np.bool)
            isMarkedCell[1] = True
            isMarkedCell[5] = True
            mesh.refine(isMarkedCell, dflag=False)
            
        if True:
            NC = mesh.number_of_cells()
            isMarkedCell = np.zeros(NC+1, dtype=np.bool)
            isMarkedCell[1] = True
            isMarkedCell[12] = True
            mesh.refine(isMarkedCell, dflag=False)
            
        if True:
            NC = mesh.number_of_cells()
            isMarkedCell = np.zeros(NC+1, dtype=np.bool)
            isMarkedCell[0] = True
            isMarkedCell[21] = True
            mesh.refine(isMarkedCell, dflag=False)
            
        print("halfedge level:\n")
        for i, val in enumerate(mesh.halfedgedata['level']):
            print(i, ':', val, mesh.ds.halfedge[i, 0:2])
            
        print("cell level:\n")
        for i, val in enumerate(mesh.celldata['level']):
            print(i, ':', val)
        
        if plot:
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            mesh.find_node(axes, showindex=True)
            #mesh.find_edge(axes, showindex=True)
            mesh.find_cell(axes, showindex=True)
            plt.show()

test = HalfEdgePolygonMeshTest()
#test.boundary_edge_to_edge_test()
#test.from_polygonmesh_test()
#test.refine_test()
#test.edge_to_cell_test()
#test.cell_barycenter_test(plot=False)
test.refine_test()
