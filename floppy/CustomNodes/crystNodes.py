# import lauescript
# from lauescript.laueio import loader
# from lauescript.cryst.iterators import iter_atom_pairs
from lauescript.cryst.transformations import frac2cart
from lauescript.types.adp import ADPDataError
from floppy.node import Node, abstractNode, Input, Output, Tag, ForLoop
from floppy.FloppyTypes import Atom, Structure, Number, LongAtom
from floppy.CustomObjects.CrystalObjects import StructureModel
from floppy.CustomObjects import toolbox
from decimal import *
import subprocess
import os, glob

@abstractNode
class CrystNode(Node):
    Tag('Crystallography')


class ReadAtoms(CrystNode):
    """
    lauescript based
    """
    Tag("lauescript")
    Input('FileName', str)
    Output('Atoms', Atom, list=True)

    def run(self):
        super(ReadAtoms, self).run()
        from lauescript.laueio.loader import Loader
        loader = Loader()
        loader.create(self._FileName)
        print('1')
        mol = loader.load('quickloadedMolecule')
        print('2')
        self._Atoms(mol.atoms)


class ReadStructure(CrystNode):
    """
    Reads in a cif file and turns it into a StructureModel object.
    If '*.cif' is given, the first cif file in the folder is taken.
    """
    Input('FileName', str)
    Output('Model', Structure)
    Output('Atoms', LongAtom, list=True)

    def run(self):
        super(ReadStructure, self).run()
        structure = StructureModel()
        if "*.cif" in self._FileName.lower():
            fileName = glob.glob(self._FileName)[0] # takes the frist cif file
        else:
            fileName = self._FileName
        structure.parse_cif(fileName)
        self._Model(structure)
        self._Atoms(structure.atoms)


class BreakStructure(CrystNode):
    """
    Reads out the parameters of a StructureModel object.
    """
    Input('Model', Structure)
    Output('Name', str)
    Output('CrystalSystem', str)
    Output('SGnumber', int)
    Output('SG', str)
    Output('Cell', Number, list=True)
    Output('CellErrors', Number, list=True)
    Output('Wavelength', Number, list=True)
    Output('Refinement', Number, list=True)
    Output('FreeVariables', Number, list=True)


    def run(self):
        super(BreakStructure, self).run()
        # handing output to pins
        self._Name(self._Model.name)
        self._CrystalSystem(self._Model.crystalSystem)
        self._SGnumber(self._Model.sgNumber)
        self._SG(self._Model.sg)
        self._Cell(self._Model.cell)
        self._CellErrors(self._Model.cellErrors)
        self._Wavelength(self._Model.wavelength)
        self._Refinement(self._Model.refinementIndicators)
        self._FreeVariables(self._Model.freeVariables)


class BreakAtom(CrystNode):
    """
    lauescript based
    """
    Tag("lauescript")
    Input('Atom', Atom)
    Output('Name', str)
    Output('Element', str)
    Output('frac', float, list=True)
    Output('cart', float, list=True)
    Output('ADP',float, list=True)
    Output('ADP_Flag', str)
    Output('Cell',float, list=True)

    def run(self):
        super(BreakAtom, self).run()
        atom = self._Atom
        # print(atom, atom.molecule.get_cell(degree=True))
        self._Name(atom.get_name())
        self._Element(atom.get_element())
        self._frac(atom.get_frac())
        self._cart(atom.get_cart())
        try:
            adp = atom.adp['cart_meas']
        except ADPDataError:
            adp = [0, 0, 0, 0, 0, 0]
        self._ADP(adp)
        self._ADP_Flag(atom.adp['flag'])
        self._Cell(atom.molecule.get_cell(degree=True))

    # def check(self):
    #     for inp in self.inputs.values():
    #         print(inp.value)
    #     return super(BreakAtom, self).check()


