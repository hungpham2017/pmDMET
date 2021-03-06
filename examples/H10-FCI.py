'''
Multipurpose Density Matrix Embedding theory (mp-DMET)
Copyright (C) 2015 Hung Q. Pham
Author: Hung Q. Pham, Unviversity of Minnesota
email: phamx494@umn.edu
'''

import sys
import pyscf
from pyscf import gto, scf, dft, ao2mo, mcscf
import numpy as np
sys.path.append('/panfs/roc/groups/6/gagliard/phamx494/mpdmet')
from mdmet import orthobasis, schmidtbasis, qcsolvers, dmet
from functools import reduce
import scipy as scipy
sys.path.append('/panfs/roc/groups/6/gagliard/phamx494/QC-DMET/src')
import localintegrals, qcdmet_paths
import dmet as qc_dmet
sys.path.append('./lib/build')
import libdmet
import time

def test_makemole(bond):
	bondlength = bond
	nat = 10
	mol = gto.Mole()
	mol.atom = []
	r = 0.5 * bondlength / np.sin(np.pi/nat)
	for i in range(nat):
		theta = i * (2*np.pi/nat)
		mol.atom.append(('H', (r*np.cos(theta), r*np.sin(theta), 0)))

	mol.basis = 'sto-6g'
	mol.build(verbose=0)

	mf = scf.RHF(mol)
	mf.scf()

	atoms_per_imp = 2 # Impurity size = 1 atom
	Norbs = mol.nao_nr()
	assert ( nat % atoms_per_imp == 0 )
	orbs_per_imp = int(Norbs * atoms_per_imp // nat)

	impClusters = []
	for cluster in range(nat // atoms_per_imp):
		impurities = np.zeros([Norbs], dtype=int)
		for orb in range( orbs_per_imp ):
			impurities[orbs_per_imp*cluster + orb] = 1
		impClusters.append(impurities)

	return mol, mf, impClusters 

def test_makemole2():
	bondlength = 1.0
	mol = gto.M(atom='He 0 0.5 0; He -0.5 0 0; Be 1 0 0; Be 2 0 0; He 3 0.5 0; He 3 -0.5 0', basis='sto-6g')
	mol.build(verbose=0)
	mf = scf.RHF(mol)
	mf.scf()
	
	unit_sizes = np.array([ 2, 5, 5, 2])
	impClusters = []
	for frag in range(4):
		impurity_orbitals = np.zeros( [mol.nao_nr()], dtype = int)
		start = unit_sizes[:frag].sum()
		impurity_orbitals[start:(start + unit_sizes[frag])] = 1
		impClusters.append(impurity_orbitals)	
	return mol, mf, impClusters 

for bond in np.arange(0.8, 2.0, 0.2): 
	mol, mf, impClusters  = test_makemole(bond)
	mc = mcscf.CASCI(mf, 10, 10)
	EFCI = mc.kernel()[0]
	print('Total energy + Time:', EFCI)
	