from floppy.node import Node, Input, Output, Tag, abstractNode
import os, ntpath

@abstractNode
class FileNode(Node):
    Tag('FileOperations')

class FileWriter(FileNode):
    """
    Creates a new node for file operations.
    :param nodeClass: subclass object of 'Node'.
    :return: newly created Node instance.
    """
    Input('FileName', str)
    Input('Overwrite', bool, select=(True, False))
    Input('LineMode', bool, select=(True, False)) # if true, append a new line
    Input('Content', str)
    Output('Trigger', object)

    def run(self):
        super(FileWriter, self).run()

        # determine file writing conditions
        if(self._Overwrite):
            writeFlag = 'w'
        else:
            writeFlag = 'a'
        # write to file
        with open(self._FileName, writeFlag) as file:
            # some funny results are produced if the os.lineseep is added via += operator
            if(self._LineMode):
                file.write(self._Content + os.linesep)
            else:
                file.write(self._Content)


class DeleteFile(FileNode):
    """
    Deletes a file if it exists.
    :param nodeClass: subclass object of 'Node'.
    :return: newly created Node instance.
    """
    Input('FileName', str)
    Output('Trigger', object)

    def run(self):
        super(DeleteFile, self).run()

        if ntpath.exists(self._FileName):
            os.remove(self._FileName)

class FileNameFromPath(FileNode):
    """
    Extracts the file name from a path.
    :param nodeClass: subclass object of 'Node'.
    :return: newly created Node instance.
    """
    Input('PathAndFile', str)
    Output('Path', str)
    Output('FileName', str)
    Output('Extension', str)

    def run(self):
        super(FileNameFromPath, self).run()

        self._Path(ntpath.dirname(self._PathAndFile))
        self._FileName(ntpath.basename(self._PathAndFile))
        self._Extension(ntpath.splitext(self._PathAndFile))


class JoinPath(FileNode):
    """
    Joins to strings which represent a path and a path or file.
    :param nodeClass: subclass object of 'Node'.
    :return: newly created Node instance.
    """
    Input("Path", str)
    Input("PathOrFileName", str)
    Output("JoinedPath", str)

    def run(self):
        super(JoinPath, self).run()

        self._JoinedPath(os.path.join(self._Path, self._PathOrFileName))