class BreakLongAtom(CrystNode):
    """
    Reads out the data of an atom with extended data for sigmas.
    """
    Input("Atom", LongAtom)
    Output("AtomName", str)
    Output("Type", str)
    Output("SoF", Number)
    Output("SoFError", Number)
    Output("PositionFract", Number, list=True)
    Output("PositionFractError", Number, list=True)
    Output("Uiso", Number)
    Output("UisoError", Number)
    Output("IsAnisotropic", bool)
    Output("ADP", Number, list=True)
    Output("ADPError", Number, list=True)

    def run(self):
        super(BreakLongAtom, self).run()
        self._AtomName(self._Atom.name)
        self._Type(self._Atom.type)
        self._SoF(self._Atom.sof)
        self._SoFError(self._Atom.sofError)
        self._PositionFract(self._Atom.positionFract)
        self._PositionFractError(self._Atom.positionFractError)
        self._Uiso(self._Atom.uiso)
        self._UisoError(self._Atom.uisoError)
        self._IsAnisotropic(self._Atom.isAnisotropic)
        self._ADP(self._Atom.adp)
        self._ADPError(self._Atom.adpError)


class Frac2Cart(CrystNode):
    """
    lauescript based
    """
    Tag("lauescript")
    Input('Position', float, list=True)
    Input('Cell', float, list=True)
    Output('Cart', float, list=True)

    def run(self):
        super(Frac2Cart, self).run()
        self._Cart(frac2cart(self._Position, self._Cell))


class SelectAtom(CrystNode):
    """
    lauescript based
    """
    Tag("lauescript")
    Input('AtomList', Atom, list=True)
    Input('AtomName', str)
    Output('Atom', Atom)

    def run(self):
        super(SelectAtom, self).run()
        name = self._AtomName
        self._Atom([atom for atom in self._AtomList if atom.get_name() == name][0])


class SelectLongAtom(CrystNode):
    """
    Choose an atom by its name.
    """
    Input('AtomList', LongAtom, list=True)
    Input('AtomName', str)
    Output('Atom', LongAtom)

    def run(self):
        super(SelectLongAtom, self).run()
        selectedAtom = None
        for atom in self._AtomList:
            if atom.name == self._AtomName:
                selectedAtom = atom
        self._Atom(selectedAtom)


# maybe do this with a global lookup table
ALLCELLPARAMETERS = ['a', 'b', 'c', 'alpha', 'beta', 'gamma'] # there is probably a more elegant and global way for this
class SelectCellParameter(CrystNode):
    """
    Lets the user choose a cell parameter from a list.
    :param nodeClass: subclass object of 'Node'.
    :return: newly created Node instance.
    """
    Input('Cell', Number, list=True)
    Input('CellParameter', str, select=ALLCELLPARAMETERS, default='a')
    Output('ParameterValue', Number)

    def run(self):
        super(SelectCellParameter, self).run()
        try:
            self._ParameterValue(self._Cell[ALLCELLPARAMETERS.index(self._CellParameter)])
        except IndexError:
            self._ParameterValue(-1)


# maybe do this with a global lookup table
ALLADPPARAMETERS = ['11', '22', '33', '23', '13', '12'] # there is probably a more elegant and global way for this
class SelectAdpParameter(CrystNode):
    """
    Lets the user choose a cell parameter from a list.
    :param nodeClass: subclass object of 'Node'.
    :return: newly created Node instance.
    """
    Input('ADP', Number, list=True)
    Input('ADPParameter', str, select=ALLADPPARAMETERS, default='11')
    Output('ParameterValue', Number)

    def run(self):
        super(SelectAdpParameter, self).run()
        try:
            self._ParameterValue(self._ADP[ALLADPPARAMETERS.index(self._ADPParameter)])
        except IndexError:
            self._ParameterValue(self._ADP[0]) # Isotropic


class IsHydrogen(CrystNode):
    """
    Tests an atom whether it is an hydrogen atom or not.
    """
    Input("Atom", LongAtom)
    Output("IsHydrogen", bool)
    Output("IsOtherElement", bool)

    def run(self):
        super(IsHydrogen, self).run()
        switch = self._Atom.type == "H"
        self._IsHydrogen(switch)
        self._IsOtherElement(not switch)


class RemoveHydrogen(CrystNode):
    """
    Removes all hydrogen atoms from a list.
    """
    Input("Atoms", LongAtom, list=True)
    Output("ClearedAtoms", LongAtom, list=True)

    def run(self):
        super(RemoveHydrogen, self).run()
        newAtomList = []
        for atom in self._Atoms:
            if atom.type != "H":
                newAtomList.append(atom)
        self._ClearedAtoms(newAtomList)


