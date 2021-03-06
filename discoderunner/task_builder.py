from xml.dom.minidom import getDOMImplementation
from os.path import isdir
from os import makedirs


class TaskBuilder:
    def __init__(self, fileName=''):
        self.fileName = fileName
        self.defaultTaskDir = 'data/test_tasks'
        self.taskBody = ''
        self.document = None
        if not isdir(self.defaultTaskDir):
            makedirs(self.defaultTaskDir)

    def writeToFile(self, string):
        with open(self.fileName, 'w') as file:
            file.write(string)

    def save(self):
        if self.fileName == '':
            fileName = 'data/test_tasks/test_task.xml'
        else:
            fileName = self.fileName
        with open(fileName, 'w') as file:
            file.write(self.getTaskBody())

    def createTemplate(self):
        self.document = self.createEmptyDocument()
        topLevelElement = self.getTopLevelElement()
        subtasksElement = self.addSubtasksElement(topLevelElement)
        self.addDataStreams(topLevelElement)
        self.addMainSubtask(subtasksElement)

    def getTopLevelElement(self):
        topLevelElement = self.document.documentElement
        return topLevelElement

    def createEmptyDocument(self):
        DOMimpl = getDOMImplementation()
        document = DOMimpl.createDocument(None, 'Task', None)
        return document

    def addDataStreams(self, topLevelElement):
        datastreamsElement = self.document.createElement('DataStreams')
        topLevelElement.appendChild(datastreamsElement)

    def addMainSubtask(self, subtasksElement):
        mainSubtaskElement = self.document.createElement('Subtask')
        mainSubtaskElement.setAttribute('name', 'Main')
        subtasksElement.appendChild(mainSubtaskElement)

    def addSubtasksElement(self, topLevelElement):
        subtasksElement = self.document.createElement('Subtasks')
        topLevelElement.appendChild(subtasksElement)
        return subtasksElement

    def addExecutor(self, name, period=1):
        executor = self.document.createElement('Executor')
        executor.setAttribute('name', name)
        executor.setAttribute('period', str(period))
        mainSubtask = self.document.getElementsByTagName('Subtask').item(0)
        mainSubtask.appendChild(executor)

    def addDefaultExecutor(self):
        self.addExecutor('Processing', 1)

    def getTaskBody(self):
        if self.document is not None:
            self.taskBody = self.document.firstChild.toprettyxml()
        return self.taskBody

    def addComponent(self, name, componentType, priority=1, bump=0):
        component = self.document.createElement('Component')
        component.setAttribute('name', name)
        component.setAttribute('type', componentType)
        component.setAttribute('priority', str(priority))
        component.setAttribute('bump', str(bump))
        executor = self.document.getElementsByTagName('Executor').item(0)
        executor.appendChild(component)

    def addComponentToExecutor(self, executorName, componentName, componentType):
        component = self.document.createElement('Component')
        component.setAttribute('name', componentName)
        component.setAttribute('type', componentType)
        component.setAttribute('priority', '1')
        component.setAttribute('bump', '0')
        executors = self.document.getElementsByTagName('Executor')
        for executor in executors:
            if executor.getAttribute('name') is executorName:
                executor.appendChild(component)

    def addParamToComponent(self, componentName, paramName, paramValue):
        components = self.document.getElementsByTagName('Component')
        for component in components:
            if component.getAttribute('name') == componentName:
                param = self.document.createElement('param')
                param.setAttribute('name', paramName)
                text = self.document.createTextNode(paramValue)
                param.appendChild(text)
                component.appendChild(param)

    def addDataStream(self, sourceName, sinkName):
        datastream = self.document.createElement('Source')
        datastream.setAttribute('name', sourceName)
        sink = self.document.createElement('sink')
        sinkValue = self.document.createTextNode(sinkName)
        sink.appendChild(sinkValue)
        datastream.appendChild(sink)
        datastreams = self.document.getElementsByTagName('DataStreams').item(0)
        datastreams.appendChild(datastream)

    def updateSource(self, componentName, newSourceName):
        sources = self.document.getElementsByTagName('Source')
        for source in sources:
            if componentName in source.getAttribute('name'):
                source.setAttribute('name', componentName + '.' + newSourceName)

    def hasSource(self, sourceName):
        sources = self.document.getElementsByTagName('Source')
        for source in sources:
            if source.getAttribute('name') == sourceName:
                return True
        return False

    def updateSink(self, componentName, newComponentName, newSinkName):
        sinks = self.document.getElementsByTagName('sink')
        for sink in sinks:
            if componentName in sink.firstChild.data:
                sink.firstChild.data = newComponentName + '.' + newSinkName
