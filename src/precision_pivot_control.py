import maya.cmds as cmds
import math as m
from functools import wraps

'''
    ----------------------------------------------------------------
    script shows precise world space locations of specified geometry
    and the transform indexes of geometry components i.e vertex 
    indices at specific vertices on the selected mesh, face normals, 
    edge normals etc.
    ----------------------------------------------------------------
'''

def showErrorDecorator(text):
    '''
        creates an error message decorator.
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (RuntimeError, TypeError, ValueError) :
                print( 'Please select: {0} '.format(text))
        return wrapper
    return decorator

def isObjectSelected():
    '''
        detects whether any object exists in scene and is currenly selected.
        If such an object/objects exist in scene, return boolean statement.
    '''
    geometry = cmds.ls(geometry=True)
    if len(geometry)>0:
        selectedObjs = cmds.ls(selection=True)
        if len(selectedObjs)>0:
            return True            
        else:
            return False
    else:
        return False 
        
class controls():            
    
    renameOptions = []
    def __init__(self):
        self._queryText = 'annotation'
    
    @property
    def queryText(self):
        return self._queryText
    
    @queryText.setter
    def rename(self, text):
        self._queryText = text    
                 
    def renameAnnotations(self, widgets):
        controls.queryText = cmds.textField(widgets['naming'], q=True, text=True)
        self.renameText(controls.queryText)
        self.renameOptions.append(controls.queryText)
                 
    def renameText(self, text):
        geometry = cmds.ls(geometry=True)[0]
        for i in cmds.ls(sl=True):
            if i.startswith(geometry):
                print( 'Please select another name, this is already taken by mesh.'   )                 
            else:
                cmds.rename(i, text)

    def findAveragePos(self, componentPositions):
        '''
            finds the average positions of listed components.
        '''      
        xCounter, yCounter, zCounter = 0, 0, 0
        for i in range(len(componentPositions)):
            xCounter += componentPositions[i][0]
            yCounter += componentPositions[i][1]
            zCounter += componentPositions[i][2]
        xCounter /= len(componentPositions)
        yCounter /= len(componentPositions)
        zCounter /= len(componentPositions)
        return xCounter, yCounter, zCounter

    @showErrorDecorator('edge')           
    def findAndAnnotateEdge(self, object, objectName, queryPrecision):
        '''
            find the vertices connecting to an edge and annotates the midpoint edge position
        '''
        edge = cmds.ls(cmds.polyListComponentConversion(object, fe=True, tv=True), fl=True)
        edgeMidpoint = self.findAveragePos([cmds.pointPosition(i) for i in edge])
        rounded = [round(edgeMidpoint[i], queryPrecision) for i in range(3)]                    
        cmds.annotate(objectName, p=edgeMidpoint, text=str(rounded))
        cmds.select(object)
        
    #@showErrorDecorator('face normal')        
    def findAndAnnotateFaceNormal(self, object, objectName, queryPrecision):
        '''
            finds the position of a face normal using adjacent vertex positions and their midpoints.
        '''
        faces = cmds.ls(cmds.polyListComponentConversion(object, ff=True, tv=True), fl=True)
        facePos = self.findAveragePos([cmds.pointPosition(i) for i in faces])
        rounded = [round(float(facePos[i]), queryPrecision) for i in range(3)]
        cmds.annotate(objectName, p=facePos, text=str(rounded))
        cmds.select(object)
        
    @showErrorDecorator('vertex')  
    def vertexControl(self, widgets, *args):
        '''
            controls the vertex position and index display in the viewport
        '''
        queryPrecision = cmds.intSliderGrp(widgets['precision'], q=True, v=True)
        objects = cmds.ls(sl=True)   
        vertexNumber = cmds.polyEvaluate(objects[0], vertex=True)
        objectName = [objects[0] + '.vtx[' + str(i) + ']' for i in range(int(vertexNumber))]
        vertexPositions = [cmds.pointPosition(objectName[i]) for i in range(vertexNumber)]
        rounded = [[round(i[j], queryPrecision) for j in range(3)] for i in vertexPositions]
        for i in range(len(rounded)):
            if args[0] is True: 
                cmds.annotate(objects[0], p=[rounded[i][0], rounded[i][1], rounded[i][2]], text=str(rounded[i]))
                cmds.select(objects[0])
            elif args[1] is True:
                cmds.annotate(objects[0], p=[rounded[i][0], rounded[i][1], rounded[i][2]], text=objectName[i])       
                cmds.select(objects[0])
                
    def fNormalControl(self, widgets):
        '''
            controls the placement and display of faceNormals on the selected polygonal mesh.
        '''
        queryPrecision = cmds.intSliderGrp(widgets['precision'], q=True, v=True)
        objects = cmds.ls(sl=True)
        numFaces = cmds.polyEvaluate(objects[0], f=True)
        allFaceNormals = [objects[0] + '.f[' + str(i) + ']' for i in range(int(numFaces))]
        for i in range(int(numFaces)):
            self.findAndAnnotateFaceNormal(allFaceNormals[i], objects[0], queryPrecision)        
        cmds.select(objects[0], r=True)
        
    def edgeControl(self, widgets):
        '''
            controls the placement and display of edgeNormals on the selected polygonal mesh.
        '''
        queryPrecision = cmds.intSliderGrp(widgets['precision'], q=True, v=True)
        objects = cmds.ls(sl=True)
        numEdges = cmds.polyEvaluate(objects[0], e=True)
        allEdgeNames = [ objects[0] + '.e[' + str(i) + ']' for i in range(int(numEdges))]
        for i in range(int(numEdges)):
            self.findAndAnnotateEdge(allEdgeNames[i], objects[0], queryPrecision)        
        cmds.select(objects[0], r=True)
        
    def geometryControl(self, widgets, *args):
        '''
            controls whenever the user selects a single geometry and wants to 
            find the position with precision
        '''
        queryPrecision = cmds.intSliderGrp(widgets['precision'], q=True, v=True)
        objectSelected = cmds.ls(sl=True)
        objectName = objectSelected[0].split('.')[0]
        if args[0] is True:
            try:
                vtxPosition = cmds.pointPosition(objectSelected[0])
                rounded = [round(vtxPosition[i], queryPrecision) for i in range(3)]
                cmds.annotate((objectSelected[0].split('.'))[0], p=[rounded[0],rounded[1],rounded[2]], text=str(rounded))
                cmds.select(objectSelected[0])
            except RuntimeError:
                print( 'Please select a vertex')
        elif args[1] is True:
            self.findAndAnnotateEdge(objectSelected[0], objectName, queryPrecision)
        elif args[2] is True:
            self.findAndAnnotateFaceNormal(objectSelected[0], objectName, queryPrecision)
        elif args[3] is True:  
            try:
                vtxFacePosition = cmds.polyNormalPerVertex(objectSelected[0], q=True, normalXYZ=True)
                rounded = [round(vtxFacePosition[i], queryPrecision) for i in range(3)]
                cmds.annotate(objectSelected[0].split('.')[0], p=[rounded[0],rounded[1],rounded[2]], text=str(rounded))
                cmds.select(objectSelected[0])
            except RuntimeError:
                print( 'Please select a vertex face')
                
    def callBackDeletion(self, *args):
        '''
            deletes all annotations when function callBack, such as when geometry
            is transformed i.e translated, rotated or scaled in someway.
        '''
        everything = cmds.ls() 
        geometry = cmds.ls(geometry=True)
        try:
            for j in self.renameOptions: cmds.delete(j)
            for i in everything:               
                if i.startswith(self._queryText):
                    cmds.delete(i)   
        except (TypeError, ValueError):
            for i in everything:               
                if i.startswith(self._queryText):
                    cmds.delete(i)
            
class UI(controls):
    
    message = '''
    ----------------------------------------------------------------
    script shows precise world space locations of specified geometry
    and the transform indexes of geometry components i.e vertex 
    indices at specific vertices on the selected mesh, face normals, 
    edge normals etc.
    ----------------------------------------------------------------
    '''
    
    def __str__(self):
        return self.message
        
    def __init__(self, windowName='PPC',widthHeight=(430,170)):
        self.windowName, self.secondWindowName = windowName, windowName
        self.widthHeight = widthHeight
        self.widgets = {}
        self.isVertexAll, self.isVertexIndexAll, self.isEdgeAll, self.isFaceNormalAll = False, False, False, False
        self.isVertex, self.isEdge, self.isFace, self.isVtxFace  = False, False, False, False
    
    def detectAndApplyChanges(self, *args):
        '''
            detects and updates which checkbox is currently selected
        '''
        queryVertexAll = cmds.checkBox(self.widgets['vertexPos'], q=True, v=True)
        queryVertexIndex = cmds.checkBox(self.widgets['vertexIndexNum'], q=True, v=True)
        queryEdgeLength = cmds.checkBox(self.widgets['edgeLength'], q=True, v=True)
        queryFaceNormal = cmds.checkBox(self.widgets['faceNormalPos'], q=True, v=True)
        # query first row of attributes
        queryVtx = cmds.checkBox(self.widgets['vertex'], q=True, v=True)
        queryEdge = cmds.checkBox(self.widgets['edge'], q=True, v=True)
        queryFace = cmds.checkBox(self.widgets['faceNormal'], q=True, v=True)
        queryVtxFace = cmds.checkBox(self.widgets['vertexFace'], q=True, v=True)
        #query second row of attributes
        
        attrList = [self.isVertexAll, self.isVertexIndexAll, self.isEdgeAll, self.isFaceNormalAll,
                    self.isVertex, self.isEdge, self.isFace, self.isVtxFace]
        queryAttrList = [queryVertexAll, queryVertexIndex, queryEdgeLength, queryFaceNormal,
                        queryVtx, queryEdge, queryFace, queryVtxFace]              
        #create list for queried attribute values and detection attribute values
        
        controls().callBackDeletion()
        #delete any annotations existing in scene        
        
        for i in range(len(attrList)):
            if queryAttrList[i] is True:
                attrList[i] = True
                if i>3 and i<8:   
                    controls().geometryControl(self.widgets, attrList[4], attrList[5], 
                                                attrList[6], attrList[7])
                elif i>-1 and i<2:
                    controls().vertexControl(self.widgets, attrList[0], attrList[1])
                elif i==3:
                    controls().fNormalControl(self.widgets)
                elif i==2:
                    controls().edgeControl(self.widgets)
        #set detection values True based on user specification
        
    def callBackFunc(self):
        try:
            cmds.deleteUI(self.mainWindow)
            self.secondWindow = cmds.window(title=self.secondWindowName, widthHeight = self.widthHeight,
                                        resizeToFitChildren=True)
            self.deleteActiveWindows(self.secondWindowName)
            cmds.scriptJob(uiDeleted=[self.secondWindow,self.killAllCommands])
            
            cmds.frameLayout('Display Options')
            cmds.rowColumnLayout(numberOfColumns=2)
            cmds.text('Attributes', w=100)
            self.widgets['naming'] = cmds.textField(w=200, text='Rename annotations.', 
                                                    enterCommand= lambda *args: controls().renameAnnotations(self.widgets), aie=True)
            
            cmds.setParent('..')
            cmds.setParent('..')
            
            cmds.rowColumnLayout(numberOfColumns=4)
            self.widgets['vertexPos'] = cmds.checkBox('Vertex Positions', w=120, onCommand = self.detectAndApplyChanges, 
                                                    offCommand = self.detectAndApplyChanges)
            self.widgets['vertexIndexNum'] = cmds.checkBox('Vertex Index', w=120, onCommand = self.detectAndApplyChanges, 
                                                    offCommand = self.detectAndApplyChanges)
            self.widgets['edgeLength'] = cmds.checkBox('Edge Normals', w=120, onCommand = self.detectAndApplyChanges, 
                                                    offCommand = self.detectAndApplyChanges)
            self.widgets['faceNormalPos'] = cmds.checkBox('Face Normals', w=130, onCommand = self.detectAndApplyChanges, 
                                                    offCommand = self.detectAndApplyChanges)
            
            cmds.setParent('..')
            
            cmds.rowColumnLayout(numberOfColumns=4)
            self.widgets['vertex'] = cmds.checkBox('Vertex', w=120, onCommand = self.detectAndApplyChanges, 
                                                    offCommand = self.detectAndApplyChanges)
            self.widgets['edge'] = cmds.checkBox('Edge Normal', w=120, onCommand = self.detectAndApplyChanges, 
                                                    offCommand = self.detectAndApplyChanges)
            self.widgets['faceNormal'] = cmds.checkBox('Face Normal', w=120, onCommand = self.detectAndApplyChanges, 
                                                    offCommand = self.detectAndApplyChanges)
            self.widgets['vertexFace'] = cmds.checkBox('Vertex Face Normal', w=130, onCommand = self.detectAndApplyChanges, 
                                                    offCommand = self.detectAndApplyChanges)
            
            cmds.setParent('..')
            
            cmds.rowColumnLayout(numberOfColumns=2)
            self.widgets['precision'] = cmds.intSliderGrp(label='Precision', field=True, minValue=1, maxValue=5, v=2)
            
            cmds.setParent('..')
            
            cmds.rowColumnLayout(numberOfColumns=3)
            reloadButton = cmds.button('Reload', w=163, command=self.detectAndApplyChanges)
            deleteAllButton = cmds.button('Delete', w=163, command=controls().callBackDeletion)
            undoButton = cmds.button('Undo', w=164, command=self.undoProc)
            
            cmds.showWindow(self.secondWindow)            
        except RuntimeError:
            pass
            
    def callBackEnded(self):
        try:
            cmds.deleteUI(self.secondWindow)
            self.mainWindow = cmds.window(title=self.windowName, widthHeight = self.widthHeight,
                                            resizeToFitChildren=True)
            self.deleteActiveWindows(self.windowName)
            
            cmds.rowColumnLayout()
            cmds.text('Please create and select polygon object to begin')
            
            cmds.showWindow(self.mainWindow)

        except RuntimeError:
            pass
            
    def cancelProc(self, windowID):
        cmds.deleteUI(windowID)
    
    def killAllCommands(self):
        '''
            kills all jobs related to the program when the application is quit
        '''       
        allJobs = cmds.scriptJob(listJobs=True)
        for i in allJobs:
            jobNumber = int(i.split(':')[0])
            job = i.split(':')[1].strip()
            if job.startswith('ct') or job.startswith('cf'):
                cmds.scriptJob(kill=jobNumber)
        print( 'killed Jobs')
        
        cmds.scriptJob(ct=['SomethingSelected',self.callBackFunc])
        cmds.scriptJob(cf=['SomethingSelected',self.callBackEnded])
        
    def undoProc(self, *args):
        cmds.undo()
    
    def deleteActiveWindows(self, windowName):
        if cmds.window(windowName, exists=True):
            cmds.deleteUI(windowName)    
        
    def createUI(self):
        if isObjectSelected():
            self.mainWindow = cmds.window(title=self.windowName, widthHeight = self.widthHeight,
                                                resizeToFitChildren=True)
            self.callBackFunc()
        else:
            self.mainWindow = cmds.window(title=self.windowName, widthHeight = self.widthHeight,
                                                resizeToFitChildren=True)
            self.deleteActiveWindows(self.windowName)
            
            cmds.rowColumnLayout()
            cmds.text('Please create and select polygon object to begin')
           
            cmds.scriptJob(ct=['SomethingSelected',self.callBackFunc])
            cmds.scriptJob(cf=['SomethingSelected',self.callBackEnded])
            cmds.scriptJob(uiDeleted=[self.mainWindow,self.killAllCommands])        
            
            cmds.showWindow(self.mainWindow)
        
if __name__=='__main__':
    userInterface = UI()
    print(userInterface)
    userInterface.createUI()