class SortAtoms(CrystNode):
    """
    Removes all hydrogen atoms from a list.
    """
    Input("Atoms", LongAtom, list=True)
    Output("SortedAtoms", LongAtom, list=True)

    def run(self):
        super(SortAtoms, self).run()
        sortAtoms = sorted(self._Atoms, key=toolbox.atom_name_sort)
        self._SortedAtoms(sortAtoms)


class PDB2INS(CrystNode):
    """
    lauescript based
    """
    Tag("lauescript")
    Input('FileName', str)
    Input('Wavelength', float)
    Input('HKLF', int)
    Input('CELL', str)
    Input('SpaceGroup', str)
    Input('ANIS', bool)
    Input('MakeHKL', bool)
    Input('REDO', bool)
    Input('Z', int)
    Output('INS', str)
    Output('HKL', str)
    Output('PDB', str)

    def __init__(self, *args, **kwargs):
        super(PDB2INS, self).__init__(*args, **kwargs)
        self.stdout = ''

    def check(self):
        x = self.inputs['FileName'].isAvailable()
        return x

    def run(self):
        super(PDB2INS, self).run()
        opt =  ('pdb2ins',
                self._FileName,
                '-i',
                '-o __pdb2ins__.ins',
                ' -w '+str(self._Wavelength) if self._Wavelength else '',
                ' -h '+str(self._HKLF) if self._HKLF else '',
                ' -c '+str(self._CELL) if self._CELL else '',
                ' -s '+str(self._SpaceGroup) if self._SpaceGroup else '',
                ' -a ' if self._ANIS else '-a',
                ' -b ' if self._MakeHKL else '-b',
                ' -r ' if self._REDO else '',
                ' -z ' + str(self._Z) if self._Z else '',
                (' -d '+ self._FileName+'.sf') if not '@' in self._FileName else '')
        opt = ' '.join(opt)
        print(opt)
        # opt = [o for o in ' '.join(opt).split(' ') if o]
        # print(opt)
        self.p = subprocess.Popen(opt, shell=True, stdout=subprocess.PIPE)
        self.stdout = ''
        while True:
            line = self.p.stdout.readline()
            if not line:
                break
            self.stdout += str(line)[1:]
        # print('ran')
        self._INS(open('__pdb2ins__.ins', 'r').read())
        try:
            self._HKL(open('__pdb2ins__.hkl', 'r').read())
        except IOError:
            try:
                self._HKL(open('{}.hkl'.format(self._FileName), 'r').read())
            except IOError:
                self._HKL('')
        try:
            self._PDB(open('__pdb2ins__.pdb', 'r').read())
        except IOError:
            self._PDB(open('{}.pdb'.format(self._FileName), 'r').read())
        for file in os.listdir():
            if file.startswith('__pdb2ins__'):
                os.remove(file)

    def report(self):
        r = super(PDB2INS, self).report()
        r['stdout'] = self.stdout
        r['template'] = 'ProgramTemplate'
        return r


class BreakPDB(CrystNode):
    """
    lauescript based
    """
    Tag("lauescript")
    Input('PDB', str)
    Output('Code', str)
    Output('R1', float)

    def run(self):
        for line in self._PDB.splitlines():
            if line.startswith('REMARK   3   R VALUE') and '(WORKING SET)' in line:
                line = [i for i in line[:-1].split() if i]
                r1 = line[-1]
            elif line.startswith('HEADER'):
                line = [i for i in line[:-1].split() if i]
                code = line[-1]
        self._Code(code)
        self._R1(r1)


class ForEachAtomPair(ForLoop):
    """
    lauescript based
    """
    Tag("lauescript")
    Input('Start', Atom, list=True)
    Output('Atom1', Atom)
    Output('Atom2', Atom)

    # def __init__(self, *args, **kwargs):
    #     super(ForEachAtomPair, self).__init__(*args, **kwargs)

    def run(self):
        atoms = self._Start
        if self.fresh:
            self.x = 0
            self.y = 1
            self.end = len(atoms)-1
        self.fresh = False
        self._Atom1(atoms[self.x])
        self._Atom2(atoms[self.y])
        self.y += 1
        if self.y >= self.end:
            self.x += 1
            self.y = self.x+1
        if self.x >= self.end:
            self._Final(self._Start)
            self.done = True
