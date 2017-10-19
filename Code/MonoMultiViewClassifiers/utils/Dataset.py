from scipy import sparse
import numpy as np
import logging
import os
import sys
import select
from ..Multiview import GetMultiviewDb as DB


def getV(DATASET, viewIndex, usedIndices=None):
    if usedIndices is None:
        usedIndices = range(DATASET.get("Metadata").attrs["datasetLength"])
    if type(usedIndices) is int:
        return DATASET.get("View" + str(viewIndex))[usedIndices, :]
    else:
        usedIndices = np.array(usedIndices)
        sortedIndices = np.argsort(usedIndices)
        usedIndices = usedIndices[sortedIndices]

        if not DATASET.get("View" + str(viewIndex)).attrs["sparse"]:
            return DATASET.get("View" + str(viewIndex))[usedIndices, :][np.argsort(sortedIndices), :]
        else:
            sparse_mat = sparse.csr_matrix((DATASET.get("View" + str(viewIndex)).get("data").value,
                                            DATASET.get("View" + str(viewIndex)).get("indices").value,
                                            DATASET.get("View" + str(viewIndex)).get("indptr").value),
                                           shape=DATASET.get("View" + str(viewIndex)).attrs["shape"])[usedIndices, :][
                         np.argsort(sortedIndices), :]

            return sparse_mat


def getShape(DATASET, viewIndex):
    if not DATASET.get("View" + str(viewIndex)).attrs["sparse"]:
        return DATASET.get("View" + str(viewIndex)).shape
    else:
        return DATASET.get("View" + str(viewIndex)).attrs["shape"]


def getValue(DATASET):
    if not DATASET.attrs["sparse"]:
        return DATASET.value
    else:
        sparse_mat = sparse.csr_matrix((DATASET.get("data").value,
                                        DATASET.get("indices").value,
                                        DATASET.get("indptr").value),
                                       shape=DATASET.attrs["shape"])
        return sparse_mat


def extractSubset(matrix, usedIndices):
    if sparse.issparse(matrix):
        newIndptr = np.zeros(len(usedIndices) + 1, dtype=int)
        oldindptr = matrix.indptr
        for exampleIndexIndex, exampleIndex in enumerate(usedIndices):
            newIndptr[exampleIndexIndex + 1] = newIndptr[exampleIndexIndex] + (
                oldindptr[exampleIndex + 1] - oldindptr[exampleIndex])
        newData = np.ones(newIndptr[-1], dtype=bool)
        newIndices = np.zeros(newIndptr[-1], dtype=int)
        oldIndices = matrix.indices
        for exampleIndexIndex, exampleIndex in enumerate(usedIndices):
            newIndices[newIndptr[exampleIndexIndex]:newIndptr[exampleIndexIndex + 1]] = oldIndices[
                                                                                        oldindptr[exampleIndex]:
                                                                                        oldindptr[exampleIndex + 1]]
        return sparse.csr_matrix((newData, newIndices, newIndptr), shape=(len(usedIndices), matrix.shape[1]))
    else:
        return matrix[usedIndices]


def initMultipleDatasets(args, nbCores):
    """Used to create copies of the dataset if multicore computation is used
    Needs arg.pathF and arg.name"""
    if nbCores > 1:
        if DB.datasetsAlreadyExist(args.pathF, args.name, nbCores):
            logging.debug("Info:\t Enough copies of the dataset are already available")
            pass
        else:
            logging.debug("Start:\t Creating " + str(nbCores) + " temporary datasets for multiprocessing")
            logging.warning(" WARNING : /!\ This may use a lot of HDD storage space : " +
                            str(os.path.getsize(args.pathF + args.name + ".hdf5") * nbCores / float(
                                1024) / 1000 / 1000) + " Gbytes /!\ ")
            confirmation = confirm()
            if not confirmation:
                sys.exit(0)
            else:
                datasetFiles = DB.copyHDF5(args.pathF, args.name, nbCores)
                logging.debug("Start:\t Creating datasets for multiprocessing")
                return datasetFiles


def confirm(resp=True, timeout=15):
    ans = input_(timeout)
    if not ans:
        return resp
    if ans not in ['y', 'Y', 'n', 'N']:
        print 'please enter y or n.'
    if ans == 'y' or ans == 'Y':
        return True
    if ans == 'n' or ans == 'N':
        return False


def input_(timeout=15):
    print "You have " + str(timeout) + " seconds to stop the script by typing n"
    i, o, e = select.select([sys.stdin], [], [], timeout)
    if i:
        return sys.stdin.readline().strip()
    else:
        return "y"
